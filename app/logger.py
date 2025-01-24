import logging
import logging.handlers
import queue
import threading
from datetime import datetime
import os

class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return super().format(record)

class LogManager:
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self.queue = queue.Queue()
        self.listener = None
        self.logger = None
        self.setup_logger()
    
    def setup_logger(self):
        """애플리케이션 로거를 설정합니다."""
        if self.logger is not None:
            return
            
        self.logger = logging.getLogger('video_manager')
        self.logger.setLevel(logging.INFO)
        
        # 큐 핸들러 설정
        queue_handler = logging.handlers.QueueHandler(self.queue)
        self.logger.addHandler(queue_handler)
        
        # 콘솔 출력을 처리할 리스너 설정
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = CustomFormatter('[%(timestamp)s] %(message)s')
        console_handler.setFormatter(formatter)
        
        # 리스너 스레드 시작
        self.listener = logging.handlers.QueueListener(self.queue, console_handler)
        self.listener.start()
    
    def stop(self):
        """로거를 안전하게 종료합니다."""
        if self.listener is not None:
            try:
                self.listener.stop()
                self.listener = None
            except Exception as e:
                print(f"Error stopping log listener: {e}")
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = LogManager()
        return cls._instance

# 전역 로그 매니저 인스턴스
log_manager = LogManager.get_instance()
logger = log_manager.logger

def get_worker_logger():
    """워커 프로세스용 로거를 반환합니다."""
    worker_logger = logging.getLogger('video_manager.worker')
    if not worker_logger.handlers:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(
            os.path.join(log_dir, "thumbnail_worker.log"),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        formatter = CustomFormatter('[%(timestamp)s] %(message)s')
        file_handler.setFormatter(formatter)
        worker_logger.addHandler(file_handler)
        worker_logger.setLevel(logging.INFO)
    return worker_logger

def shutdown_logger():
    """로거를 종료합니다."""
    log_manager.stop() 