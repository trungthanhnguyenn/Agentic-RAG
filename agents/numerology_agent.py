from pathlib import Path
import re
from typing import Dict, Any, List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from app.config import get_openai_llm
from tools.numerology_tool import CalNum, S3Client
from tools.data_validator_tool import DataValidator


def _read_prompt() -> str:
    base_dir = Path(__file__).resolve().parents[1]
    prompt_path = base_dir / "prompts" / "numerology_prompt.txt"
    return prompt_path.read_text(encoding="utf-8")


mapping_definition = {
    "life_path": """Chỉ số Đường đời là chỉ số cốt lõi chiếm 60% khả năng thành công của một trader. Đây là “chart gốc” thể hiện toàn diện cấu trúc tâm lý – chiến lược – động lực sống của bạn. Nó chỉ ra mục đích tồn tại, tố chất nổi trội, thử thách vận mệnh và bài học tối quan trọng mà bạn cần vượt qua để đạt "breakout" trong hành trình cuộc đời. Khi bạn giao dịch đúng “chiến lược cuộc đời” này, bạn sẽ đạt được tự do, thành công và hạnh phúc bền vững.""",
    "purpose": """Chỉ số Sứ mệnh cho biết vai trò và trách nhiệm lớn lao của bạn trên “sân chơi” tài chính. Khi hoàn thành sứ mệnh này, bạn sẽ đạt được lợi nhuận bền vững, sự tự do tài chính, và tạo ra giá trị to lớn cho cộng đồng trader cũng như thị trường.""",
    "soul": """Chỉ số Linh hồn tiết lộ **những khát khao sâu thẳm trong giao dịch.** Chỉ số này giúp bạn hiểu rõ động cơ đằng sau mỗi quyết định vào/thoát lệnh và cách bạn phản ứng trước biến động thị trường. Nhờ đó, bạn có thể lựa chọn phong cách trading, môi trường nhóm và cộng đồng phù hợp để duy trì năng lượng và cảm hứng khi giao dịch.""",
    "lifepath_life_purpose_link": """Chỉ số Liên kết Đường đời – Sứ mệnh cho bạn biết chiến lược hành động để hoàn tất “bài test” lớn nhất của cuộc đời và đạt được mục tiêu dài hạn.""",
    "balance": """Chỉ số Cân bằng tiết lộ cách bạn phản ứng khi thị trường biến động và áp lực giao dịch gia tăng. Từ đó giúp bạn điều chỉnh mindset để đưa ra quyết định lệnh chuẩn xác, tối ưu lợi nhuận và hạn chế rủi ro.""",
    "personality": """Chỉ số Nhân cách tiết lộ "ấn tượng đầu tiên" mà thị trường và cộng đồng trader cảm nhận về bạn. Chỉ số này mô tả tần số giao dịch và phong cách quản trị vốn mà bạn đang gửi ra bên ngoài.""",
    "soul_personality_link": """Chỉ số Liên kết Linh hồn – Nhân cách là **cầu nối giữa phong cách giao dịch nội tại và hình ảnh của bạn trong mắt cộng đồng trader.** Chỉ số này giúp bạn điều chỉnh cách thể hiện, từ đó tránh những hiểu nhầm về năng lực hoặc mục tiêu của mình.""",
    "attitude": """Chỉ số Thái độ mô tả cách bạn phản ứng và xử lý các tình huống trên thị trường mỗi ngày. Từ đó, bạn có thể lựa chọn trạng thái tâm lý phù hợp để nâng cấp kỹ năng giao dịch và đón nhận những cơ hội lợi nhuận tốt nhất.""",
    "maturity": """Chỉ số Trưởng thành cho bạn biết trong giai đoạn năng lượng cao nhất của sự nghiệp trading (thường là 30 – 40 tuổi), bạn nên tập trung vào chiến lược, kỹ năng và mindset nào để đạt đỉnh phong độ giao dịch.""",
    "milestone_1": """Giai đoạn đầu tiên đóng vai trò đặt nền móng cho cả sự nghiệp trading. Đây là khoảng thời gian bạn định hình tư duy giao dịch, rèn luyện kỷ luật bản thân và xây dựng nền tảng tâm lý để tồn tại lâu dài trên thị trường.""",
    "milestone_2": """Giai đoạn 2 đối với trader được xem là giai đoạn trưởng thành trong giao dịch – thời điểm bắt đầu có sự ổn định về chiến lược, tâm lý và quản lý vốn. Đây là lúc bạn nhận ra rõ rệt sự thay đổi trong cách đọc thị trường, kiểm soát cảm xúc và ra quyết định.""",
    "milestone_3": """Sau hai giai đoạn đầu tập trung xây dựng nền tảng kiến thức, kỷ luật và tư duy thị trường, giai đoạn 3 là lúc bạn tĩnh lặng quan sát thị trường và chính mình, nhận diện điểm mạnh – điểm yếu, từ đó định hình chiến lược giao dịch phù hợp cho chặng tiếp theo.""",
    "milestone_4": """Giai đoạn 4 trong sự nghiệp trading mang đến cho bạn những cơ hội và thử thách để vừa đóng góp cho cộng đồng trader (chia sẻ kinh nghiệm, mentor thế hệ mới), vừa tận hưởng thành quả giao dịch đã tích lũy. Để duy trì sự cân bằng và tiếp tục tăng trưởng lợi nhuận, bạn cần duy trì thói quen học tập, rèn luyện kỷ luật, và đi đúng hướng từ các giai đoạn trước.""",
    "challenge_1": """Các thách thức tương ứng cho giai đoạn 1""",
    "challenge_2": """Các thách thức tương ứng cho giai đoạn 2""",
    "challenge_3": """Các thách thức tương ứng cho giai đoạn 3""",
    "challenge_4": """Các thách thức tương ứng cho giai đoạn 4""",
    "personal_year": """Chỉ số năm cá nhân cho trader thêm góc nhìn về những biến động có thể xảy ra và những gì có thể kỳ vọng trong năm giao dịch sắp tới.""",
    "personal_month": """Chỉ số Tháng cá nhân cho trader cái nhìn về xu hướng năng lượng và cường độ cơ hội trong toàn bộ tháng. Nó giúp xác định giai đoạn nên tăng cường giao dịch, giai đoạn cần thận trọng hoặc thời điểm tập trung nhiều hơn vào việc phân tích và hoàn thiện chiến lược thay vì vào lệnh dồn dập.""",
    "personal_day": """Chỉ số Ngày cá nhân cho trader mang đến gợi ý về việc hôm nay bạn nên tập trung vào loại giao dịch hoặc hoạt động nào để tối đa hóa hiệu quả. """,
    "generation": """Chỉ số Thế hệ trong trading giúp bạn nhận biết những yêu cầu và kỳ vọng để hòa hợp với xu hướng thị trường và cộng đồng trader. Khi hiểu rõ mối liên kết giữa bản thân và môi trường giao dịch, bạn sẽ điều chỉnh hành vi để hạn chế rủi ro và tối ưu hiệu suất.""",
    "lession": """Chỉ số Bài học là chỉ số thể hiện những giai đoạn thị trường thử thách khắc nghiệt, đòi hỏi bạn phải có kỷ luật thép, khả năng kiểm soát cảm xúc và kiên trì tới cùng mới có thể vượt qua. Nếu vượt qua được, bạn sẽ trở thành một trader vững vàng, kiểm soát tốt rủi ro và tối ưu lợi nhuận bền vững.""",
    "passion": """Chỉ số Đam mê phản ánh phong cách giao dịch, thế mạnh riêng cũng như những hoạt động thị trường có thể mang lại cảm xúc hứng khởi cho bạn. Đây là chìa khóa giúp bạn duy trì tinh thần thép và năng lượng tích cực trong suốt hành trình rèn luyện và phát triển kỹ năng trading.""",
    "missing_arrow": """Là nhóm 3 số liên tiếp không xuất hiện trên biểu đồ ngày sinh, báo hiệu khoảng trống kỹ năng hoặc tư duy trong giao dịch. Nếu nhận biết và rèn luyện đúng cách, trader có thể biến điểm yếu thành lợi thế, nâng độ kỷ luật, kiểm soát cảm xúc và tối ưu chiến lược.""",
    "birth_day": """Chỉ số Ngày sinh được coi như một “món quà” mà thị trường trao cho bạn, hé lộ lợi thế cạnh tranh bẩm sinh cũng như khả năng phản ứng tự nhiên khi giao dịch. Từ chỉ số này, bạn sẽ hình dung được phong cách trading và điều kiện thị trường nào giúp bạn tối ưu hóa hiệu suất.""",
    "subconscious_strength": """Chỉ số Sức mạnh tiềm thức phản ánh kỹ năng và tư duy bạn cần phát triển để đạt lợi thế cạnh tranh trên thị trường, cũng như ứng phó hiệu quả với biến động và rủi ro giao dịch.""",
    "missing_aspects": """Chỉ số Thiếu cho thấy những kỹ năng và phẩm chất mà trader chưa có sẵn khi bước vào thị trường. Nhận diện được điều này sẽ giúp bạn rèn luyện và bổ sung để giao dịch hiệu quả hơn, giảm rủi ro và tối đa hóa lợi nhuận.""",
    "rational_thinking": """Tư duy lý trí là chỉ số phản ánh cách bạn phân tích thị trường và đưa ra quyết định giao dịch. Về cơ bản, chỉ số này nói lên nhiều điều về cách bạn xử lý thông tin và hành động trong những phiên thị trường biến động mạnh."""
}

