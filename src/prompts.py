"""
🧠 PROMPTS & SAFEGUARDS (Dành cho Role 3: Prompt & Safeguard Engineer)
Chủ đề: Trợ Lý Nắm Bắt Tính Cách & Chọn Quà Tặng Phù Hợp
Nơi cấu hình System Prompt và Phanh An Toàn (Guardrails) cho AI.

📍 MỐC 1: Failure Modes (các trường hợp tool có thể bị lỗi/thất bại)
Ứng với 3 tool của Role 2 (analyze_personality, search_gift_catalog, get_occasion_tips):

1. analyze_personality:
   - Mô tả người nhận quá ngắn/mơ hồ (VD: "bình thường", "không biết") -> không đủ dữ liệu suy luận.
2. search_gift_catalog:
   - Sở thích suy ra không khớp danh mục nào trong catalog -> không tìm thấy quà.
   - Ngân sách quá thấp, không có quà nào phù hợp trong nhóm sở thích đó.
   - Ngân sách không hợp lệ (âm, bằng 0, hoặc không phải số).
3. get_occasion_tips:
   - Dịp tặng nằm ngoài danh sách hỗ trợ (VD: "Ngày tận thế", occasion bịa ra để bẫy).
4. Chung (cấp Agent):
   - Người dùng hỏi lạc đề, không liên quan đến chọn quà (test phạm vi/guardrail).
   - Agent lặp lại cùng một Action với tham số giống hệt mà không tiến triển -> cần MAX_ITERATIONS chặn (cấu hình ở Mốc 3).
"""

# Baseline Chatbot Prompt (Chỉ dùng LLM thông thường, không có Tool)
CHATBOT_BASELINE_PROMPT = """Bạn là một Chatbot tư vấn thông thường.
Hãy trả lời câu hỏi của người dùng một cách thân thiện dựa trên kiến thức có sẵn của bạn.
Nếu không biết thông tin thực tế thời gian thực, hãy lịch sự thông báo cho người dùng.
"""

# ReAct Agent Prompt (Ép LLM suy luận theo chuỗi Thought -> Action)
REACT_SYSTEM_PROMPT = """Bạn là một ReAct Agent thông minh có khả năng sử dụng công cụ (Tools).

Danh sách các công cụ bạn có thể sử dụng:
1. get_weather[location]: Tra cứu thời tiết hiện tại của một thành phố.
2. search_flights[origin, destination]: Tra cứu chuyến bay giữa 2 địa điểm.

QUY TẮC BẮT BUỘC: Khi trả lời, bạn PHẢI tuân theo định dạng từng dòng như sau:

Thought: Suy luận của bạn về bước tiếp theo cần làm.
Action: tên_công_cụ[tham_số]
(Sau đó dừng lại chờ hệ thống trả về kết quả Observation)

Khi đã có đủ thông tin để trả lời người dùng, hãy dùng định dạng:
Thought: Tôi đã có đủ thông tin để trả lời.
Final Answer: Câu trả lời hoàn chỉnh cuối cùng gửi cho người dùng.

BẮT ĐẦU:
"""

# 🛡️ GUARDRAILS CONFIGURATION (PHANH AN TOÀN)
MAX_ITERATIONS = 3  # Giới hạn tối đa 3 vòng lặp Thought-Action để tránh lặp vô tận
TIMEOUT_SECONDS = 10  # Timeout cho mỗi lần gọi tool
