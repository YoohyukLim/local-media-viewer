import os
import sys
import logging
import argparse
import yaml
import platform
import socket
import selectors
import subprocess
import signal
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
        self.host = self.config.get('host', 'localhost')
        self.port = self.config.get('port', 9990)
        self.platform = platform.system()
        self.sel = selectors.DefaultSelector()
        self.server_socket = None
        self.running = True
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러"""
        signal_name = signal.Signals(signum).name
        logger.info(f"Received signal {signal_name}")
        self.running = False
        self.cleanup()
    
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
    
    def load_config(self, config_path: str) -> dict:
        """설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            sys.exit(1)
    
    def accept(self, sock: socket.socket, mask):
        """새로운 클라이언트 연결 처리"""
        conn, addr = sock.accept()
        logger.info(f'Accepted connection from {addr}')
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.read)
    
    def read(self, conn: socket.socket, mask):
        """클라이언트로부터 데이터 읽기"""
        try:
            data = conn.recv(4096).decode('utf-8')
            if data:
                if '\n' in data:
                    file_path = data.strip()
                    self.open_file(file_path)
        
            # 데이터 처리 후 항상 연결 종료
            logger.info('Closing connection')
            self.sel.unregister(conn)
            conn.close()
        except Exception as e:
            logger.error(f'Error reading from socket: {e}')
            self.sel.unregister(conn)
            conn.close()
    
    def cleanup(self):
        """소켓 및 셀렉터 정리"""
        if self.running:  # 중복 cleanup 방지
            self.running = False
            if self.server_socket:
                self.sel.unregister(self.server_socket)
                self.server_socket.close()
            self.sel.close()
            logger.info("Cleaned up server resources")
    
    def monitor(self):
        """TCP 서버 실행 및 모니터링"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.setblocking(False)
            
            self.sel.register(self.server_socket, selectors.EVENT_READ, self.accept)
            logger.info(f'Starting monitor on {self.host}:{self.port}')
            
            while self.running:
                events = self.sel.select(timeout=1.0)
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)
                    
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Server error: {e}")
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