# Enhanced keyword mapping based on question context and mapping_definition
KEYWORD_MAP: Dict[str, List[str]] = {
    # Core life indicators (always relevant)
    "đường đời": ["life_path"],
    "sứ mệnh": ["life_purpose"],
    "ngày sinh": ["birth_day"],
    
    # Personality & inner self
    "linh hồn": ["soul"],
    "nhân cách": ["personality"],
    "cân bằng": ["balance"],
    "đam mê": ["passion"],
    "tư duy": ["rational_thinking"],
    
    # Growth & development
    "trưởng thành": ["maturity"],
    "thử thách": ["challenge_1", "challenge_2", "challenge_3", "challenge_4"],
    "giai đoạn": ["milestone_1", "milestone_2", "milestone_3", "milestone_4"],
    "bài học": ["shadow_challenge_code"],
    
    # Personal timing
    "năm cá nhân": ["personal_year"],
    "tháng cá nhân": ["personal_month"],
    "ngày cá nhân": ["personal_day"],
    
    # Connections & insights
    "liên kết": ["lifepath_life_purpose_link", "soul_personality_link"],
    "thế hệ": ["societal_adaptability_index"],
    
    # Self-awareness
    "thiếu": ["missing_aspects"],
    "sức mạnh": ["subconscious_strength"],
}

