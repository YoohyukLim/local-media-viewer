import os
import queue
import threading
import time
from typing import Dict, Optional, Tuple
from concurrent.futures import ProcessPoolExecutor, Future
from .thumbnail import create_thumbnail
from ..config import Settings
from ..logger import LogManager
from multiprocessing import get_context
import signal
from functools import partial

def _init_worker():
    """워커 프로세스 초기화 함수"""
    # 워커 프로세스에서 KeyboardInterrupt 무시
    signal.signal(signal.SIGINT, signal.SIG_IGN)

class ThumbnailWorker:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.task_queue = queue.Queue()
        self.results: Dict[str, bool] = {}
        self.worker_thread: Optional[threading.Thread] = None
        self.result_thread: Optional[threading.Thread] = None
        self.should_stop = threading.Event()  # Event 객체로 변경
        self._executor: Optional[ProcessPoolExecutor] = None
        self._futures: Dict[str, Tuple[Future, str]] = {}
        self._lock = threading.Lock()
        self.logger = LogManager.get_instance().logger
    
    def start(self):
        """작업자 스레드를 시작합니다."""
        if self.worker_thread is None:
            self.should_stop.clear()
            self._executor = ProcessPoolExecutor(
                max_workers=self.settings.THUMBNAIL_MAX_WORKERS,
                mp_context=get_context('spawn'),
                initializer=_init_worker  # 워커 프로세스 초기화 함수 설정
            )
            self.worker_thread = threading.Thread(target=self._process_queue)
            self.result_thread = threading.Thread(target=self._process_results)
            self.worker_thread.daemon = True
            self.result_thread.daemon = True
            self.worker_thread.start()
            self.result_thread.start()
            self.logger.info("Thumbnail worker started")
    
    def stop(self):
        """작업자 스레드를 중지합니다."""
        if self.should_stop.is_set():
            return  # 이미 종료 중이면 리턴
            
        self.logger.info("Stopping thumbnail worker...")
        self.should_stop.set()
        
        # 1. 진행 중인 작업 취소
        try:
            with self._lock:
                for future, _ in self._futures.values():
                    if future.done():
                        continue
                    future.cancel()
                self._futures.clear()
        except Exception as e:
            self.logger.error(f"Error canceling futures: {str(e)}")
        
        # 2. 스레드 종료 대기
        threads = []
        if self.worker_thread and self.worker_thread.is_alive():
            threads.append(self.worker_thread)
        if self.result_thread and self.result_thread.is_alive():
            threads.append(self.result_thread)
            
        for thread in threads:
            try:
                thread.join(timeout=0.5)
            except Exception as e:
                self.logger.error(f"Error joining thread: {str(e)}")
        
        # 3. 프로세스 풀 종료
        if self._executor is not None:
            try:
                self._executor.shutdown(wait=False, cancel_futures=True)
            except Exception as e:
                self.logger.error(f"Error shutting down executor: {str(e)}")
            finally:
                self._executor = None
        
        self.worker_thread = None
        self.result_thread = None
        self.logger.info("Thumbnail worker stopped")
    
    def add_task(self, thumbnail_id: str, video_path: str) -> None:
        """썸네일 생성 작업을 큐에 추가합니다."""
        thumbnail_path = self.settings.get_thumbnail_path(thumbnail_id)
        
        # 썸네일이 이미 존재하고 최신인 경우 스킵
        if os.path.exists(thumbnail_path):
            try:
                # 비디오 파일과 썸네일 파일의 수정 시간 비교
                video_mtime = os.path.getmtime(video_path)
                thumb_mtime = os.path.getmtime(thumbnail_path)
                
                if video_mtime <= thumb_mtime:
                    self.logger.info(f"Skipping thumbnail creation for: {video_path} (already exists)")
                    return
                    
                self.logger.info(f"Updating outdated thumbnail for: {video_path}")
            except Exception as e:
                self.logger.error(f"Error checking thumbnail status: {str(e)}")
                # 에러 발생 시 안전하게 썸네일 재생성
        
        # 썸네일이 없거나 업데이트가 필요한 경우
        self.task_queue.put((thumbnail_id, video_path, thumbnail_path))
        self.logger.info(f"Added thumbnail task for: {video_path}")
    
    def get_result(self, thumbnail_id: str) -> Optional[bool]:
        """특정 썸네일의 생성 결과를 반환합니다."""
        with self._lock:
            return self.results.get(thumbnail_id)
    
    def _process_queue(self):
        """큐의 작업을 처리합니다."""
        while not self.should_stop.is_set():
            try:
                try:
                    thumbnail_id, video_path, thumbnail_path = self.task_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                if self._executor is None or self.should_stop.is_set():
                    break
                    
                self.logger.info(f"Processing thumbnail for: {video_path}")
                future = self._executor.submit(
                    create_thumbnail,
                    video_path,
                    thumbnail_path,
                    self.settings
                )
                
                with self._lock:
                    self._futures[thumbnail_id] = (future, video_path)
                
                self.task_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error in queue processing: {str(e)}")
                continue
    
    def _process_results(self):
        """완료된 썸네일 생성 작업의 결과를 처리합니다."""
        while not self.should_stop.is_set():
            try:
                with self._lock:
                    done_futures = []
                    for thumbnail_id, (future, video_path) in self._futures.items():
                        if future.done():
                            try:
                                success = future.result(timeout=0)
                                self.results[thumbnail_id] = success
                                if success:
                                    self.logger.info(f"Successfully created thumbnail for: {video_path}")
                                else:
                                    self.logger.error(f"Failed to create thumbnail for: {video_path}")
                                done_futures.append(thumbnail_id)
                            except KeyboardInterrupt:
                                # 인터럽트 발생 시 썸네일 파일 정리
                                try:
                                    thumbnail_path = self.settings.get_thumbnail_path(thumbnail_id)
                                    tmp_path = f"{thumbnail_path}.tmp"
                                    if os.path.exists(tmp_path):
                                        os.remove(tmp_path)
                                except Exception:
                                    pass
                                done_futures.append(thumbnail_id)
                                self.logger.info(f"Cancelled thumbnail creation for: {video_path}")
                            except Exception as e:
                                self.logger.error(f"Error processing thumbnail result: {str(e)}")
                                done_futures.append(thumbnail_id)
                    
                    # 처리 완료된 Future 제거
                    for thumbnail_id in done_futures:
                        del self._futures[thumbnail_id]
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in result processing: {str(e)}")
                continue

# 전역 worker 인스턴스
_worker: Optional[ThumbnailWorker] = None
_worker_lock = threading.Lock()

def get_thumbnail_worker(settings: Settings) -> ThumbnailWorker:
    """ThumbnailWorker의 싱글톤 인스턴스를 반환합니다."""
    global _worker
    
    # 첫 번째 검사 (락 없이)
    if _worker is not None:
        return _worker
        
    with _worker_lock:
        # 두 번째 검사 (락 안에서)
        if _worker is None:
            _worker = ThumbnailWorker(settings)
            _worker.start()
        return _worker

def shutdown_thumbnail_worker():
    """ThumbnailWorker를 종료합니다."""
    global _worker
    with _worker_lock:
        if _worker is not None:
            _worker.stop()
            _worker = None