import os
import sys
import time
import subprocess
import logging
import argparse
import yaml
import atexit
import platform
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlayerMonitor:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.pipe_path = self.config.get('pipe_path', 'D:/videos/player.pipe')
        self.ensure_pipe()
        # 프로세스 종료 시 파이프 파일 정리
        atexit.register(self.cleanup)
        
        # 플랫폼 확인
        self.platform = platform.system()
    
    def open_file(self, file_path: str):
        """플랫폼에 따라 파일 열기"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return
                
            if self.platform == "Windows":
                os.startfile(file_path)
            elif self.platform == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
                
            logger.info(f"Opened file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to open file: {e}")
    
    def cleanup(self):
        """파이프 파일 정리"""
        try:
            if os.path.exists(self.pipe_path):
                os.remove(self.pipe_path)
                logger.info(f"Removed pipe file: {self.pipe_path}")
        except Exception as e:
            logger.error(f"Failed to remove pipe file: {e}")
    
    def load_config(self, config_path: str) -> dict:
        """설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            sys.exit(1)
    
    def ensure_pipe(self):
        """파이프 파일이 없으면 생성"""
        try:
            pipe_dir = os.path.dirname(self.pipe_path)
            os.makedirs(pipe_dir, exist_ok=True)
            
            # 파일이 없으면 빈 파일 생성
            if not os.path.exists(self.pipe_path):
                open(self.pipe_path, 'w').close()
                logger.info(f"Created pipe file at {self.pipe_path}")
        except Exception as e:
            logger.error(f"Failed to create pipe file: {e}")
            sys.exit(1)
    
    def execute_command(self, command: str):
        """Windows start 커맨드 실행"""
        try:
            subprocess.run(command, shell=True)
            logger.info(f"Executed command: {command}")
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
    
    def monitor(self):
        """파이프 파일 모니터링"""
        logger.info(f"Starting monitor on {self.pipe_path}")
        
        try:
            last_position = 0
            while True:
                try:
                    with open(self.pipe_path, 'r') as pipe:
                        pipe.seek(last_position)
                        while True:
                            file_path = pipe.readline().strip()
                            if file_path:
                                self.open_file(file_path)
                            last_position = pipe.tell()
                            time.sleep(0.1)
                except KeyboardInterrupt:
                    logger.info("Received shutdown signal")
                    break
                except Exception as e:
                    logger.error(f"Error reading from pipe: {e}")
                    time.sleep(1)
        finally:
            self.cleanup()

def main():
    parser = argparse.ArgumentParser(description='Video Player Monitor')
    parser.add_argument('--config', type=str, default='config.yaml',
                      help='Path to config file (default: config.yaml)')
    args = parser.parse_args()
    
    monitor = PlayerMonitor(args.config)
    monitor.monitor()

if __name__ == "__main__":
    main() 