# Context-based question analysis for intelligent indicator selection
CONTEXT_MAPPING = {
    # Trading performance issues
    "thua": ["life_path", "balance", "challenge_1", "challenge_2", "challenge_3", "challenge_4", "missing_aspects"],
    "lỗ": ["life_path", "balance", "challenge_1", "challenge_2", "challenge_3", "challenge_4", "missing_aspects"],
    "thất bại": ["life_path", "balance", "challenge_1", "challenge_2", "challenge_3", "challenge_4", "missing_aspects"],
    
    # Success & winning
    "thắng": ["life_path", "life_purpose", "passion", "maturity", "personal_year", "personal_day"],
    "hiệu quả": ["life_path", "life_purpose", "balance", "rational_thinking", "personal_year"],
    "thành công": ["life_path", "life_purpose", "maturity", "milestone_1", "milestone_2", "milestone_3", "milestone_4"],
    
    # Decision making
    "quyết định": ["balance", "rational_thinking", "personal_day", "life_path"],
    "nên": ["personal_day", "personal_month", "balance", "life_path"],
    "có nên": ["personal_day", "personal_month", "balance", "life_path"],
    
    # Emotional & psychological
    "tâm lý": ["soul", "personality", "balance", "emotional_response_style"],
    "cảm xúc": ["soul", "personality", "balance", "emotional_response_style"],
    "kiểm soát": ["balance", "rational_thinking", "maturity"],
    "buồn": ["soul", "personality", "balance", "emotional_response_style"],
    "vui": ["soul", "personality", "balance", "emotional_response_style"],
    "tự tin": ["soul", "personality", "balance", "emotional_response_style"],
    "thất vọng": ["soul", "personality", "balance", "emotional_response_style"],
    
    # Strategy & approach
    "chiến lược": ["life_path", "life_purpose", "maturity", "milestone_1", "milestone_2", "milestone_3", "milestone_4"],
    "phương pháp": ["life_path", "life_purpose", "balance", "rational_thinking"],
    "cách": ["life_path", "life_purpose", "balance", "rational_thinking"],
    
    # Risk & management
    "rủi ro": ["balance", "challenge_1", "challenge_2", "challenge_3", "challenge_4", "missing_aspects"],
    "chú ý": ["balance", "challenge_1", "challenge_2", "challenge_3", "challenge_4", "missing_aspects"],
    "quản lý": ["balance", "maturity", "rational_thinking"],
    
    # Motivation & purpose
    "động lực": ["life_purpose", "soul", "passion"],
    "mục tiêu": ["life_purpose", "maturity", "milestone_1", "milestone_2", "milestone_3", "milestone_4"],
    
    # Learning & improvement
    "học": ["missing_aspects", "subconscious_strength", "maturity"],
    "cải thiện": ["missing_aspects", "subconscious_strength", "challenge_1", "challenge_2", "challenge_3", "challenge_4"],
    "phát triển": ["maturity", "milestone_1", "milestone_2", "milestone_3", "milestone_4"],
}


