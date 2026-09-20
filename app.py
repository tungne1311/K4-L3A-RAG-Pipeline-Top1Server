import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
import streamlit as st
from dotenv import load_dotenv
import time

# MOCK DATA CAO CẤP HƠN
def mock_generate_with_citation(query: str, top_k: int):
    time.sleep(1.2)
    if "thời tiết" in query.lower() or "paris" in query.lower():
        return {
            "answer": "⚠️ Tôi không thể xác minh thông tin này từ nguồn hiện có. Vui lòng chỉ hỏi các thông tin liên quan đến quy định và cẩm nang du lịch Đà Nẵng - Hội An.",
            "sources": [],
            "retrieval_source": "none"
        }
    
    retrieval_source = "hybrid" if "quy định" in query.lower() else "dense"
    
    return {
        "answer": f"Dựa trên dữ liệu hệ thống, đây là thông tin về: **{query}**.\n\nTheo quy định của thành phố, du khách cần tuân thủ các quy tắc an toàn và văn minh đô thị [1]. Đồng thời, bạn có thể trải nghiệm ẩm thực đặc sắc tại khu vực phố cổ [2]. Nếu cần hỗ trợ khẩn cấp, vui lòng liên hệ ban quản lý.",
        "sources": [
            {
                "id": "mock-chunk-1",
                "content": "Điều 3: Quy định an toàn bãi biển. Không tắm biển sau 19h00. Luôn mặc áo phao khi tham gia các hoạt động thể thao dưới nước. Tuân thủ hiệu lệnh của lực lượng cứu hộ.",
                "score": 0.9234,
                "retrieval_method": "dense",
                "metadata": {
                    "title": "Quy chế Quản lý Bãi biển Đà Nẵng 2026",
                    "source": "Quy_che_bai_bien_DN.pdf",
                    "url": "https://danang.gov.vn/quy-che"
                }
            },
            {
                "id": "mock-chunk-2",
                "content": "Phố cổ Hội An cấm xe gắn máy vào các khung giờ: 9h-11h và 15h-21h30 hàng ngày. Khuyến khích du khách đi bộ hoặc sử dụng xe đạp. Các điểm đỗ xe nằm ở rìa phố cổ.",
                "score": 0.8112,
                "retrieval_method": "bm25",
                "metadata": {
                    "title": "Cẩm nang giao thông Hội An",
                    "source": "camnang_giaothong_ha.json",
                    "url": "https://hoian.gov.vn/giaothong"
                }
            }
        ][:top_k],
        "retrieval_source": retrieval_source
    }

try:
    from src.task10_generation import generate_with_citation
except ImportError:
    generate_with_citation = mock_generate_with_citation

load_dotenv()

