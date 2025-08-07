# 파일명: backend/langchain_chain.py
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import AIMessage
from .config import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION, validate_azure_config

class LogAnalysisChain:
    def __init__(self):
        # 설정 검증
        is_valid, message = validate_azure_config()
        if not is_valid:
            print(f"⚠️ Azure OpenAI 설정 오류: {message}")
            self.llm = None
            self.prompt_template = None
            return
        
        try:
            self.llm = AzureChatOpenAI(
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_KEY,
                api_version=AZURE_OPENAI_API_VERSION,
                deployment_name=AZURE_OPENAI_DEPLOYMENT,
                temperature=0.7
            )
            self.prompt_template = self._create_prompt_template()
            print("✅ Azure OpenAI 연결 설정 완료")
        except Exception as e:
            print(f"❌ Azure OpenAI 초기화 오류: {e}")
            self.llm = None
            self.prompt_template = None
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """LangChain 프롬프트 템플릿 생성"""
        system_message = SystemMessagePromptTemplate.from_template(
            """당신은 Tomcat WAS 로그 분석 전문가입니다. 
            Java 웹 애플리케이션 서버 환경에서 발생하는 다양한 에러를 분석하고 해결책을 제시하는 것이 주요 업무입니다.
            
            분석 시 고려사항:
            - HTTP 응답 코드별 의미
            - 메모리 관련 이슈 (OutOfMemoryError, GC 등)
            - 데이터베이스 연결 문제
            - 네트워크 및 타임아웃 이슈
            - 애플리케이션 로직 오류
            
            응답 형식:
            원인 분석:
            - [구체적인 원인 설명]
            
            해결 방안:
            - [실행 가능한 해결책 제시]"""
        )
        
        human_message = HumanMessagePromptTemplate.from_template(
            """다음 Tomcat WAS 에러 로그를 분석해주세요:
            
            로그 레벨: {level}
            에러 메시지: {message}
            응답 시간: {response_time}ms
            발생 시간: {timestamp}
            
            이 에러의 원인과 해결 방안을 제시해주세요."""
        )
        
        return ChatPromptTemplate.from_messages([system_message, human_message])
    
    def analyze_log(self, log_data: dict) -> str:
        """로그 분석 실행"""
        # Azure OpenAI 설정 확인
        if self.llm is None:
            return """❌ Azure OpenAI 설정이 올바르지 않습니다.

다음을 확인해주세요:

1. .env 파일 설정:
   - AZURE_OPENAI_KEY: 실제 Azure OpenAI API 키
   - AZURE_OPENAI_ENDPOINT: https://your-resource.openai.azure.com/ 형태
   - AZURE_OPENAI_DEPLOYMENT: 실제 배포된 모델명 (예: gpt-4, gpt-35-turbo)

2. Azure OpenAI 리소스 확인:
   - 구독이 활성화되어 있는지 확인
   - 올바른 지역의 엔드포인트인지 확인
   - 배포된 모델명이 정확한지 확인

3. 네트워크 연결 확인:
   - 방화벽이나 프록시 설정 확인"""
        
        try:
            # 프롬프트 생성
            formatted_prompt = self.prompt_template.format_messages(
                level=log_data.get('level', 'UNKNOWN'),
                message=log_data.get('message', ''),
                response_time=log_data.get('response_time', 0),
                timestamp=log_data.get('timestamp', '')
            )
            
            # LLM 호출 (invoke 메서드 사용)
            response = self.llm.invoke(formatted_prompt)
            
            if isinstance(response, AIMessage):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            error_message = str(e)
            
            # 구체적인 오류 메시지 제공
            if "401" in error_message:
                return """❌ 인증 오류 (401):

문제: API 키 또는 엔드포인트가 올바르지 않습니다.

해결 방법:
1. .env 파일에서 AZURE_OPENAI_KEY 확인
2. Azure Portal에서 API 키 재생성
3. AZURE_OPENAI_ENDPOINT URL 확인 (예: https://your-resource.openai.azure.com/)
4. 구독이 활성 상태인지 확인"""
            
            elif "404" in error_message:
                return """❌ 리소스를 찾을 수 없음 (404):

문제: 배포명 또는 엔드포인트가 잘못되었습니다.

해결 방법:
1. AZURE_OPENAI_DEPLOYMENT 이름 확인
2. Azure Portal에서 실제 배포된 모델명 확인
3. 엔드포인트 URL이 정확한지 확인"""
            
            elif "429" in error_message:
                return """❌ 요청 한도 초과 (429):

문제: API 호출 한도를 초과했습니다.

해결 방법:
1. 잠시 후 다시 시도
2. 구독 플랜 확인 및 업그레이드 고려"""
            
            else:
                return f"""❌ 분석 중 오류가 발생했습니다:

오류 내용: {error_message}

일반적인 해결 방법:
1. 인터넷 연결 확인
2. Azure OpenAI 서비스 상태 확인
3. API 키와 엔드포인트 재확인"""

# 전역 인스턴스
log_analysis_chain = LogAnalysisChain()