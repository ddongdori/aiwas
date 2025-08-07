# 📊 Tomcat WAS 로그 모니터링 & AI 분석 시스템

**📖 프로젝트 개요**

Tomcat WAS 에러 로그를 모니터링하고 AI 기반 분석을 제공하는 웹 애플리케이션입니다. Streamlit과 OpenAI API를 활용하여 에러 로그의 원인 분석과 해결 방안을 자동으로 제공합니다.

## ✨ 주요 기능

- **로그 모니터링**: Tomcat WAS 에러 로그 실시간 감지 및 수집
- **AI 기반 분석**: OpenAI GPT 모델을 활용한 에러 원인 분석 및 해결 방안 제공
- **시각적 대시보드**: 실시간 차트 및 통계 정보 제공
- **로그 검색**: 날짜, 시간, 키워드 기반 로그 검색
- **클립보드 복사**: AI 분석 결과를 클립보드로 간편 복사

## 🛠 기술 스택

### Backend & Database
- **Database**: SQLite (로그 데이터 저장)
- **State Management**: Streamlit Session State
- **Data Processing**: Pandas

### AI & Analytics
- **AI API**: Azure OpenAI Service (GPT 모델)
- **Data Visualization**: Plotly
- **Real-time Processing**: 백그라운드 로그 모니터링

### Frontend
- **UI Framework**: Streamlit
- **Styling**: Custom CSS (모던 블루 테마)
- **Interactive Components**: 
  - 로그 차트
  - 페이징 테이블
  - 검색 필터
  - 클립보드 복사 기능

## 📦 Python 핵심 패키지
    streamlit>=1.28.0          # 웹 프레임워크
    pandas>=1.5.0              # 데이터 처리
    plotly>=5.15.0             # 시각화
    langchain>=0.1.0           # AI 워크플로우
    langchain-openai>=0.1.0    # Azure OpenAI 통합
    python-dotenv>=1.0.0       # 환경 변수
    requests>=2.30.0           # HTTP 클라이언트

## 🏗 프로젝트 구조
    LogIQ_v2/
    ├── frontend/
    │   └── app.py                    # Streamlit 메인 앱
    ├── backend/
    │   ├── config.py                 # 설정 및 검증
    │   ├── db_manager.py             # SQLite DB 관리
    │   ├── ai_analyzer.py            # AI 분석 인터페이스
    │   ├── langchain_chain.py        # LangChain AI 엔진
    │   ├── log_monitor.py            # 로그 모니터링
    │   └── log_generator.py          # 샘플 로그 생성
    ├── requirements.txt              # Python 의존성
    ├── .env                          # 환경 변수
    └── README.md                     # 프로젝트 문서

## 🔧 설치 및 실행
### 1. 패키지 설치
    pip install -r requirements.txt
### 2. 환경변수 설정
    .env 파일 생성:
    OPENAI_API_TYPE
    AZURE_OPENAI_KEY
    AZURE_OPENAI_API_VERSION
    AZURE_OPENAI_ENDPOINT
    AZURE_OPENAI_DEPLOYMENT
    LOG_FILE=./tomcat.log
    DB_PATH=./logs.db
    REFRESH_INTERVAL=5000
### 3. 애플리케이션 실행
    streamlit run app.py

## 🏛️ 4계층 아키텍쳐
    📱 Layer 1: app.py (Frontend/Presentation Layer)
        - UI/UX: Streamlit 컴포넌트 렌더링
        - 사용자 상호작용: 버튼, 입력, 테이블 등
        - 데이터 시각화: 차트, 메트릭, 테이블 표시
        - 상태 관리: Session State 관리
    🔗 Layer 2: ai_analyzer.py (Business Logic/Service Layer)
        - 비즈니스 로직: 에러 검증, 데이터 전처리
        - 오케스트레이션: 여러 서비스 조합
        - 추상화: Frontend와 AI 엔진 사이 중간층
        - 다양한 인터페이스: ID 기반, 메시지 직접 등
    🤖 Layer 3: langchain_chain.py (AI Orchestration Layer)
        - 프롬프트 엔지니어링: 전문적인 System/Human 메시지
        - LLM 설정: Temperature, API 버전 등 최적화
        - 템플릿 관리: 재사용 가능한 프롬프트 템플릿
        - LangChain 기능: Chain, Memory, Parser 활용
    ☁️ Layer 4: Azure OpenAI API (External Service)
        - 실제 AI 추론: GPT 모델 실행
