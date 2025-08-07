# 파일명: backend/ai_analyzer.py
from .langchain_chain import log_analysis_chain
from .db_manager import db_manager
from typing import Dict, Optional

class AIAnalyzer:
    def __init__(self):
        self.chain = log_analysis_chain
        self.db = db_manager
    
    def analyze_error_log(self, log_id: int) -> Optional[str]:
        """에러 로그 AI 분석"""
        try:
            # DB에서 로그 조회
            log_data = self.db.get_log_by_id(log_id)
            if not log_data:
                return "해당 로그를 찾을 수 없습니다."
            
            # LangChain을 통한 분석
            analysis_result = self.chain.analyze_log(log_data)
            return analysis_result
            
        except Exception as e:
            return f"분석 중 오류가 발생했습니다: {str(e)}"
    
    def analyze_log_message(self, log_message: str, log_level: str = "ERROR", 
                           response_time: int = 0) -> str:
        """로그 메시지 직접 분석"""
        try:
            log_data = {
                'level': log_level,
                'message': log_message,
                'response_time': response_time,
                'timestamp': 'N/A'
            }
            
            analysis_result = self.chain.analyze_log(log_data)
            return analysis_result
            
        except Exception as e:
            return f"분석 중 오류가 발생했습니다: {str(e)}"

# 전역 인스턴스
ai_analyzer = AIAnalyzer()