def _extract_user_profile(question: str) -> Dict[str, str]:
    """Extract DOB and name if present in the question string.

    Supported patterns:
    - dob=dd/mm/yyyy or ngay_sinh=dd/mm/yyyy
    - name=... or ten=...
    """
    dob = None
    name = None

    dob_match = re.search(r"\b(?:dob|ngay_sinh)\s*[:=]\s*(\d{2}/\d{2}/\d{4})", question, flags=re.IGNORECASE)
    if dob_match:
        dob = dob_match.group(1)

    name_match = re.search(r"\b(?:name|ten)\s*[:=]\s*([^;\n]+)", question, flags=re.IGNORECASE)
    if name_match:
        name = name_match.group(1).strip()

    return {"dob": dob or "01/01/1990", "name": name or "Nguyen Van A"}


def _select_keys(question: str) -> List[str]:
    """
    Intelligently select relevant numerology indicators based on question context.
    Uses both explicit keywords and contextual analysis.
    """
    selected: List[str] = []
    q = question.lower()
    
    # Step 1: Check explicit keywords first
    for kw, keys in KEYWORD_MAP.items():
        if kw in q:
            selected.extend(keys)
    
    # Step 2: Analyze context for additional indicators
    for context_key, context_indicators in CONTEXT_MAPPING.items():
        if context_key in q:
            selected.extend(context_indicators)
    
    # Step 3: Always include core indicators (life_path and personal_day)
    if "life_path" not in selected:
        selected.append("life_path")
    if "personal_day" not in selected:
        selected.append("personal_day")
    
    # Step 4: Remove duplicates while preserving order
    seen = set()
    ordered_unique = []
    for k in selected:
        if k not in seen:
            seen.add(k)
            ordered_unique.append(k)
    
    # Step 5: Limit to reasonable number of indicators (max 8-10)
    if len(ordered_unique) > 10:
        # Prioritize core indicators and keep most relevant ones
        priority_indicators = ["life_path", "personal_day", "life_purpose", "balance"]
        final_selection = []
        
        # Add priority indicators first
        for indicator in priority_indicators:
            if indicator in ordered_unique:
                final_selection.append(indicator)
        
        # Add remaining indicators up to limit
        for indicator in ordered_unique:
            if indicator not in final_selection and len(final_selection) < 10:
                final_selection.append(indicator)
        
        return final_selection
    
    return ordered_unique


