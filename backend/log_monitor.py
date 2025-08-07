# 파일명: backend/log_monitor.py
import threading
import time
import os
import re
from typing import Optional
from .db_manager import db_manager
from .config import LOG_FILE

class LogMonitor:
    def __init__(self):
        self.log_file = LOG_FILE
        self.db = db_manager
        self.monitoring = False
        self.monitor_thread = None
        
        # 에러 패턴 정의
        self.error_patterns = {
            'ERROR': re.compile(r'ERROR'),
            'FATAL': re.compile(r'FATAL'),
            'Exception': re.compile(r'Exception'),
            'OutOfMemoryError': re.compile(r'OutOfMemoryError'),
            'SQLException': re.compile(r'SQLException'),
            'TimeoutException': re.compile(r'TimeoutException'),
        }
    
    def start_monitoring(self):
        """로그 모니터링 시작"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print(f"로그 모니터링 시작: {self.log_file}")
    
    def stop_monitoring(self):
        """로그 모니터링 중지"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        print("로그 모니터링 중지")
    
    def _monitor_loop(self):
        """로그 파일 tail 모드 모니터링"""
        try:
            self._ensure_log_file_exists()
            
            with open(self.log_file, 'r', encoding='utf-8') as file:
                # 파일 끝으로 이동
                file.seek(0, 2)
                
                while self.monitoring:
                    line = file.readline()
                    if line:
                        self._process_log_line(line.strip())
                    else:
                        time.sleep(0.1)  # 새로운 로그 대기
                        
        except Exception as e:
            print(f"로그 모니터링 오류: {e}")
    
    def _ensure_log_file_exists(self):
        """로그 파일 존재 확인 및 생성"""
        if not os.path.exists(self.log_file):
            # 디렉토리 생성
            os.makedirs(os.path.dirname(self.log_file) if os.path.dirname(self.log_file) else '.', exist_ok=True)
            # 빈 파일 생성
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("")
    
    def _process_log_line(self, line: str):
        """로그 라인 처리 및 에러 감지"""
        try:
            # 에러 패턴 확인
            for level, pattern in self.error_patterns.items():
                if pattern.search(line):
                    # 응답시간 추출 (예: [1234ms] 형태)
                    response_time = self._extract_response_time(line)
                    
                    # DB에 저장
                    self.db.insert_log(
                        level=level,
                        message=line,
                        response_time=response_time
                    )
                    print(f"에러 로그 감지: {level} - {line[:100]}...")
                    break
                    
        except Exception as e:
            print(f"로그 처리 오류: {e}")
    
    def _extract_response_time(self, line: str) -> int:
        """로그에서 응답시간 추출"""
        try:
            # [1234ms] 패턴 검색
            match = re.search(r'\[(\d+)ms\]', line)
            if match:
                return int(match.group(1))
            
            # 다른 패턴들도 추가 가능
            # response_time=1234 패턴
            match = re.search(r'response_time=(\d+)', line)
            if match:
                return int(match.group(1))
                
        except:
            pass
        
        return 0  # 기본값

# 전역 인스턴스
log_monitor = LogMonitor()