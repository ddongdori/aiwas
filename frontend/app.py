# 파일명: frontend/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta, timezone
import sys
import os
import time

# 한국 시간대 설정
KST = timezone(timedelta(hours=9))

# 백엔드 모듈 import를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.db_manager import db_manager
from backend.ai_analyzer import ai_analyzer  # ai_analyzer로 복원 (내부적으로 LangChain 사용)
from backend.log_monitor import log_monitor
from backend.log_generator import log_generator
from backend.config import REFRESH_INTERVAL

# Streamlit 페이지 설정
st.set_page_config(
    page_title="Tomcat WAS 로그 모니터",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 현대적이고 깔끔한 CSS 스타일 + JavaScript 적용
st.markdown("""
<style>
    /* ===== 전체 앱 스타일 ===== */
    .stApp {
        background-color: #FFFFFF;
        color: #333333;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    }
    
    /* ===== 메인 컨테이너 ===== */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: none;
    }
    
    /* ===== 사이드바 스타일 ===== */
    .sidebar .sidebar-content {
        background-color: #F8F9FA;
        border-right: 2px solid #E9ECEF;
        width: 370px !important;
        min-width: 370px !important;
    }
    
    /* 사이드바 컨테이너 전체 */
    section[data-testid="stSidebar"] {
        width: 370px !important;
        min-width: 370px !important;
        max-width: 370px !important;
    }
    
    section[data-testid="stSidebar"] > div {
        width: 370px !important;
        min-width: 370px !important;
        max-width: 370px !important;
    }
    
    /* ===== 앱 헤더 ===== */
    .app-header {
        background: linear-gradient(135deg, #007BFF 0%, #0056b3 100%);
        color: white;
        padding: 1.5rem 2rem;
        margin: -2rem -2rem 2rem -2rem;
        border-radius: 0 0 10px 10px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0, 123, 255, 0.2);
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .app-subtitle {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* ===== 메트릭 카드 ===== */
    .metric-card {
        background: #FFFFFF;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #E9ECEF;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin: 0.5rem 0;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 8px rgba(0,123,255,0.1);
        transform: translateY(-2px);
        border-color: #007BFF;
    }
    
    /* ===== 표시기 ===== */
    .realtime-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #28A745 0%, #20C997 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 1rem;
        animation: pulse 1s infinite;
    }
    
    .realtime-dot {
        width: 6px;
        height: 6px;
        background-color: white;
        border-radius: 50%;
        animation: blink 0.5s infinite;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
    
    /* ===== 섹션 컨테이너 ===== */
    .section-container {
        background: #FFFFFF;
        border: 1px solid #E9ECEF;
        border-radius: 8px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* ===== 버튼 스타일 ===== */
    .stButton > button {
        background-color: #007BFF !important;
        color: white !important;
        border: 2px solid #007BFF !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(0,123,255,0.2) !important;
    }
    
    .stButton > button:hover {
        background-color: #0056b3 !important;
        border-color: #0056b3 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0,123,255,0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    .stButton > button:disabled {
        background-color: #E9ECEF !important;
        color: #6C757D !important;
        border-color: #DEE2E6 !important;
        cursor: not-allowed !important;
        box-shadow: none !important;
        transform: none !important;
    }
    
    .stButton > button:disabled:hover {
        background-color: #E9ECEF !important;
        color: #6C757D !important;
        border-color: #DEE2E6 !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* Primary 버튼 (AI 분석) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #007BFF 0%, #0056b3 100%) !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.7rem 1.5rem !important;
        border: none !important;
    }
    
    /* Secondary 버튼 */
    .stButton > button[kind="secondary"] {
        background-color: #6C757D !important;
        border: 2px solid #6C757D !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #5A6268 !important;
        border-color: #5A6268 !important;
    }
    
    /* ===== 클립보드 복사 버튼 스타일 ===== */
    .copy-button {
        background: linear-gradient(135deg, #28A745 0%, #20C997 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(40,167,69,0.2);
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .copy-button:hover {
        background: linear-gradient(135deg, #20C997 0%, #28A745 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(40,167,69,0.3);
    }
    
    .copy-button:active {
        transform: translateY(0);
    }
    
    .copy-success {
        background: linear-gradient(135deg, #28A745 0%, #20C997 100%) !important;
        animation: copySuccess 0.3s ease;
    }
    
    @keyframes copySuccess {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* ===== 제목 스타일 ===== */
    h1, h2, h3, h4 {
        color: #333333 !important;
        font-weight: 700;
    }
    
    h1 {
        color: #007BFF !important;
        font-size: 2.5rem !important;
    }
    
    h2 {
        color: #007BFF !important;
        font-size: 2rem !important;
        border-bottom: 2px solid #007BFF;
        padding-bottom: 0.5rem;
    }
    
    h3 {
        color: #495057 !important;
        font-size: 1.5rem !important;
    }
    
    /* ===== 입력 필드 스타일 ===== */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input {
        background: #FFFFFF;
        border: 2px solid #E9ECEF;
        border-radius: 5px;
        color: #333333;
        font-size: 0.9rem;
        padding: 0.5rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stDateInput > div > div > input:focus,
    .stTimeInput > div > div > input:focus {
        border-color: #007BFF;
        box-shadow: 0 0 0 2px rgba(0,123,255,0.1);
        outline: none;
    }
    
    /* ===== 데이터프레임 스타일 ===== */
    .stDataFrame {
        border: 1px solid #E9ECEF;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* ===== 메시지 스타일 ===== */
    .stSuccess {
        background-color: #D4EDDA;
        border: 1px solid #C3E6CB;
        border-left: 4px solid #28A745;
        color: #155724;
    }
    
    .stWarning {
        background-color: #FFF3CD;
        border: 1px solid #FFEAA7;
        border-left: 4px solid #FFC107;
        color: #856404;
    }
    
    .stError {
        background-color: #F8D7DA;
        border: 1px solid #F5C6CB;
        border-left: 4px solid #DC3545;
        color: #721C24;
    }
    
    .stInfo {
        background-color: #CCE7FF;
        border: 1px solid #B8DAFF;
        border-left: 4px solid #007BFF;
        color: #004085;
    }
    
    /* ===== Expander 스타일 ===== */
    .streamlit-expanderHeader {
        background-color: #F8F9FA;
        border: 1px solid #DEE2E6;
        color: #495057;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #E9ECEF;
    }
    
    .streamlit-expanderContent {
        background-color: #FFFFFF;
        border: 1px solid #DEE2E6;
        border-top: none;
    }
    
    /* ===== 사이드바 버튼 스타일 ===== */
    .sidebar .stButton > button {
        background-color: #007BFF;
        color: white;
        border: none;
        width: 100%;
        margin: 0.2rem 0;
    }
    
    .sidebar .stButton > button:hover {
        background-color: #0056b3;
    }
    
    /* ===== 상태 표시기 ===== */
    .status-online {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #28A745;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    .status-offline {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #DC3545;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* ===== 배지 스타일 ===== */
    .badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    
    .badge-primary {
        background-color: #CCE7FF;
        color: #004085;
        border: 1px solid #B8DAFF;
    }
    
    .badge-success {
        background-color: #D4EDDA;
        color: #155724;
        border: 1px solid #C3E6CB;
    }
    
    .badge-warning {
        background-color: #FFF3CD;
        color: #856404;
        border: 1px solid #FFEAA7;
    }
    
    .badge-error {
        background-color: #F8D7DA;
        color: #721C24;
        border: 1px solid #F5C6CB;
    }
    
    /* ===== 하이라이트 카드 ===== */
    .highlight-card {
        background: linear-gradient(135deg, #CCE7FF 0%, #E3F2FD 100%);
        border: 2px solid #007BFF;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,123,255,0.1);
    }
    
    .success-card {
        background: linear-gradient(135deg, #D4EDDA 0%, #F8FFF9 100%);
        border: 2px solid #28A745;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(40,167,69,0.1);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #FFF3CD 0%, #FFFEF7 100%);
        border: 2px solid #FFC107;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(255,193,7,0.1);
    }
    
    /* ===== 페이지네이션 ===== */
    .pagination-info {
        background-color: #F8F9FA;
        border: 1px solid #DEE2E6;
        border-radius: 5px;
        padding: 1rem;
        text-align: center;
        color: #6C757D;
        font-weight: 600;
        margin: 1rem 0;
    }
    
    /* ===== 정보 섹션 ===== */
    .info-box {
        background-color: #F8F9FA;
        border-left: 4px solid #007BFF;
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    
    /* ===== 하단 고정 상태바 ===== */
    .status-bar {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #FFFFFF;
        border: 1px solid #DEE2E6;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        z-index: 1000;
        font-size: 0.85rem;
        color: #6C757D;
    }
    
    /* ===== 스크롤바 스타일 ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F8F9FA;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #007BFF;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #0056b3;
    }
    
    /* ===== 메트릭 카드 중앙 정렬 ===== */
    div[data-testid="metric-container"] {
        text-align: center;
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    div[data-testid="metric-container"] > div {
        justify-content: center;
    }
    
    div[data-testid="metric-container"] label {
        text-align: center;
        justify-content: center;
    }
    
    div[data-testid="metric-container"] div[data-testid="metric-value"] {
        text-align: center;
        justify-content: center;
    }
    
    div[data-testid="metric-container"] div[data-testid="metric-delta"] {
        text-align: center;
        justify-content: center;
    }
    
    /* ===== 반응형 디자인 ===== */
    @media (max-width: 768px) {
        .app-title {
            font-size: 2rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .section-container {
            padding: 1rem;
        }
    }
</style>

<script>
// 전역 변수로 분석 결과 저장
window.analysisResults = {};

// 분석 결과 저장 함수
function storeAnalysisResult(buttonId, text) {
    window.analysisResults[buttonId] = text;
}

// 클립보드 복사 함수 (저장된 데이터 사용)
function copyStoredToClipboard(buttonId) {
    const text = window.analysisResults[buttonId];
    if (!text) {
        alert('복사할 데이터가 없습니다.');
        return;
    }
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function() {
            showCopySuccess(buttonId);
        }).catch(function(err) {
            console.error('클립보드 복사 실패:', err);
            fallbackCopyText(text, buttonId);
        });
    } else {
        fallbackCopyText(text, buttonId);
    }
}

// 구형 브라우저를 위한 대체 복사 함수
function fallbackCopyText(text, buttonId) {
    try {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
        showCopySuccess(buttonId);
    } catch (err) {
        console.error('대체 복사 방법 실패:', err);
        alert('복사 실패: ' + err);
    }
}

// 복사 성공 표시
function showCopySuccess(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        const originalText = button.innerHTML;
        button.innerHTML = '✅ 복사됨!';
        button.classList.add('copy-success');
        
        setTimeout(function() {
            button.innerHTML = originalText;
            button.classList.remove('copy-success');
        }, 2000);
    }
}
</script>
""", unsafe_allow_html=True)

def initialize_services():
    """서비스 초기화"""
    if 'services_initialized' not in st.session_state:
        log_monitor.start_monitoring()
        log_generator.start_generating()
        st.session_state.services_initialized = True

def get_recent_errors_by_time(minutes=60):
    """지정된 시간(분) 내의 에러 로그 개수와 이전 기간 대비 비교 반환"""
    try:
        import sqlite3
        from backend.config import DB_PATH
        
        # 현재 시간에서 지정된 분만큼 뺀 시간 (KST 기준)
        now = datetime.now(KST)
        current_start = now - timedelta(minutes=minutes)
        current_start_str = current_start.strftime('%Y-%m-%d %H:%M:%S')
        
        # 이전 기간 (그 전 시간)
        previous_start = now - timedelta(minutes=minutes * 2)
        previous_start_str = previous_start.strftime('%Y-%m-%d %H:%M:%S')
        previous_end_str = current_start.strftime('%Y-%m-%d %H:%M:%S')
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # 현재 기간 에러 수
            cursor.execute('''
                SELECT COUNT(*) 
                FROM error_logs 
                WHERE timestamp >= ?
            ''', (current_start_str,))
            current_count = cursor.fetchone()[0]
            
            # 이전 기간 에러 수
            cursor.execute('''
                SELECT COUNT(*) 
                FROM error_logs 
                WHERE timestamp >= ? AND timestamp < ?
            ''', (previous_start_str, previous_end_str))
            previous_count = cursor.fetchone()[0]
            
            # 증가/감소 계산
            if previous_count > 0:
                delta = current_count - previous_count
                delta_percent = (delta / previous_count) * 100
                if delta > 0:
                    delta_text = f"+{delta} (+{delta_percent:.1f}%)"
                    delta_color = "inverse"
                elif delta < 0:
                    delta_text = f"{delta} ({delta_percent:.1f}%)"
                    delta_color = "normal"
                else:
                    delta_text = "변화없음"
                    delta_color = "normal"
            else:
                if current_count > 0:
                    delta_text = f"+{current_count} (신규)"
                    delta_color = "inverse"
                else:
                    delta_text = "에러 없음"
                    delta_color = "normal"
            
            return current_count, delta_text, delta_color
            
    except Exception as e:
        st.error(f"에러 수 조회 실패: {e}")
        return 0, "조회 실패", "normal"

def get_realtime_error_stats():
    """최근 1시간 에러 통계 생성 (5분 단위)"""
    try:
        import sqlite3
        from backend.config import DB_PATH
        
        # 현재 시간에서 1시간 전까지 (KST 기준)
        now = datetime.now(KST)
        one_hour_ago = now - timedelta(hours=1)
        
        # 5분 단위로 시간 구간 생성 (더 세밀한 모니터링)
        time_buckets = []
        current_time = one_hour_ago
        while current_time <= now:
            time_buckets.append(current_time)
            current_time += timedelta(minutes=5)
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            stats_data = []
            
            for i in range(len(time_buckets) - 1):
                bucket_start = time_buckets[i]
                bucket_end = time_buckets[i + 1]
                
                bucket_start_str = bucket_start.strftime('%Y-%m-%d %H:%M:%S')
                bucket_end_str = bucket_end.strftime('%Y-%m-%d %H:%M:%S')
                
                # 해당 시간 구간의 에러 수와 평균 응답시간
                cursor.execute('''
                    SELECT 
                        COUNT(*) as error_count,
                        AVG(response_time) as avg_response_time
                    FROM error_logs 
                    WHERE timestamp >= ? AND timestamp < ?
                ''', (bucket_start_str, bucket_end_str))
                
                result = cursor.fetchone()
                error_count = result[0] if result[0] else 0
                avg_response_time = result[1] if result[1] else 0
                
                stats_data.append({
                    'time_bucket': bucket_start,
                    'error_count': error_count,
                    'avg_response_time': round(avg_response_time, 1)
                })
            
            return stats_data
            
    except Exception as e:
        st.error(f"통계 조회 실패: {e}")
        return []

def create_copy_button_component(button_id, analysis_text, button_text="분석 결과 복사"):
    """Streamlit 컴포넌트 방식으로 클립보드 복사 버튼 생성"""
    # 텍스트 정리
    clean_text = analysis_text.replace('<br>', '\n').replace('<div>', '').replace('</div>', '').replace('\r', '')
    
    # 고유한 컴포넌트 HTML 생성
    component_html = f"""
    <div style="margin: 1rem 0;">
        <button 
            class="copy-button" 
            id="{button_id}"
            onclick="handleCopyClick('{button_id}')"
            title="분석 결과를 클립보드에 복사합니다"
            style="
                background: linear-gradient(135deg, #28A745 0%, #20C997 100%);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0.6rem 1.2rem;
                font-weight: 600;
                font-size: 0.9rem;
                cursor: pointer;
                transition: all 0.2s ease;
                box-shadow: 0 2px 4px rgba(40,167,69,0.2);
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
            "
        >
            📋 {button_text}
        </button>
    </div>
    
    <script>
        // 분석 결과 저장
        if (typeof window.analysisData === 'undefined') {{
            window.analysisData = {{}};
        }}
        window.analysisData['{button_id}'] = `{clean_text}`;
        
        // 클릭 핸들러
        function handleCopyClick(buttonId) {{
            const text = window.analysisData[buttonId];
            if (!text) {{
                alert('복사할 데이터가 없습니다.');
                return;
            }}
            
            // 클립보드 복사
            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(text).then(function() {{
                    showSuccess(buttonId);
                }}).catch(function(err) {{
                    console.error('복사 실패:', err);
                    fallbackCopy(text, buttonId);
                }});
            }} else {{
                fallbackCopy(text, buttonId);
            }}
        }}
        
        // 구형 브라우저 대응
        function fallbackCopy(text, buttonId) {{
            try {{
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                document.execCommand('copy');
                textArea.remove();
                showSuccess(buttonId);
            }} catch (err) {{
                console.error('대체 복사 실패:', err);
                alert('복사 실패: ' + err);
            }}
        }}
        
        // 성공 표시
        function showSuccess(buttonId) {{
            const button = document.getElementById(buttonId);
            if (button) {{
                const originalText = button.innerHTML;
                button.innerHTML = '✅ 복사됨!';
                button.style.background = 'linear-gradient(135deg, #28A745 0%, #20C997 100%)';
                button.style.transform = 'scale(1.05)';
                
                setTimeout(function() {{
                    button.innerHTML = originalText;
                    button.style.transform = 'scale(1)';
                }}, 2000);
            }}
        }}
    </script>
    """
    
    # HTML 컴포넌트로 렌더링
    st.components.v1.html(component_html, height=80)

def create_app_header():
    """앱 헤더 생성"""
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">📊 Tomcat WAS 로그 모니터</h1>
        <p class="app-subtitle">에러 로그 모니터링 & AI 분석 시스템</p>
    </div>
    """, unsafe_allow_html=True)

def create_realtime_error_chart():
    """에러 통계 차트 생성 - 최근 1시간 기준"""
    # 표시기 추가
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("## 📈 에러 현황")
    
    with col2:
        current_time = datetime.now(KST).strftime('%H:%M:%S')
        st.markdown(f"""
        <div class="realtime-indicator">
            <div class="realtime-dot"></div>
            시간 {current_time}
        </div>
        """, unsafe_allow_html=True)
    
    # 데이터 가져오기
    stats_data = get_realtime_error_stats()
    
    if not stats_data:
        st.info("📊 최근 1시간 내 에러 데이터가 없습니다.")
        return
    
    df = pd.DataFrame(stats_data)
    df['time_bucket'] = pd.to_datetime(df['time_bucket'])
    
    # 현재 시간 기준 1시간 범위 설정
    now = datetime.now(KST)
    one_hour_ago = now - timedelta(hours=1)
    
    # 깔끔한 Plotly 차트 생성
    fig = go.Figure()
    
    # 응답시간 라인 차트
    fig.add_trace(go.Scatter(
        x=df['time_bucket'],
        y=df['avg_response_time'],
        mode='lines+markers',
        name='평균 응답시간 (ms)',
        line=dict(color='#007BFF', width=3),
        marker=dict(size=8, color='#007BFF'),
        hovertemplate='<b>%{y:.1f}ms</b><br>%{x|%H:%M}<extra></extra>',
        connectgaps=False
    ))
    
    # 에러 개수 바 차트 (보조 y축)
    fig.add_trace(go.Bar(
        x=df['time_bucket'],
        y=df['error_count'],
        name='에러 개수',
        yaxis='y2',
        opacity=0.7,
        marker_color='#DC3545',
        hovertemplate='<b>%{y}개</b><br>%{x|%H:%M}<extra></extra>',
        width=300000  # 5분을 밀리초로 변환 (5분 = 300초 = 300,000밀리초)
    ))
    
    # 현재 시간 표시선을 shape으로 추가
    fig.add_shape(
        type="line",
        x0=now,
        x1=now,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(
            color="#28A745",
            width=2,
            dash="dash"
        )
    )
    
    # 현재 시간 주석 추가
    fig.add_annotation(
        x=now,
        y=1,
        yref="paper",
        text="현재 시간",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1,
        arrowcolor="#28A745",
        bgcolor="#28A745",
        bordercolor="#28A745",
        borderwidth=1,
        font=dict(color="white", size=10)
    )
    
    # 깔끔한 레이아웃 설정
    fig.update_layout(
        title=dict(
            text=f'📈 에러 모니터링 (최근 1시간) - 5분 단위',
            font=dict(size=20, color='#333333', family='Arial'),
            x=0.5
        ),
        xaxis=dict(
            title='시간 (5분 단위)',
            color='#333333',
            gridcolor='#E9ECEF',
            range=[one_hour_ago, now],  # datetime 객체 사용 (range에서는 지원됨)
            tickformat='%H:%M',
            dtick=300000  # 5분 간격 (300초 = 300,000밀리초)
        ),
        yaxis=dict(
            title='평균 응답시간 (ms)',
            side='left',
            color='#007BFF',
            gridcolor='#E9ECEF'
        ),
        yaxis2=dict(
            title='에러 개수',
            side='right',
            overlaying='y',
            color='#DC3545'
        ),
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(color='#333333', family='Arial'),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=450,
        margin=dict(t=80, b=50, l=50, r=50)
    )
    
    # 차트 표시
    st.plotly_chart(fig, use_container_width=True)

def perform_error_search(query: str, start_datetime: datetime, end_datetime: datetime):
    """에러 검색 실행"""
    try:
        start_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        end_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        
        import sqlite3
        from backend.config import DB_PATH
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            sql_query = '''
                SELECT id, timestamp, level, message, response_time
                FROM error_logs
                WHERE timestamp BETWEEN ? AND ?
            '''
            params = [start_str, end_str]
            
            if query and query.strip():
                sql_query += ' AND message LIKE ?'
                params.append(f'%{query}%')
            
            sql_query += ' ORDER BY timestamp DESC LIMIT 100'
            
            cursor.execute(sql_query, params)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            results = [dict(zip(columns, row)) for row in rows]
            return results
            
    except Exception as e:
        st.error(f"검색 중 오류가 발생했습니다: {e}")
        return []

def show_search_results_popup():
    """검색 결과 팝업 표시"""
    if st.session_state.get('show_search_results', False):
        if st.session_state.get('search_just_executed', False):
            st.markdown("""
            <div class="highlight-card">
                <h2 style="margin: 0; color: #007BFF;">🎯 검색 결과</h2>
                <p style="margin: 0.5rem 0 0 0; color: #333333;">검색이 완료되었습니다. 아래에서 결과를 확인하세요.</p>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.search_just_executed = False
        
        # 검색 결과 헤더
        col1, col2 = st.columns([5, 1])
        
        with col1:
            search_params = st.session_state.get('search_params', {})
            query = search_params.get('query', '')
            start_dt = search_params.get('start_datetime', '')
            end_dt = search_params.get('end_datetime', '')
            
            st.markdown(f"""
            <div class="section-container">
                <h3 style="color: #007BFF; margin: 0 0 1rem 0;">🔍 검색 조건</h3>
                <div class="info-box">
                    <p style="margin: 0;"><strong>검색어:</strong> 
                    <span class="badge badge-primary">{query if query else '전체'}</span></p>
                    <p style="margin: 0.5rem 0 0 0;"><strong>기간:</strong> 
                    {start_dt.strftime('%Y-%m-%d %H:%M')} ~ {end_dt.strftime('%Y-%m-%d %H:%M')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("❌ 검색 닫기", key="close_search_results", type="secondary", use_container_width=True):
                st.session_state.show_search_results = False
                if 'current_page' in st.session_state:
                    del st.session_state.current_page
                st.rerun()
        
        # 검색 결과 처리
        results = st.session_state.get('search_results', [])
        
        if not results:
            st.markdown("""
            <div class="warning-card">
                <h3 style="color: #856404; margin: 0 0 1rem 0;">🔍 검색 결과가 없습니다</h3>
                <div style="color: #333333;">
                    <h4 style="color: #333333; margin: 0 0 0.5rem 0;">💡 검색 팁:</h4>
                    <ul style="line-height: 1.6; margin: 0;">
                        <li>검색어를 더 간단하게 입력해보세요</li>
                        <li>시간 범위를 넓혀보세요</li>
                        <li>검색어를 비우고 전체 검색을 해보세요</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 페이징 처리
            ITEMS_PER_PAGE = 10
            total_items = len(results)
            total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            
            if 'current_page' not in st.session_state:
                st.session_state.current_page = 1
            
            if st.session_state.current_page > total_pages:
                st.session_state.current_page = 1
            
            current_page = st.session_state.current_page
            start_idx = (current_page - 1) * ITEMS_PER_PAGE
            end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)
            current_results = results[start_idx:end_idx]
            
            # 검색 결과 요약
            st.markdown(f"""
            <div class="success-card">
                <h3 style="color: #155724; margin: 0;">📋 총 {total_items}개의 에러 로그 발견!</h3>
                <p style="color: #333333; margin: 0.5rem 0 0 0; font-weight: 600;">
                    현재 {current_page}/{total_pages} 페이지 ({start_idx + 1}~{end_idx}번째 결과)
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # 검색 결과 표시 - 테이블 형태로 변경
            st.markdown("### 📋 검색 결과 목록")
            
            # 현재 페이지 결과를 DataFrame으로 변환
            if current_results:
                # 테이블용 데이터 준비
                table_data = []
                for i, log in enumerate(current_results):
                    global_index = start_idx + i + 1
                    
                    # 메시지 미리보기 (50자로 제한)
                    message_preview = log['message'][:50] + ('...' if len(log['message']) > 50 else '')
                    
                    table_data.append({
                        '순번': global_index,
                        'ID': log['id'],
                        '발생시간': log['timestamp'],
                        '레벨': log['level'],
                        '에러 메시지': message_preview,
                        '응답시간(ms)': log['response_time'],
                        '상태': '분석 대기'
                    })
                
                # DataFrame 생성
                df = pd.DataFrame(table_data)
                
                # Streamlit 테이블로 표시 (선택 가능)
                st.data_editor(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        '순번': st.column_config.NumberColumn('순번', width='small'),
                        'ID': st.column_config.NumberColumn('ID', width='small'),
                        '발생시간': st.column_config.TextColumn('발생시간', width='medium'),
                        '레벨': st.column_config.TextColumn('레벨', width='small'),
                        '에러 메시지': st.column_config.TextColumn('에러 메시지', width='large'),
                        '응답시간(ms)': st.column_config.NumberColumn('응답시간(ms)', width='small'),
                        '상태': st.column_config.TextColumn('상태', width='small')
                    },
                    disabled=['순번', 'ID', '발생시간', '레벨', '에러 메시지', '응답시간(ms)', '상태'],
                    height=400
                )
                
                st.markdown("---")
                
                # 로그 선택 및 상세 보기 섹션
                st.markdown("### 🔍 로그 상세 정보 및 AI 분석")
                
                # 로그 선택용 selectbox
                log_options = [f"#{start_idx + i + 1} - ID {log['id']} - {log['level']} - {log['timestamp']}" for i, log in enumerate(current_results)]
                
                selected_log_idx = st.selectbox(
                    "분석할 로그를 선택하세요:",
                    options=range(len(log_options)),
                    format_func=lambda x: log_options[x],
                    key="selected_search_log"
                )
                
                if selected_log_idx is not None:
                    selected_log = current_results[selected_log_idx]
                    
                    # 선택된 로그 상세 정보를 3개 컬럼으로 분할
                    detail_col1, detail_col2, detail_col3 = st.columns([2, 1, 1])
                    
                    with detail_col1:
                        st.markdown("#### 📝 전체 에러 메시지")
                        st.code(selected_log['message'], language='text', wrap_lines=True)
                        
                        # 에러 키워드 분석
                        error_keywords = ['Exception', 'Error', 'Failed', 'Timeout', 'OutOfMemory', 'SQLException', 'NullPointer']
                        found_keywords = [keyword for keyword in error_keywords if keyword.lower() in selected_log['message'].lower()]
                        
                        if found_keywords:
                            st.markdown("#### 🏷️ 감지된 에러 키워드")
                            keyword_badges = " ".join([f'<span class="badge badge-error">{keyword}</span>' for keyword in found_keywords])
                            st.markdown(keyword_badges, unsafe_allow_html=True)
                    
                    with detail_col2:
                        st.markdown("#### 📊 로그 정보")
                        level_colors = {"ERROR": "#DC3545", "FATAL": "#6F42C1", "Exception": "#FD7E14"}
                        level_color = level_colors.get(selected_log['level'], "#6C757D")
                        response_color = "#DC3545" if selected_log['response_time'] > 3000 else "#FFC107" if selected_log['response_time'] > 1000 else "#28A745"
                        
                        st.markdown(f"""
                        <div class="section-container">
                            <div style="margin-bottom: 1rem;">
                                <strong>🆔 ID:</strong><br>
                                <span style="font-size: 1.2em; color: #007BFF;">{selected_log['id']}</span>
                            </div>
                            <div style="margin-bottom: 1rem;">
                                <strong>📊 레벨:</strong><br>
                                <span style="color: {level_color}; font-weight: bold; font-size: 1.1em;">{selected_log['level']}</span>
                            </div>
                            <div style="margin-bottom: 1rem;">
                                <strong>⏱️ 응답시간:</strong><br>
                                <span style="color: {response_color}; font-weight: bold; font-size: 1.1em;">{selected_log['response_time']}ms</span>
                            </div>
                            <div>
                                <strong>🕐 발생시간:</strong><br>
                                <small style="color: #6C757D;">{selected_log['timestamp']}</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with detail_col3:
                        st.markdown("#### 🤖 AI 분석 작업")
                        
                        # AI 분석 버튼
                        if st.button(
                            "🚀 AI 분석 실행",
                            key=f"analyze_selected_{selected_log['id']}",
                            type="primary",
                            use_container_width=True,
                            help="선택된 로그를 AI로 분석합니다"
                        ):
                            with st.spinner("🔍 AI가 로그를 분석 중입니다..."):
                                try:
                                    # ai_analyzer를 통한 분석 (내부적으로 LangChain 사용)
                                    analysis_result = ai_analyzer.analyze_error_log(selected_log['id'])
                                    st.session_state[f'analysis_result_{selected_log["id"]}'] = analysis_result
                                    st.session_state.selected_analysis_result = analysis_result
                                    st.session_state.show_analysis_popup = True
                                    st.session_state.auto_scroll_to_analysis = True  # 자동 스크롤 플래그
                                    st.success("✅ 분석 완료! 아래로 스크롤하여 결과를 확인하세요.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ 분석 실패: {e}")
                        
                        # 분석 결과 보기 버튼
                        if st.session_state.get(f'analysis_result_{selected_log["id"]}'):
                            st.success("✅ 분석 완료됨")
                            if st.button(
                                "📋 분석 결과 보기",
                                key=f"show_result_{selected_log['id']}",
                                use_container_width=True,
                                type="secondary"
                            ):
                                st.session_state.selected_analysis_result = st.session_state[f'analysis_result_{selected_log["id"]}']
                                st.session_state.show_analysis_popup = True
                                st.rerun()
                        
                        # 메인 화면에서 분석 버튼
                        if st.button(
                            "🔗 메인에서 분석",
                            key=f"main_analyze_{selected_log['id']}",
                            use_container_width=True,
                            help="메인 대시보드에서 이 로그를 분석합니다"
                        ):
                            st.session_state.selected_main_log_id = selected_log['id']
                            st.session_state.show_search_results = False
                            if 'current_page' in st.session_state:
                                del st.session_state.current_page
                            st.success(f"✅ ID {selected_log['id']} 로그를 메인 화면에서 선택했습니다!")
                            st.rerun()
            else:
                st.info("현재 페이지에 표시할 검색 결과가 없습니다.")
            
            # 개선된 페이지네이션 컨트롤
            if total_pages > 1:
                st.markdown("---")
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%);
                    border-radius: 12px;
                    border: 2px solid #DEE2E6;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    padding: 1.5rem 2rem;
                    margin: 2rem 0;
                ">
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4, col5 = st.columns([1.2, 1.2, 2, 1.2, 1.2])
                
                with col1:
                    if st.button("⏮️ 첫 페이지", key="first_page", disabled=(current_page == 1), use_container_width=True):
                        st.session_state.current_page = 1
                        st.rerun()
                
                with col2:
                    if st.button("◀️ 이전", key="prev_page", disabled=(current_page == 1), use_container_width=True):
                        st.session_state.current_page = max(1, current_page - 1)
                        st.rerun()
                
                with col3:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
                        border: 2px solid #007BFF;
                        border-radius: 10px;
                        padding: 1rem 1.5rem;
                        text-align: center;
                        color: #007BFF;
                        font-weight: 700;
                        font-size: 1.1rem;
                        box-shadow: 0 2px 8px rgba(0,123,255,0.15);
                        margin: 0 1rem;
                    ">
                        <div style="font-size: 1.3rem; color: #007BFF;">페이지 {current_page} / {total_pages}</div>
                        <div style="font-size: 0.85rem; color: #6C757D; margin-top: 0.3rem;">
                            총 {total_items}개 중 {start_idx + 1}-{end_idx}번째
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    if st.button("▶️ 다음", key="next_page", disabled=(current_page == total_pages), use_container_width=True):
                        st.session_state.current_page = min(total_pages, current_page + 1)
                        st.rerun()
                
                with col5:
                    if st.button("⏭️ 마지막", key="last_page", disabled=(current_page == total_pages), use_container_width=True):
                        st.session_state.current_page = total_pages
                        st.rerun()

def show_analysis_popup():
    """AI 분석 결과 팝업"""
    if st.session_state.get('show_analysis_popup', False):
        # 자동 스크롤 감지 - HTML 앵커 사용
        if st.session_state.get('auto_scroll_to_analysis', False):
            st.markdown("""
            <div id="analysis-result-section" style="scroll-margin-top: 100px;">
                <div style="
                    background: linear-gradient(135deg, #007BFF 0%, #0056b3 100%);
                    color: white;
                    padding: 1.5rem 2rem;
                    border-radius: 15px;
                    text-align: center;
                    margin: 2rem 0;
                    box-shadow: 0 8px 25px rgba(0,123,255,0.4);
                    border: 3px solid #fff;
                    animation: highlightPulse 2s ease-in-out;
                ">
                    <h2 style="margin: 0; color: white; font-size: 1.8em;">🎯 AI 분석 완료!</h2>
                    <p style="margin: 0.8rem 0 0 0; opacity: 0.95; font-size: 1.1em;">
                        상세한 분석 결과를 아래에서 확인하세요 ⬇️
                    </p>
                </div>
            </div>
            
            <style>
            @keyframes highlightPulse {
                0%, 100% { 
                    transform: scale(1); 
                    box-shadow: 0 8px 25px rgba(0,123,255,0.4);
                }
                50% { 
                    transform: scale(1.02); 
                    box-shadow: 0 12px 35px rgba(0,123,255,0.6);
                }
            }
            </style>
            """, unsafe_allow_html=True)
            
            # URL hash 기반 스크롤 (브라우저 네이티브 기능 사용)
            st.markdown("""
            <script>
                // 페이지 로드 후 즉시 스크롤
                window.location.hash = '#analysis-result-section';
                
                // 추가 보장을 위한 setTimeout
                setTimeout(function() {
                    const element = document.getElementById('analysis-result-section');
                    if (element) {
                        element.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }, 100);
                
                // 한 번 더 시도 (Streamlit 렌더링 완료 후)
                setTimeout(function() {
                    const element = document.getElementById('analysis-result-section');
                    if (element) {
                        const rect = element.getBoundingClientRect();
                        window.scrollTo({
                            top: window.pageYOffset + rect.top - 50,
                            behavior: 'smooth'
                        });
                    }
                }, 300);
            </script>
            """, unsafe_allow_html=True)
            
            # 플래그 리셋
            st.session_state.auto_scroll_to_analysis = False
        
        st.markdown("---")
        
        col1, col2 = st.columns([5, 1])
        
        with col1:
            st.markdown("## 🤖 AI 분석 결과")
        
        with col2:
            if st.button("❌ 닫기", key="close_analysis_popup", type="secondary"):
                st.session_state.show_analysis_popup = False
                st.rerun()
        
        analysis_text = st.session_state.get('selected_analysis_result', '')
        
        if "원인 분석:" in analysis_text and "해결 방안:" in analysis_text:
            parts = analysis_text.split("해결 방안:")
            cause_analysis = parts[0].replace("원인 분석:", "").strip()
            solution = parts[1].strip()
            
            # 원인 분석 섹션
            st.markdown(f"""
            <div class="section-container" style="border-left: 4px solid #FFC107;">
                <h4 style="color: #856404; margin-top: 0;">🔍 원인 분석</h4>
                <div style="color: #333333; line-height: 1.6;">{cause_analysis.replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 해결 방안 섹션
            st.markdown(f"""
            <div class="section-container" style="border-left: 4px solid #28A745;">
                <h4 style="color: #155724; margin-top: 0;">💡 해결 방안</h4>
                <div style="color: #333333; line-height: 1.6;">{solution.replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="section-container">
                <div style="color: #333333; line-height: 1.6;">{analysis_text.replace(chr(10), "<br>")}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 클립보드 복사 버튼
        create_copy_button_component("copy_popup_analysis", analysis_text, "분석 결과 복사")

def display_error_logs():
    """에러 로그 테이블 표시"""
    st.markdown("## 📋 최근 에러 로그")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🔄 새로고침", key="refresh_logs", type="secondary"):
            if 'log_current_page' in st.session_state:
                del st.session_state.log_current_page
            st.rerun()
    
    all_logs = db_manager.get_recent_logs(limit=100)
    
    if not all_logs:
        st.info("📝 표시할 에러 로그가 없습니다.")
        return
    
    # 페이징 설정
    LOGS_PER_PAGE = 15
    total_logs = len(all_logs)
    total_log_pages = (total_logs + LOGS_PER_PAGE - 1) // LOGS_PER_PAGE
    
    if 'log_current_page' not in st.session_state:
        st.session_state.log_current_page = 1
    
    current_log_page = st.session_state.log_current_page
    start_log_idx = (current_log_page - 1) * LOGS_PER_PAGE
    end_log_idx = min(start_log_idx + LOGS_PER_PAGE, total_logs)
    current_logs = all_logs[start_log_idx:end_log_idx]
    
    # 페이지 정보
    if total_log_pages > 1:
        st.markdown(f"""
        <div class="pagination-info">
            <strong>페이지 {current_log_page}/{total_log_pages}</strong> | 
            총 {total_logs}개 로그 중 {start_log_idx + 1}-{end_log_idx}번째 표시
        </div>
        """, unsafe_allow_html=True)
    
    # 데이터프레임 생성 및 표시
    df = pd.DataFrame(current_logs)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    display_df = df[['id', 'timestamp', 'level', 'message', 'response_time']].copy()
    display_df.columns = ['ID', '발생시간', '레벨', '에러 메시지', '응답시간(ms)']
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=400,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "발생시간": st.column_config.TextColumn("발생시간", width="medium"),
            "레벨": st.column_config.TextColumn("레벨", width="small"),
            "에러 메시지": st.column_config.TextColumn("에러 메시지", width="large"),
            "응답시간(ms)": st.column_config.NumberColumn("응답시간(ms)", width="small")
        }
    )
    
    # 개선된 로그 페이지네이션 컨트롤
    if total_log_pages > 1:
        st.markdown("---")
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%);
            border-radius: 12px;
            border: 2px solid #DEE2E6;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            padding: 1.5rem 2rem;
            margin: 2rem 0;
        ">
        </div>
        """, unsafe_allow_html=True)
        
        log_col1, log_col2, log_col3, log_col4, log_col5 = st.columns([1.2, 1.2, 2, 1.2, 1.2])
        
        with log_col1:
            if st.button("⏮️ 첫 페이지", key="log_first", disabled=(current_log_page == 1), use_container_width=True):
                st.session_state.log_current_page = 1
                st.rerun()
        
        with log_col2:
            if st.button("◀️ 이전", key="log_prev", disabled=(current_log_page == 1), use_container_width=True):
                st.session_state.log_current_page = max(1, current_log_page - 1)
                st.rerun()
        
        with log_col3:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
                border: 2px solid #007BFF;
                border-radius: 10px;
                padding: 1rem 1.5rem;
                text-align: center;
                color: #007BFF;
                font-weight: 700;
                font-size: 1.1rem;
                box-shadow: 0 2px 8px rgba(0,123,255,0.15);
                margin: 0 1rem;
            ">
                <div style="font-size: 1.3rem; color: #007BFF;">페이지 {current_log_page} / {total_log_pages}</div>
                <div style="font-size: 0.85rem; color: #6C757D; margin-top: 0.3rem;">
                    총 {total_logs}개 중 {start_log_idx + 1}-{end_log_idx}번째
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with log_col4:
            if st.button("▶️ 다음", key="log_next", disabled=(current_log_page == total_log_pages), use_container_width=True):
                st.session_state.log_current_page = min(total_log_pages, current_log_page + 1)
                st.rerun()
        
        with log_col5:
            if st.button("⏭️ 마지막", key="log_last", disabled=(current_log_page == total_log_pages), use_container_width=True):
                st.session_state.log_current_page = total_log_pages
                st.rerun()
    
    # AI 분석 섹션
    st.markdown("---")
    st.markdown("### 🤖 AI 분석")
    
    if len(current_logs) > 0:
        log_options = [f"ID {log['id']} - {log['level']} - {log['timestamp']}" for log in current_logs]
        
        selected_idx = st.selectbox(
            "분석할 로그를 선택하세요:",
            options=range(len(log_options)),
            format_func=lambda x: log_options[x],
            key="selected_log"
        )
        
        if selected_idx is not None:
            selected_log = current_logs[selected_idx]
            
            # 선택된 로그 정보 표시
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("**선택된 로그:**")
                st.code(selected_log['message'][:500] + ('...' if len(selected_log['message']) > 500 else ''), language='text')
            
            with col2:
                st.markdown("**로그 정보:**")
                st.markdown(f"""
                <div style="background: #F8F9FA; padding: 1rem; border-radius: 5px;">
                    <div><strong>ID:</strong> {selected_log['id']}</div>
                    <div><strong>레벨:</strong> {selected_log['level']}</div>
                    <div><strong>응답시간:</strong> {selected_log['response_time']}ms</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🚀 AI 분석 실행", key="analyze_main", type="primary", use_container_width=True):
                    with st.spinner("🔍 AI가 로그를 분석 중입니다..."):
                        # ai_analyzer를 통한 분석 (내부적으로 LangChain 사용)
                        analysis_result = ai_analyzer.analyze_error_log(selected_log['id'])
                        st.session_state.analysis_result = analysis_result
                        st.session_state.show_analysis = True
                        st.session_state.analyzed_log_id = selected_log['id']
                        st.session_state.auto_scroll_to_main_analysis = True  # 메인 분석 스크롤 플래그
                        st.success("✅ 분석 완료! 아래로 스크롤하여 결과를 확인하세요.")
                        st.rerun()
                
                if (st.session_state.get('analyzed_log_id') == selected_log['id'] and 
                    st.session_state.get('analysis_result')):
                    st.success("✅ 분석 완료!")
                    if st.button("📋 분석 결과 보기", key="show_main_result", type="secondary", use_container_width=True):
                        st.session_state.show_analysis = True
                        st.rerun()