def _calculate_current_milestone_and_challenge(birthday: str, age_milestones: List[int], current_date: str = None) -> Dict[str, Any]:
    """
    Calculate which milestone the user is currently in based on their personal age_milestones.
    
    Args:
        birthday: User's date of birth in 'dd/mm/yyyy' format
        age_milestones: List of 4 milestone ages from CalNum calculation
        current_date: Current date in 'dd/mm/yyyy' format (defaults to today)
    
    Returns:
        Dict containing current milestone info and challenge
    """
    from datetime import datetime
    import pytz
    
    # Parse dates
    try:
        dob = datetime.strptime(birthday, '%d/%m/%Y')
        if current_date:
            current = datetime.strptime(current_date, '%d/%m/%Y')
        else:
            # Use current time in Vietnam timezone
            vntz = pytz.timezone("Asia/Ho_Chi_Minh")
            current = datetime.now(vntz)
        
        # Calculate current age
        age = current.year - dob.year
        if current.month < dob.month or (current.month == dob.month and current.day < dob.day):
            age -= 1
        
        # Determine current milestone based on personal age_milestones
        current_milestone = 1  # Default to first milestone
        milestone_name = "milestone_1"
        
        for i, milestone_age in enumerate(age_milestones, 1):
            if age >= milestone_age:
                current_milestone = i
                milestone_name = f"milestone_{i}"
            else:
                break
        
        # Get corresponding challenge
        challenge_name = f"challenge_{current_milestone}"
        
        # Get milestone age info
        current_milestone_age = age_milestones[current_milestone - 1] if current_milestone <= len(age_milestones) else age_milestones[-1]
        next_milestone_age = age_milestones[current_milestone] if current_milestone < len(age_milestones) else None
        
        return {
            "current_age": age,
            "current_milestone": current_milestone,
            "milestone_name": milestone_name,
            "challenge_name": challenge_name,
            "current_milestone_age": current_milestone_age,
            "next_milestone_age": next_milestone_age,
            "milestone_description": f"Bạn đang ở giai đoạn {current_milestone} (tuổi {age}/{current_milestone_age})",
            "challenge_description": f"Thách thức tương ứng với giai đoạn {current_milestone}",
            "age_milestones": age_milestones
        }
        
    except Exception as e:
        print(f"Error calculating milestone: {e}")
        return {
            "current_age": None,
            "current_milestone": 1,
            "milestone_name": "milestone_1",
            "challenge_name": "challenge_1",
            "current_milestone_age": age_milestones[0] if age_milestones else None,
            "next_milestone_age": age_milestones[1] if len(age_milestones) > 1 else None,
            "milestone_description": "Không thể xác định giai đoạn hiện tại",
            "challenge_description": "Thách thức tương ứng",
            "age_milestones": age_milestones
        }

