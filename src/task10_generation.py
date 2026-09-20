import os
from dotenv import load_dotenv
from openai import OpenAI
from .task9_retrieval_pipeline import retrieve

load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = """Bạn là trợ lý du lịch ảo chuyên về Đà Nẵng - Hội An.
Trả lời chỉ từ context được cung cấp.
Mỗi khẳng định phải có citation [1], [2],... tương ứng với số thứ tự trong context.
Nếu thiếu evidence, hãy trả lời chính xác câu này: "Tôi không thể xác minh thông tin này từ nguồn hiện có."
Không bịa đặt thông tin."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context để tránh lost-in-the-middle."""
    if len(chunks) <= 2:
        return list(chunks)
    # Sắp xếp theo pattern: Quan trọng nhất ở đầu và cuối (1, 3, 5, ..., 6, 4, 2)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk["metadata"]
        url = metadata.get("url") or "Không có"
        parts.append(
            f"[{index}] Tiêu đề: {metadata.get('title', 'N/A')} | "
            f"Nguồn: {metadata.get('source', 'N/A')} | URL: {url}\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình."""
    if LLM_PROVIDER.lower() == "openai":
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P
        )
        return response.choices[0].message.content
    else:
        raise NotImplementedError(f"Provider {LLM_PROVIDER} chưa được implement cho bài này.")


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult."""
    try:
        chunks = retrieve(query, top_k=top_k)
    except NotImplementedError:
        raise  # Bắn ngược lỗi nếu task 9 chưa làm để app.py bắt
    except Exception as e:
        # Fallback an toàn nếu retrieval pipeline gãy (vd lỗi mạng, pageindex sập...)
        return {
            "answer": f"Lỗi hệ thống khi tìm kiếm dữ liệu: {e}",
            "sources": [],
            "retrieval_source": "none"
        }

    if not chunks:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
            "sources": [],
            "retrieval_source": "none",
        }

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"
    
    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
    except Exception as e:
        return {
            "answer": f"Lỗi hệ thống khi gọi LLM: {e}",
            "sources": chunks,
            "retrieval_source": chunks[0]["retrieval_method"],
        }

    return {
        "answer": answer,
        "sources": chunks, # Giữ nguyên order gốc cho mảng sources trả về UI
        "retrieval_source": chunks[0]["retrieval_method"],
    }

if __name__ == "__main__":
    print(generate_with_citation("Đà nẵng có gì chơi?"))
