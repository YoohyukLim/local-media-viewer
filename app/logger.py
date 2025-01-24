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

# 로그 메시지를 저장할 큐
log_queue = queue.Queue()

def setup_logger():
    """애플리케이션 로거를 설정합니다."""
    logger = logging.getLogger('video_manager')
    logger.setLevel(logging.INFO)
    
    # 큐 핸들러 설정
    queue_handler = logging.handlers.QueueHandler(log_queue)
    logger.addHandler(queue_handler)
    
    # 콘솔 출력을 처리할 리스너 설정
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = CustomFormatter('[%(timestamp)s] %(message)s')
    console_handler.setFormatter(formatter)
    
    # 리스너 스레드 시작
    listener = logging.handlers.QueueListener(log_queue, console_handler)
    listener.start()
    
    return logger, listener

# 전역 로거 인스턴스와 리스너
logger, log_listener = setup_logger()

def get_worker_logger():
    """워커 프로세스용 로거를 반환합니다."""
    worker_logger = logging.getLogger('video_manager.worker')
    if not worker_logger.handlers:
        # 로그 디렉토리 생성
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # 파일 핸들러 설정
        file_handler = logging.FileHandler(
            os.path.join(log_dir, "thumbnail_worker.log"),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        formatter = CustomFormatter('[%(timestamp)s] %(message)s')
        file_handler.setFormatter(formatter)
        worker_logger.addHandler(file_handler)
        
        # 큐 핸들러도 추가하여 콘솔에도 출력
        queue_handler = logging.handlers.QueueHandler(log_queue)
        worker_logger.addHandler(queue_handler)
        
        worker_logger.setLevel(logging.INFO)
    return worker_logger 