"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Chủ đề: Trợ Lý Nắm Bắt Tính Cách & Chọn Quà Tặng Phù Hợp
Nơi khai báo tất cả các "món đồ nghề" mà ReAct Agent có thể gọi.

📍 MỐC 1: Liệt kê tên các công cụ (Tool List)
1. analyze_personality  -> Suy ra nhóm sở thích/tính cách từ mô tả người nhận quà.
2. search_gift_catalog   -> Tra cứu danh sách quà phù hợp theo sở thích + ngân sách + dịp tặng.
3. get_occasion_tips     -> Gợi ý lưu ý/mẹo chọn quà theo dịp tặng cụ thể.

📍 MỐC 2: Tool Specs chuẩn hóa -> xem TOOL_SPECS ở cuối file (dùng để mô tả tool
cho REACT_SYSTEM_PROMPT ở Mốc 3, và để Role 5 tra cứu khi phân tích Trace Log).
"""

def analyze_personality(description: str) -> str:
    """
    Phân tích mô tả về người nhận quà để suy ra nhóm sở thích/tính cách chính.

    Args:
        description (str): Mô tả ngắn về người nhận (Ví dụ: 'thích công nghệ, hướng nội, hay đọc sách')

    Returns:
        str: Nhóm sở thích được suy ra ('công nghệ' | 'tri thức' | 'thể thao' | 'sáng tạo'),
             dùng làm tham số interest cho search_gift_catalog. Trả về chuỗi "LỖI: ..." nếu
             mô tả quá mơ hồ để suy luận.

    Ví dụ gọi (định dạng ReAct): analyze_personality['thích đọc sách, hướng nội']
    """
    desc_lower = description.lower()
    if "công nghệ" in desc_lower or "gadget" in desc_lower:
        return "công nghệ"
    elif "sách" in desc_lower or "đọc" in desc_lower:
        return "tri thức"
    elif "thể thao" in desc_lower or "gym" in desc_lower or "sức khỏe" in desc_lower:
        return "thể thao"
    elif "nghệ thuật" in desc_lower or "vẽ" in desc_lower or "sáng tạo" in desc_lower:
        return "sáng tạo"
    else:
        return f"LỖI: Không đủ dữ liệu để phân tích tính cách từ mô tả '{description}'."


def search_gift_catalog(interest: str, budget: int, occasion: str = "") -> str:
    """
    Tra cứu danh sách quà tặng phù hợp theo nhóm sở thích và ngân sách.

    Args:
        interest (str): Nhóm sở thích (Ví dụ: 'công nghệ', 'sáng tạo') - lấy từ analyze_personality
        budget (int): Ngân sách tối đa (VNĐ)
        occasion (str): Dịp tặng quà (Ví dụ: 'Sinh nhật', 'Valentine') - không bắt buộc

    Returns:
        str: Danh sách quà tặng gợi ý kèm giá, hoặc chuỗi "LỖI: ..." nếu không tìm được
             danh mục khớp hoặc không có quà nào trong ngân sách.

    Ví dụ gọi (định dạng ReAct): search_gift_catalog['công nghệ', 500000, 'Sinh nhật']
    """
    catalog = {
        "công nghệ": [("Tai nghe Bluetooth", 500000), ("Sạc dự phòng", 300000), ("Đồng hồ thông minh", 1500000)],
        "tri thức": [("Sách bán chạy", 150000), ("Voucher nhà sách", 200000), ("Máy đọc sách", 2500000)],
        "thể thao": [("Bình giữ nhiệt thể thao", 250000), ("Thảm tập yoga", 350000)],
        "sáng tạo": [("Bộ màu vẽ cao cấp", 400000), ("Khóa học vẽ online", 600000)],
    }
    options = catalog.get(interest.lower().strip())
    if not options:
        return f"LỖI: Không tìm thấy danh mục quà phù hợp với sở thích '{interest}'."
    matched = [f"{name} - {price:,} VNĐ" for name, price in options if price <= budget]
    if not matched:
        cheapest = min(options, key=lambda x: x[1])
        return (f"LỖI: Không có quà nào trong ngân sách {budget:,} VNĐ. "
                f"Quà rẻ nhất thuộc nhóm này là '{cheapest[0]}' giá {cheapest[1]:,} VNĐ.")
    return f"Gợi ý quà cho dịp {occasion or 'chung'}:\n" + "\n".join(matched)


def get_occasion_tips(occasion: str) -> str:
    """
    Gợi ý lưu ý/mẹo khi chọn quà theo dịp tặng cụ thể.

    Args:
        occasion (str): Dịp tặng quà (Ví dụ: 'Sinh nhật', 'Valentine', 'Kỷ niệm')

    Returns:
        str: Mẹo chọn quà phù hợp dịp, hoặc chuỗi "LỖI: ..." kèm danh sách dịp được hỗ trợ
             nếu dịp tặng không nằm trong danh sách.

    Ví dụ gọi (định dạng ReAct): get_occasion_tips['Sinh nhật']
    """
    tips = {
        "sinh nhật": "Nên ưu tiên món quà cá nhân hóa, gắn với sở thích riêng của người nhận.",
        "valentine": "Nên chọn quà mang tính lãng mạn, tinh tế hơn là thực dụng.",
        "kỷ niệm": "Nên chọn quà có giá trị lưu giữ lâu dài, tránh đồ dùng một lần.",
        "tốt nghiệp": "Nên chọn quà mang tính khích lệ cho chặng đường tiếp theo (sách, phụ kiện công sở).",
    }
    tip = tips.get(occasion.lower().strip())
    if not tip:
        return f"LỖI: Chưa có gợi ý cho dịp '{occasion}'. Các dịp hỗ trợ: {', '.join(tips.keys())}."
    return tip


# Danh sách các tool được đăng ký để Agent sử dụng
AVAILABLE_TOOLS = {
    "analyze_personality": analyze_personality,
    "search_gift_catalog": search_gift_catalog,
    "get_occasion_tips": get_occasion_tips,
}


# 📍 MỐC 2: TOOL SPECS CHUẨN HÓA (dùng để mô tả tool trong REACT_SYSTEM_PROMPT ở Mốc 3)
TOOL_SPECS = [
    {
        "name": "analyze_personality",
        "signature": "analyze_personality[description]",
        "description": "Suy ra nhóm sở thích chính của người nhận quà từ một đoạn mô tả tự do.",
        "params": {"description": "str - Mô tả ngắn về người nhận quà"},
        "example": "analyze_personality['thích đọc sách, hướng nội']",
    },
    {
        "name": "search_gift_catalog",
        "signature": "search_gift_catalog[interest, budget, occasion]",
        "description": "Tra cứu danh sách quà tặng phù hợp theo nhóm sở thích, ngân sách tối đa và dịp tặng.",
        "params": {
            "interest": "str - Nhóm sở thích, thường lấy từ kết quả analyze_personality",
            "budget": "int - Ngân sách tối đa (VNĐ)",
            "occasion": "str - Dịp tặng quà (không bắt buộc, có thể để trống)",
        },
        "example": "search_gift_catalog['công nghệ', 500000, 'Sinh nhật']",
    },
    {
        "name": "get_occasion_tips",
        "signature": "get_occasion_tips[occasion]",
        "description": "Gợi ý mẹo/lưu ý khi chọn quà theo một dịp tặng cụ thể.",
        "params": {"occasion": "str - Dịp tặng quà (Ví dụ: 'Sinh nhật', 'Valentine')"},
        "example": "get_occasion_tips['Sinh nhật']",
    },
]