st.set_page_config(
    page_title="Vietnam Travel Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# INJECT ADVANCED CSS TẠO GIAO DIỆN HIỆN ĐẠI
st.markdown("""
<style>
    /* Global styling */
    .stApp {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header/Hero Section */
    .hero-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .hero-title { font-size: 2.5em; font-weight: 800; margin-bottom: 10px; }
    .hero-subtitle { font-size: 1.1em; opacity: 0.9; }

    /* Source Cards (Adaptive to Dark/Light mode) */
    .source-card {
        background: var(--secondary-background-color);
        border: 1px solid var(--border-color);
        border-left: 5px solid var(--primary-color);
        padding: 15px 20px;
        margin: 10px 0;
        border-radius: 8px;
        transition: transform 0.2s;
        color: var(--text-color);
    }
    .source-card:hover { transform: translateY(-3px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.75em;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-right: 8px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    /* Muted colors for badges so they look good on both dark and light */
    .badge-hybrid { background: rgba(25, 135, 84, 0.2); color: #28a745; border: 1px solid rgba(25, 135, 84, 0.3); }
    .badge-dense { background: rgba(13, 110, 253, 0.2); color: #4da3ff; border: 1px solid rgba(13, 110, 253, 0.3); }
    .badge-bm25 { background: rgba(255, 193, 7, 0.2); color: #ffc107; border: 1px solid rgba(255, 193, 7, 0.3); }
    .badge-pageindex { background: rgba(220, 53, 69, 0.2); color: #ff6b6b; border: 1px solid rgba(220, 53, 69, 0.3); }
    .badge-score { background: var(--background-color); color: var(--text-color); border: 1px solid var(--border-color); }
    
    /* Link styling */
    .source-link {
        color: var(--primary-color);
        text-decoration: none;
        font-weight: 600;
    }
    .source-link:hover { text-decoration: underline; }
    
    /* Text colors override for h4 inside source card */
    .source-card h4 { color: var(--text-color) !important; font-weight: bold; }
    .source-card em { color: var(--text-color) !important; opacity: 0.8; }
    
    /* Hide top padding */
    .block-container { padding-top: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# HERO BANNER
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🏖️ Trợ lý Du lịch Đà Nẵng - Hội An</div>
    <div class="hero-subtitle">Hệ thống hỏi đáp thông minh RAG (Retrieval-Augmented Generation) chống ảo giác AI.</div>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "👋 Xin chào! Tôi có thể giúp gì cho lịch trình du lịch Đà Nẵng - Hội An của bạn hôm nay?"}]

# SIDEBAR (Control Panel)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3284/3284614.png", width=80)
    st.title("Bảng Điều Khiển")
    
    st.markdown("---")
    st.subheader("Cài đặt Truy xuất")
    top_k = st.slider("Số lượng tài liệu (Top K)", min_value=1, max_value=8, value=3, help="Số lượng chunks văn bản AI dùng để làm ngữ cảnh.")
    
    st.markdown("---")
    st.subheader("Trạng thái Hệ thống")
    status = "🟢 Hoạt động (Real)" if generate_with_citation != mock_generate_with_citation else "🟡 Giả lập (Mock UI)"
    st.markdown(f"**Backend:** {status}")
    st.markdown("**LLM Engine:** GPT-4o-mini")
    st.markdown("**Vector DB:** ChromaDB")
    
    st.markdown("---")
    if st.button("🔄 Xóa hội thoại", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "👋 Xin chào! Tôi có thể giúp gì cho lịch trình du lịch Đà Nẵng - Hội An của bạn hôm nay?"}]
        st.rerun()

# MAIN CHAT AREA
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        if "sources" in message and message["sources"]:
            ret_src = message.get("retrieval_source", "unknown")
            with st.expander(f"🔎 Xem nguồn trích dẫn đính kèm ({len(message['sources'])} tài liệu)"):
                for idx, source in enumerate(message["sources"], 1):
                    meta = source.get("metadata", {})
                    method = source.get('retrieval_method', 'unknown')
                    badge = f"badge-{method}" if method in ['hybrid', 'dense', 'bm25', 'pageindex'] else ""
                    
                    st.markdown(f"""
                    <div class="source-card">
                        <h4 style="margin: 0 0 10px 0; color: #1e3c72;">[{idx}] {meta.get('title', 'N/A')}</h4>
                        <div style="margin-bottom: 12px;">
                            <span class="badge {badge}">{method}</span>
                            <span class="badge badge-score">Score: {source.get('score', 0):.3f}</span>
                        </div>
                        <div style="font-size: 0.95em; color: #555; margin-bottom: 10px;">
                            <em>"{source.get('content', '')}"</em>
                        </div>
                        <div style="font-size: 0.85em;">
                            📎 <strong>File gốc:</strong> {meta.get('source', 'N/A')} | 
                            🔗 <strong>URL:</strong> <a class="source-link" href="{meta.get('url', '#')}" target="_blank">Xem trên web</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

query = st.chat_input("Nhập câu hỏi (Ví dụ: Quy định tắm biển Đà Nẵng là gì?)...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Đang truy xuất CSDL và tổng hợp..."):
            try:
                try:
                    result = generate_with_citation(query, top_k=top_k)
                except NotImplementedError:
                    result = mock_generate_with_citation(query, top_k=top_k)
                    
                answer = result.get("answer")
                sources = result.get("sources", [])
                retrieval_source = result.get("retrieval_source")
                
                message_placeholder.markdown(answer)
                
                if sources:
                    with st.expander(f"🔎 Xem nguồn trích dẫn đính kèm ({len(sources)} tài liệu)"):
                        for idx, source in enumerate(sources, 1):
                            meta = source.get("metadata", {})
                            method = source.get('retrieval_method', 'unknown')
                            badge = f"badge-{method}" if method in ['hybrid', 'dense', 'bm25', 'pageindex'] else ""
                            
                            st.markdown(f"""
                            <div class="source-card">
                                <h4 style="margin: 0 0 10px 0; color: #1e3c72;">[{idx}] {meta.get('title', 'N/A')}</h4>
                                <div style="margin-bottom: 12px;">
                                    <span class="badge {badge}">{method}</span>
                                    <span class="badge badge-score">Score: {source.get('score', 0):.3f}</span>
                                </div>
                                <div style="font-size: 0.95em; color: #555; margin-bottom: 10px;">
                                    <em>"{source.get('content', '')}"</em>
                                </div>
                                <div style="font-size: 0.85em;">
                                    📎 <strong>File gốc:</strong> {meta.get('source', 'N/A')} | 
                                    🔗 <strong>URL:</strong> <a class="source-link" href="{meta.get('url', '#')}" target="_blank">Xem trên web</a>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.session_state.messages.append({
                    "role": "assistant", "content": answer,
                    "sources": sources, "retrieval_source": retrieval_source
                })
            except Exception as e:
                st.error(f"Lỗi: {e}")
