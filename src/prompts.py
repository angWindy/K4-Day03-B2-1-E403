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

# 📍 MỐC 2: Baseline Chatbot Prompt (Chỉ dùng LLM thông thường, KHÔNG có Tool)
# Mục đích: làm rõ giới hạn của Chatbot gốc khi không tra cứu được catalog quà thực tế,
# để so sánh với ReAct Agent ở Mốc 3.
CHATBOT_BASELINE_PROMPT = """Bạn là một Chatbot tư vấn chọn quà tặng thông thường.
Hãy trả lời câu hỏi tư vấn quà tặng của người dùng một cách thân thiện, dựa trên kiến thức
chung có sẵn của bạn về sở thích và các loại quà tặng phổ biến.

Bạn KHÔNG có khả năng tra cứu danh mục quà thực tế, KHÔNG biết giá cụ thể hiện tại,
và KHÔNG xác nhận được tồn kho/khuyến mãi. Nếu người dùng hỏi thông tin cụ thể như vậy
(VD: giá chính xác một món quà, quà có sẵn hay không), hãy lịch sự thông báo rằng bạn
chỉ có thể gợi ý chung chung và không có dữ liệu thực tế, thay vì bịa ra thông tin.
"""

# ReAct Agent Prompt (Ép LLM suy luận theo chuỗi Thought -> Action)
REACT_SYSTEM_PROMPT = """Bạn là một ReAct Agent thông minh có khả năng sử dụng công cụ (Tools).

Danh sách các công cụ bạn có thể sử dụng:
1. analyze_personality[description]: Suy ra nhóm sở thích chính của người nhận quà từ một đoạn mô tả tự do.
2. search_gift_catalog[interest, budget, occasion]: Tra cứu danh sách quà tặng phù hợp theo nhóm sở thích, ngân sách tối đa và dịp tặng.
3. get_occasion_tips[occasion]: Gợi ý mẹo/lưu ý khi chọn quà theo một dịp tặng cụ thể.

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
