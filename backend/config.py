# 파일명: backend/config.py
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Azure OpenAI 설정 (여러 명칭 지원)
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY") or os.getenv("AZURE_OPENAI_API_KEY", "your-key")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com/")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "dev-gpt-4.1-mini")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# 데이터베이스 설정
DB_PATH = os.getenv("DB_PATH", "./logs.db")

# 로그 파일 설정
LOG_FILE = os.getenv("LOG_FILE") or os.getenv("LLOG_FILE", "./tomcat.log")  # LLOG_FILE 오타 지원

# 기타 설정
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "10"))  # 초
LOG_GENERATION_INTERVAL = 5  # 초

# Azure OpenAI 설정 검증 함수
def validate_azure_config():
    """Azure OpenAI 설정 검증"""
    if AZURE_OPENAI_KEY == "your-key" or not AZURE_OPENAI_KEY:
        return False, "AZURE_OPENAI_KEY가 설정되지 않았습니다."
    
    if not AZURE_OPENAI_ENDPOINT.startswith("https://"):
        return False, "AZURE_OPENAI_ENDPOINT가 올바르지 않습니다."
    
    if AZURE_OPENAI_DEPLOYMENT == "dev-gpt-4.1-mini" and "dev-gpt-4.1-mini" not in AZURE_OPENAI_DEPLOYMENT:
        return False, "AZURE_OPENAI_DEPLOYMENT를 확인해주세요."
    
    return True, "설정이 올바릅니다."

# 설정 상태 출력
def print_config_status():
    """현재 설정 상태 출력"""
    print("=== Azure OpenAI 설정 상태 ===")
    print(f"Key: {'설정됨' if AZURE_OPENAI_KEY and AZURE_OPENAI_KEY != 'your-key' else '❌ 미설정'}")
    print(f"Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f"Deployment: {AZURE_OPENAI_DEPLOYMENT}")
    print(f"API Version: {AZURE_OPENAI_API_VERSION}")
    
    is_valid, message = validate_azure_config()
    print(f"상태: {'✅' if is_valid else '❌'} {message}")
    print("=" * 30)