def show_analysis_modal():
    """메인 AI 분석 결과 모달"""
    if st.session_state.get('show_analysis', False):
        # 메인 분석 자동 스크롤 처리
        if st.session_state.get('auto_scroll_to_main_analysis', False):
            st.markdown("""
            <div id="main-analysis-section" style="scroll-margin-top: 100px;">
                <div style="
                    background: linear-gradient(135deg, #28A745 0%, #20C997 100%);
                    color: white;
                    padding: 1.5rem 2rem;
                    border-radius: 15px;
                    text-align: center;
                    margin: 2rem 0;
                    box-shadow: 0 8px 25px rgba(40,167,69,0.4);
                    border: 3px solid #fff;
                    animation: successBounce 1s ease-out;
                ">
                    <h2 style="margin: 0; color: white; font-size: 1.8em;">✅ 메인 AI 분석 완료!</h2>
                    <p style="margin: 0.8rem 0 0 0; opacity: 0.95; font-size: 1.1em;">
                        아래에서 상세 분석 결과를 확인하세요 🚀
                    </p>
                </div>
            </div>
            
            <style>
            @keyframes successBounce {
                0% { 
                    transform: scale(0.8) translateY(-30px); 
                    opacity: 0; 
                }
                60% { 
                    transform: scale(1.05) translateY(5px); 
                    opacity: 0.9; 
                }
                100% { 
                    transform: scale(1) translateY(0); 
                    opacity: 1; 
                }
            }
            </style>
            """, unsafe_allow_html=True)
            
            # 메인 분석 스크롤
            st.markdown("""
            <script>
                // URL hash로 스크롤
                window.location.hash = '#main-analysis-section';
                
                // 추가 보장
                setTimeout(function() {
                    const element = document.getElementById('main-analysis-section');
                    if (element) {
                        element.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }, 100);
                
                // 최종 보장 (Streamlit 렌더링 완료 후)
                setTimeout(function() {
                    const element = document.getElementById('main-analysis-section');
                    if (element) {
                        const rect = element.getBoundingClientRect();
                        window.scrollTo({
                            top: window.pageYOffset + rect.top - 50,
                            behavior: 'smooth'
                        });
                    }
                }, 500);
            </script>
            """, unsafe_allow_html=True)
            
            # 플래그 리셋
            st.session_state.auto_scroll_to_main_analysis = False
        
        st.markdown("---")
        
        col1, col2 = st.columns([5, 1])
        
        with col1:
            st.markdown("## 🤖 AI 분석 결과")
        
        with col2:
            if st.button("❌ 닫기", key="close_main_analysis", type="secondary"):
                st.session_state.show_analysis = False
                st.rerun()
        
        analysis_text = st.session_state.analysis_result
        
        if "원인 분석:" in analysis_text and "해결 방안:" in analysis_text:
            parts = analysis_text.split("해결 방안:")
            cause_analysis = parts[0].replace("원인 분석:", "").strip()
            solution = parts[1].strip()
            
            st.markdown(f"""
            <div class="section-container" style="border-left: 4px solid #FFC107;">
                <h4 style="color: #856404; margin-top: 0;">🔍 원인 분석</h4>
                <div style="color: #333333; line-height: 1.6;">{cause_analysis.replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="section-container" style="border-left: 4px solid #28A745;">
                <h4 style="color: #155724; margin-top: 0;">💡 해결 방안</h4>
                <div style="color: #333333; line-height: 1.6;">{solution.replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="section-container">
                <div style="color: #333333; line-height: 1.6;">{analysis_text.replace(chr(10), "<br>")}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 클립보드 복사 버튼
        create_copy_button_component("copy_main_analysis", analysis_text, "분석 결과 복사")

def sidebar_filters():
    """사이드바 필터 구현"""
    st.sidebar.markdown("## 🔍 로그 검색")
    
    # 검색어 입력
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    
    search_query = st.sidebar.text_input(
        "검색어:",
        value=st.session_state.search_query,
        placeholder="에러 메시지 또는 키워드",
        key="search_input",
        help="에러 메시지에서 검색할 키워드를 입력하세요"
    )
    
    # 날짜 범위 설정
    st.sidebar.markdown("### 📅 검색 기간")
    
    # 기본값 설정
    if 'search_start_date' not in st.session_state:
        st.session_state.search_start_date = date.today() - timedelta(days=1)
    if 'search_end_date' not in st.session_state:
        st.session_state.search_end_date = date.today()
    if 'search_start_time' not in st.session_state:
        st.session_state.search_start_time = datetime.now().replace(hour=0, minute=0).time()
    if 'search_end_time' not in st.session_state:
        st.session_state.search_end_time = datetime.now().replace(hour=23, minute=59).time()
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        start_date = st.date_input("시작일", value=st.session_state.search_start_date)
        start_time = st.time_input("시작 시간", value=st.session_state.search_start_time)
    
    with col2:
        end_date = st.date_input("종료일", value=st.session_state.search_end_date)
        end_time = st.time_input("종료 시간", value=st.session_state.search_end_time)
    
    # 세션 상태 업데이트
    st.session_state.search_query = search_query
    st.session_state.search_start_date = start_date
    st.session_state.search_end_date = end_date
    st.session_state.search_start_time = start_time
    st.session_state.search_end_time = end_time
    
    # 검색 조건 미리보기
    st.sidebar.markdown("### 🔍 검색 조건")
    st.sidebar.markdown(f"""
    - **검색어:** {search_query if search_query else '전체'}
    - **기간:** {start_date} {start_time.strftime('%H:%M')} ~ {end_date} {end_time.strftime('%H:%M')}
    """)
    
    # 검색 실행
    if st.sidebar.button("🔍 검색 실행", type="primary", use_container_width=True):
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
        
        if start_datetime > end_datetime:
            st.sidebar.error("⚠️ 시작 시간이 종료 시간보다 늦습니다!")
            return
        
        with st.sidebar:
            with st.spinner("🔍 검색 중..."):
                search_results = perform_error_search(search_query, start_datetime, end_datetime)
        
        st.session_state.search_results = search_results
        st.session_state.show_search_results = True
        st.session_state.search_just_executed = True
        st.session_state.search_params = {
            'query': search_query,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime
        }
        
        if search_results:
            st.sidebar.success(f"✅ {len(search_results)}개 결과 발견!")
        else:
            st.sidebar.warning("⚠️ 검색 결과가 없습니다.")
        
        st.rerun()
    
    # 빠른 검색
    st.sidebar.markdown("### ⚡ 빠른 검색")
    quick_col1, quick_col2 = st.sidebar.columns(2)
    
    with quick_col1:
        if st.button("최근 1시간", use_container_width=True):
            now = datetime.now(KST)
            st.session_state.search_start_date = now.date()
            st.session_state.search_start_time = (now - timedelta(hours=1)).time()
            st.session_state.search_end_date = now.date()
            st.session_state.search_end_time = now.time()
            st.rerun()
    
    with quick_col2:
        if st.button("오늘", use_container_width=True):
            today = date.today()
            st.session_state.search_start_date = today
            st.session_state.search_start_time = datetime.now().replace(hour=0, minute=0).time()
            st.session_state.search_end_date = today
            st.session_state.search_end_time = datetime.now().replace(hour=23, minute=59).time()
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # 시스템 상태
    st.sidebar.markdown("### 📊 시스템 상태")
    
    # AI 설정 확인
    from backend.config import validate_azure_config
    is_valid, message = validate_azure_config()
    
    if is_valid:
        st.sidebar.markdown('<span class="status-online"></span>**LangChain + Azure OpenAI 연결됨**', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<span class="status-offline"></span>**Azure OpenAI 설정 필요**', unsafe_allow_html=True)
    
    st.sidebar.markdown('<span class="status-online"></span>**로그 모니터링 활성**', unsafe_allow_html=True)
    st.sidebar.markdown('<span class="status-online"></span>**샘플 로그 생성 중**', unsafe_allow_html=True)
    
    # 통계 정보
    recent_1hour_count, delta_text, delta_color = get_recent_errors_by_time(minutes=60)
    st.sidebar.markdown("### 📈 통계 (1시간)")
    st.sidebar.metric("에러 수", recent_1hour_count, delta=delta_text, delta_color=delta_color)
    
    # 현재 시간
    kst_now = datetime.now(KST)
    st.sidebar.markdown(f"**현재 시간:** {kst_now.strftime('%H:%M:%S')}")

def main():
    """메인 애플리케이션"""
    # 서비스 초기화
    initialize_services()
    
    # 앱 헤더
    create_app_header()
    
    # 사이드바 필터
    sidebar_filters()
    
    # 검색 결과가 있으면 최상단에 표시
    if st.session_state.get('show_search_results', False):
        show_search_results_popup()
        st.markdown("---")
    
    # 메인 대시보드 시작
    st.markdown("## 📊 모니터링 대시보드")
    
    # 메트릭 카드 섹션
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 최근 1시간 에러 수 (이전 1시간 대비)
        current_count, delta_text, delta_color = get_recent_errors_by_time(minutes=60)
        st.metric(
            label="📊 최근 1시간 에러 수",
            value=current_count,
            delta=delta_text,
            delta_color=delta_color,
            help="최근 1시간 내 발생한 에러 수 (이전 1시간 대비)"
        )
    
    with col2:
        # 기존 평균 응답시간 로직 (최근 20개 기준 유지)
        recent_logs = db_manager.get_recent_logs(limit=20)
        if recent_logs:
            avg_time = sum(log['response_time'] for log in recent_logs) / len(recent_logs)
            delta_color = "inverse" if avg_time > 2000 else "normal"
            st.metric(
                label="⏱️ 평균 응답시간",
                value=f"{avg_time:.1f}ms",
                delta=f"최근 20개 평균",
                delta_color=delta_color,
                help="최근 20개 에러의 평균 응답시간"
            )
        else:
            st.metric("⏱️ 평균 응답시간", "0ms", help="데이터 없음")
    
    with col3:
        kst_now = datetime.now(KST)
        st.metric(
            label="🕐 현재 시간 (KST)",
            value=kst_now.strftime("%H:%M:%S"),
            delta=kst_now.strftime("%Y-%m-%d"),
            help="한국 표준시 기준"
        )
    
    st.markdown("---")
    
    # 에러 통계 차트 (최근 1시간 기준, 10분 단위)
    create_realtime_error_chart()
    
    st.markdown("---")
    
    # 에러 로그 테이블 (전체 폭 사용)
    display_error_logs()
    
    # 팝업 모달들
    show_analysis_modal()
    show_analysis_popup()
    
    # 하단 고정 상태바
    kst_now = datetime.now(KST)
    st.markdown(f"""
    <div class="status-bar">
        <span class="status-online"></span>
        모니터링 중 | {kst_now.strftime('%H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()