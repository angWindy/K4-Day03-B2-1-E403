"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import ast
import inspect
import json
import os
import re
import sys
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

# Nhận diện dòng "Action: tên_công_cụ[tham_số]" và "Final Answer: ..." theo đúng
# định dạng bắt buộc trong REACT_SYSTEM_PROMPT (src/prompts.py)
ACTION_PATTERN = re.compile(r"Action:\s*(\w+)\[(.*)\]")
FINAL_ANSWER_PATTERN = re.compile(r"Final Answer:\s*(.+)", re.DOTALL)


def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")

    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}")

    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")


def _coerce_scalar(token: str):
    """Chuyển 1 token text thành str/int/float, bỏ dấu nháy bao quanh nếu có."""
    token = token.strip()
    if len(token) >= 2 and token[0] == token[-1] and token[0] in ("'", '"'):
        return token[1:-1]
    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        pass
    return token


def parse_tool_call(model_output: str):
    """
    Tách dòng 'Action: tên_công_cụ[tham_số]' trong phản hồi của LLM thành
    (tool_name, args_tuple). Trả về None nếu không tìm thấy Action hợp lệ,
    hoặc (tool_name, None) nếu tìm thấy Action nhưng tham số không parse được.
    """
    match = ACTION_PATTERN.search(model_output)
    if not match:
        return None

    tool_name, raw_args = match.group(1), match.group(2).strip()
    if not raw_args:
        return tool_name, ()

    try:
        # Bọc thành tuple literal để dùng ast.literal_eval parse an toàn
        # (không exec code tùy ý), hỗ trợ đúng chuẩn khi LLM có đặt dấu nháy.
        return tool_name, ast.literal_eval(f"({raw_args},)")
    except (ValueError, SyntaxError):
        pass

    # Fallback: LLM không đặt dấu nháy quanh chuỗi (VD: Action: get_occasion_tips[Kỷ niệm]).
    # Chỉ tách theo dấu phẩy khi số phần tử khớp đúng số tham số của tool, để tránh cắt
    # nhầm câu mô tả tự do (1 tham số) có chứa dấu phẩy bên trong.
    tool_func = AVAILABLE_TOOLS.get(tool_name)
    expected_arity = len(inspect.signature(tool_func).parameters) if tool_func else None
    parts = [p.strip() for p in raw_args.split(",")]
    if expected_arity is not None and expected_arity > 1 and len(parts) == expected_arity:
        return tool_name, tuple(_coerce_scalar(p) for p in parts)
    return tool_name, (raw_args.strip("'\" "),)


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) có Guardrails.
    Mỗi vòng lặp gọi LLM Provider thực sự (theo REACT_SYSTEM_PROMPT), tự parse
    Action mà LLM sinh ra, thực thi tool tương ứng trong AVAILABLE_TOOLS rồi đưa
    Observation trở lại cho LLM ở vòng tiếp theo.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    scratchpad = ""
    step = 0

    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")

        prompt = f"Câu hỏi của người dùng: {user_query}\n{scratchpad}"
        response = provider.generate(prompt, system_prompt=REACT_SYSTEM_PROMPT).strip()
        print(response)

        final_match = FINAL_ANSWER_PATTERN.search(response)
        if final_match:
            print(f"\n🏁 Final Answer: {final_match.group(1).strip()}")
            return

        parsed = parse_tool_call(response)
        if parsed is None:
            print("🛡️ GUARDRAIL: Phản hồi không đúng định dạng Thought/Action/Final Answer. Dừng an toàn.")
            return

        tool_name, args = parsed
        tool_func = AVAILABLE_TOOLS.get(tool_name)
        if tool_func is None:
            obs = f"LỖI: Tool '{tool_name}' không tồn tại trong AVAILABLE_TOOLS."
        elif args is None:
            obs = f"LỖI: Không parse được tham số cho Action '{tool_name}'."
        else:
            try:
                obs = tool_func(*args)
            except Exception as e:
                obs = f"LỖI: Tool '{tool_name}' gặp lỗi khi thực thi - {e}"

        print(f"👁️ Observation: {obs}")
        scratchpad += f"\n{response}\nObservation: {obs}\n"

    print(
        f"🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa "
        f"{MAX_ITERATIONS} bước. Ngắt lặp an toàn!"
    )


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("==================================================")

    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(
        f"🔌 LLM Provider đang hoạt động: "
        f"{provider.__class__.__name__} (Model: {model_name})"
    )

    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")

    # Chạy lần lượt toàn bộ test cases
    for index, test_case in enumerate(tests, start=1):
        sample_query = test_case.get("question", test_case.get("input", ""))

        print(f"\n================== TEST CASE {index} ==================")

        print("--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
        run_baseline_chatbot(sample_query, provider)

        print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
        run_react_agent(sample_query, provider)