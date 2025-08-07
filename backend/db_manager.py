# 파일명: backend/db_manager.py
import sqlite3
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from .config import DB_PATH

# 한국 시간대 설정
KST = timezone(timedelta(hours=9))

class DatabaseManager:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_database()
        
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    response_time INTEGER DEFAULT 0,
                    created_at DATETIME NOT NULL
                )
            ''')
            conn.commit()
    
    def insert_log(self, level: str, message: str, response_time: int = 0, timestamp=None):
        """에러 로그 삽입 (한국 시간으로)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # timestamp가 전달되지 않으면 한국 시간으로 생성
            if timestamp is None:
                current_timestamp = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
            else:
                # datetime 객체가 전달된 경우
                if hasattr(timestamp, 'strftime'):
                    current_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    current_timestamp = str(timestamp)
            
            cursor.execute('''
                INSERT INTO error_logs (timestamp, level, message, response_time, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (current_timestamp, level, message, response_time, current_timestamp))
            conn.commit()
    
    def get_recent_logs(self, limit: int = 10, search_query: str = None, 
                       start_date: str = None, end_date: str = None) -> List[Dict]:
        """최근 에러 로그 조회"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT id, timestamp, level, message, response_time
                FROM error_logs
                WHERE 1=1
            '''
            params = []
            
            if search_query:
                query += " AND message LIKE ?"
                params.append(f"%{search_query}%")
            
            if start_date:
                query += " AND DATE(timestamp) >= ?"
                params.append(start_date)
                
            if end_date:
                query += " AND DATE(timestamp) <= ?"
                params.append(end_date)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
    
    def get_error_stats_last_hour(self) -> List[Dict]:
        """최근 1시간 에러 통계 (5분 간격) - 한국 시간 기준"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 한국 시간 기준으로 1시간 전 계산
            one_hour_ago = datetime.now(KST) - timedelta(hours=1)
            one_hour_ago_str = one_hour_ago.strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
                SELECT 
                    strftime('%Y-%m-%d %H:%M', 
                        datetime(timestamp, '-' || (strftime('%M', timestamp) % 5) || ' minutes')
                    ) as time_bucket,
                    AVG(response_time) as avg_response_time,
                    COUNT(*) as error_count
                FROM error_logs 
                WHERE timestamp >= ?
                GROUP BY time_bucket
                ORDER BY time_bucket
            ''', (one_hour_ago_str,))
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
    
    def get_log_by_id(self, log_id: int) -> Optional[Dict]:
        """ID로 로그 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, timestamp, level, message, response_time
                FROM error_logs
                WHERE id = ?
            ''', (log_id,))
            
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None

# 전역 인스턴스
db_manager = DatabaseManager()