def _prepare_data(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    question: str = input_dict["question"]
    user_name: Optional[str] = input_dict.get("user_name")
    birthday: Optional[str] = input_dict.get("birthday")
    current_day: Optional[str] = input_dict.get("current_day")
    
    # Use manual input if provided, otherwise fallback to parsing
    if user_name and birthday:
        profile = {"dob": birthday, "name": user_name}
    else:
        profile = _extract_user_profile(question)

    # Validate minimal profile
    DataValidator().validate_profile(profile.get("name"), profile.get("dob"))

    # Validate current_day: accept dd/mm/yyyy; if invalid/empty/None, let CalNum default to VN time
    def _normalize_current_day(day_str: Optional[str]) -> Optional[str]:
        if not day_str:
            return None
        s = str(day_str).strip()
        if not s:
            return None
        import re
        if re.fullmatch(r"\d{2}/\d{2}/\d{4}", s):
            return s
        return None

    normalized_current = _normalize_current_day(current_day)

    cal = CalNum(dob=profile["dob"], name=profile["name"], current_date=normalized_current)
    numbers = cal.get_personal_date_num()

    selected_keys = _select_keys(question)

    # Get age_milestones from CalNum calculation
    age_milestones = numbers.get("age_milestones", [])
    
    # Calculate current milestone and challenge based on user's personal age_milestones
    milestone_info = _calculate_current_milestone_and_challenge(profile["dob"], age_milestones)
    
    # If milestone or challenge indicators are selected, prioritize current ones
    milestone_indicators = [k for k in selected_keys if k.startswith("milestone_")]
    challenge_indicators = [k for k in selected_keys if k.startswith("challenge_")]
    
    if milestone_indicators or challenge_indicators:
        # Replace generic milestone/challenge with current ones
        for i, key in enumerate(selected_keys):
            if key.startswith("milestone_"):
                selected_keys[i] = milestone_info["milestone_name"]
            elif key.startswith("challenge_"):
                selected_keys[i] = milestone_info["challenge_name"]
        
        # Remove duplicates after replacement
        selected_keys = list(dict.fromkeys(selected_keys))

    # Fetch S3 docs for all selected indicators
    s3 = S3Client()
    docs: Dict[str, str] = {}

    # Map indicator keys to their corresponding number values and S3 types
    indicator_mapping = {
        "life_path": ("life_path", numbers.get("life_path")),
        "life_purpose": ("life_purpose", numbers.get("life_purpose")),
        "soul": ("soul", numbers.get("soul")),
        "personality": ("personality", numbers.get("personality")),
        "balance": ("balance", numbers.get("balance")),
        "maturity": ("maturity", numbers.get("maturity")),
        "passion": ("passion", numbers.get("passion")),
        "emotional_response_style": ("emotional_response_style", numbers.get("emotional_response_style")),
        "link_connection": ("link_connection", numbers.get("link_connection")),
        "challenge_1": ("challenge_1", numbers.get("challenge_1")),
        "challenge_2": ("challenge_2", numbers.get("challenge_2")),
        "challenge_3": ("challenge_3", numbers.get("challenge_3")),
        "challenge_4": ("challenge_4", numbers.get("challenge_4")),
        "milestone_1": ("milestone_1", numbers.get("milestone_phase", {}).get("milestone_1")),
        "milestone_2": ("milestone_2", numbers.get("milestone_phase", {}).get("milestone_2")),
        "milestone_3": ("milestone_3", numbers.get("milestone_phase", {}).get("milestone_3")),
        "milestone_4": ("milestone_4", numbers.get("milestone_phase", {}).get("milestone_4")),
        "rational_thinking": ("rational_thinking", numbers.get("rational_thinking")),
        "personal_day": ("personal_day", numbers.get("alignment_signals", {}).get("personal_day")),
        "personal_year": ("personal_year", numbers.get("alignment_signals", {}).get("personal_year")),
        "personal_month": ("personal_month", numbers.get("alignment_signals", {}).get("personal_month")),
    }

    # Prefetch S3 docs for current milestone/challenge so they are always available
    try:
        current_milestone_ord = int(milestone_info.get("current_milestone"))
        milestone_key = milestone_info.get("milestone_name")
        if milestone_key:
            milestone_val = numbers.get("milestone_phase", {}).get(milestone_key)
            if isinstance(milestone_val, int):
                try:
                    doc_content = s3.get_document_text_for_numerology(
                        "milestone", milestone_val, milestone_number=current_milestone_ord
                    )
                    if doc_content and not doc_content.startswith("Lỗi"):
                        docs[milestone_key] = doc_content
                except Exception:
                    pass
        challenge_key = milestone_info.get("challenge_name")
        if challenge_key:
            challenge_val = numbers.get("challenge", {}).get(challenge_key)
            if isinstance(challenge_val, int):
                try:
                    doc_content = s3.get_document_text_for_numerology(
                        "challenge", challenge_val, challenge_number=current_milestone_ord
                    )
                    if doc_content and not doc_content.startswith("Lỗi"):
                        docs[challenge_key] = doc_content
                except Exception:
                    pass
    except Exception:
        pass

    # Fetch documents for all selected keys
    print(f"�� Fetching documents for {len(selected_keys)} selected keys...")
    print(f"📅 Current milestone info: {milestone_info}")
    
    for key in selected_keys:
        print(f"  Processing key: {key}")
        
        # Special handling: milestone_X and challenge_X should fetch S3 docs by ordinal (1..4)
        if key.startswith("milestone_"):
            try:
                milestone_ord = int(key.split("_")[1])
                # File name expects milestone value (calculated), folder expects ordinal 1..4
                milestone_value = numbers.get("milestone_phase", {}).get(f"milestone_{milestone_ord}")
                if not isinstance(milestone_value, int):
                    docs[f"{key}_error"] = f"Invalid milestone value: {milestone_value}"
                    print(f"    ⚠️ Invalid milestone value: {milestone_value}")
                    continue
                try:
                    doc_content = s3.get_document_text_for_numerology(
                        "milestone",
                        milestone_value,
                        milestone_number=milestone_ord,
                    )
                    if doc_content:
                        docs[key] = doc_content
                        print(f"    ✅ Milestone doc fetched: {len(str(doc_content))} chars")
                    else:
                        docs[f"{key}_error"] = "Empty content"
                        print(f"    ⚠️ Milestone doc fetch returned empty content")
                except Exception as e:
                    docs[f"{key}_error"] = str(e)
                    print(f"    ❌ Milestone doc exception: {e}")
                continue
            except Exception as e:
                print(f"    ⚠️ Invalid milestone key '{key}': {e}")

        if key.startswith("challenge_"):
            try:
                challenge_ord = int(key.split("_")[1])
                # File name expects challenge value (calculated), folder expects ordinal 1..4
                challenge_value = numbers.get("challenge", {}).get(f"challenge_{challenge_ord}")
                if not isinstance(challenge_value, int):
                    docs[f"{key}_error"] = f"Invalid challenge value: {challenge_value}"
                    print(f"    ⚠️ Invalid challenge value: {challenge_value}")
                    continue
                try:
                    doc_content = s3.get_document_text_for_numerology(
                        "challenge",
                        challenge_value,
                        challenge_number=challenge_ord,
                    )
                    if doc_content:
                        docs[key] = doc_content
                        print(f"    ✅ Challenge doc fetched: {len(str(doc_content))} chars")
                    else:
                        docs[f"{key}_error"] = "Empty content"
                        print(f"    ⚠️ Challenge doc fetch returned empty content")
                except Exception as e:
                    docs[f"{key}_error"] = str(e)
                    print(f"    ❌ Challenge doc exception: {e}")
                continue
            except Exception as e:
                print(f"    ⚠️ Invalid challenge key '{key}': {e}")

        if key in indicator_mapping:
            s3_type, number_value = indicator_mapping[key]
            print(f"    S3 type: {s3_type}, number value: {number_value}")
            
            if isinstance(number_value, int):
                try:
                    doc_content = s3.get_document_text_for_numerology(s3_type, number_value)
                    if doc_content and not doc_content.startswith("Lỗi"):
                        docs[key] = doc_content
                        print(f"    ✅ Document fetched: {len(doc_content)} chars")
                    else:
                        docs[f"{key}_error"] = doc_content
                        print(f"    ⚠️ Document fetch failed: {doc_content}")
                except Exception as e:
                    docs[f"{key}_error"] = str(e)
                    print(f"    ❌ Exception: {e}")
            else:
                docs[f"{key}_error"] = f"Invalid number value: {number_value}"
                print(f"    ⚠️ Invalid number value: {number_value}")
        else:
            # For indicators not in S3 mapping, use the calculated values and meanings
            print(f"    Using calculated value for: {key}")
            
            if key in numbers:
                if key not in docs:
                    docs[key] = f"Giá trị: {numbers[key]}"
            elif key == milestone_info["milestone_name"]:
                # Current milestone with age context
                if key not in docs:
                    milestone_value = numbers.get("milestone_phase", {}).get(f"milestone_{milestone_info['current_milestone']}")
                    docs[key] = f"{milestone_info['milestone_description']} - Giá trị: {milestone_value}"
            elif key == milestone_info["challenge_name"]:
                # Current challenge with age context
                if key not in docs:
                    challenge_value = numbers.get("challenge", {}).get(f"challenge_{milestone_info['current_milestone']}")
                    docs[key] = f"{milestone_info['challenge_description']} - Giá trị: {challenge_value}"
            elif key.startswith("challenge_"):
                challenge_num = key.split("_")[1]
                challenge_value = numbers.get("challenge", {}).get(f"challenge_{challenge_num}")
                if challenge_value is not None and key not in docs:
                    docs[key] = f"Thách thức {challenge_num}: {challenge_value}"
            elif key.startswith("milestone_"):
                milestone_num = key.split("_")[1]
                milestone_value = numbers.get("milestone_phase", {}).get(f"milestone_{milestone_num}")
                if milestone_value is not None and key not in docs:
                    docs[key] = f"Giai đoạn {milestone_num}: {milestone_value}"
            else:
                if key not in docs:
                    docs[key] = f"Giá trị: {numbers.get(key, 'N/A')}"

    # Provide mapping meanings for selected keys
    meanings: Dict[str, str] = {}
    for k in selected_keys:
        if k in mapping_definition:
            meanings[k] = mapping_definition[k]

    # Return both structured payload and text resources
    return {
        "question": question,
        "profile": profile,
        "selected_keys": selected_keys,
        "numbers": numbers,
        "docs": docs,
        "meanings": meanings,
        "milestone_info": milestone_info,  # Add milestone context
    }


def build_numerology_agent():
    prepare = RunnableLambda(_prepare_data)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            _read_prompt() + "\n\nBạn luôn ưu tiên hai thư mục: Đường đời (life_path) và Ngày cá nhân (personal_day).\nTận dụng dữ liệu 'numbers', 'meanings' và 'docs' để trả lời ngắn gọn, thực tiễn cho trader.",
        ),
        (
            "human",
            (
                "Câu hỏi: {question}\n\n"
                "Khoá chọn: {selected_keys}\n\n"
                "Số liệu: {numbers}\n\n"
                "Ý nghĩa: {meanings}\n\n"
                "Tài liệu: {docs}\n"
            ),
        ),
    ])

    llm = get_openai_llm()
    chain = (
        prepare | prompt | llm | StrOutputParser()
    )
    return chain
