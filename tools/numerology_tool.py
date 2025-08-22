# tools/numerology_tool.py
"""
Personal Numerology Calculator

This module implements comprehensive numerology calculations based on
Vietnamese numerology principles including master numbers (11, 22, 33).
"""

from datetime import datetime
from typing import Dict, List, Set, Tuple, Union
import pytz
from dotenv import load_dotenv
import os
import boto3
from botocore.client import Config
from docx import Document
from io import BytesIO


load_dotenv()

class S3Client:
    def __init__(self):
        self.s3 = boto3.client('s3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION'),
            endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
            config=Config(s3={"addressing_style": "virtual"})
        )
        self.bucket_name = os.getenv('BUCKET_NAME')

    def get_document_text_for_numerology(self, number_type: str, number: int, milestone_number: int = None, challenge_number: int = None) -> str:
        """
        Tải file từ S3 dựa trên loại số và giá trị số.

        Args:
            number_type (str): Loại số, ví dụ 'life_path', 'personal_day', 'personal_year', etc.
            number (int): Giá trị số.

        Returns:
            str: Nội dung văn bản của tài liệu.
        """
        # Map number types to folder and file naming conventions
        # Based on actual bucket structure: numerology_trader/{folder}/{file}
        base_folder = "numerology_trader"
        
        if number_type == "personal_year":
            folder = f"{base_folder}/nam_ca_nhan"
            file_name = f"nam_ca_nhan_{number}.docx"
        elif number_type == "personal_day":
            folder = f"{base_folder}/ngay_ca_nhan"
            file_name = f"ngay_ca_nhan_{number}.docx"
        elif number_type == "personal_month":
            folder = f"{base_folder}/thang_ca_nhan"
            file_name = f"thang_ca_nhan_{number}.docx"
        elif number_type == "life_path":
            folder = f"{base_folder}/duong_doi"
            file_name = f"duong_doi_{number}.docx"
        elif number_type == "life_purpose":
            folder = f"{base_folder}/su_menh"
            file_name = f"su_menh_{number}.docx"
        elif number_type == "soul":
            folder = f"{base_folder}/linh_hon"
            file_name = f"linh_hon_{number}.docx"
        elif number_type == "personality":
            folder = f"{base_folder}/nhan_cach"
            file_name = f"nhan_cach_{number}.docx"
        elif number_type == "balance":
            folder = f"{base_folder}/can_bang"
            file_name = f"can_bang_{number}.docx"
        elif number_type == "maturity":
            folder = f"{base_folder}/truong_thanh"
            file_name = f"truong_thanh_{number}.docx"
        elif number_type == "passion":
            folder = f"{base_folder}/dam_me"
            file_name = f"dam_me_{number}.docx"
        elif number_type == "rational_thinking":
            folder = f"{base_folder}/tu_duy_ly_tri"
            file_name = f"tu_duy_ly_tri_{number}.docx"
        elif number_type in ("milestone", "giai_doan"):
            # Milestone documents are indexed by milestone order (1..4)
            folder = f"{base_folder}/giai_doan_{milestone_number}"
            file_name = f"chang_{number}.docx"
        elif number_type in ("challenge", "thu_thach"):
            # Challenge documents are indexed by challenge order (1..4)
            folder = f"{base_folder}/thach_thuc_giai_doan_{challenge_number}"
            file_name = f"thach_thuc_{number}.docx"
        else:
            # For unsupported types, return a placeholder
            return f"Tài liệu cho {number_type} với giá trị {number} chưa có sẵn."

        file_key = f"{folder}/{file_name}"
        print(f"[S3 Numerology] Fetching: bucket={self.bucket_name}, key={file_key}")

        if self.s3 is None:
            raise ValueError("S3 client không được khởi tạo.")

        try:
            # print(f"🔍 Attempting to fetch: {file_key} from bucket: {self.bucket_name}")
            
            # Check if bucket exists and is accessible
            try:
                self.s3.head_bucket(Bucket=self.bucket_name)
                print(f"✅ Bucket {self.bucket_name} is accessible")
            except Exception as bucket_error:
                print(f"⚠️ Bucket access issue: {bucket_error}")
                return f"Không thể truy cập bucket {self.bucket_name}: {bucket_error}"
            
            # Try to get the object
            try:
                obj = self.s3.get_object(Bucket=self.bucket_name, Key=file_key)
                # print(f"✅ Object retrieved successfully")
                
                # Check if Body exists and is readable
                if "Body" not in obj:
                    print(f"⚠️ No Body in S3 response: {obj.keys()}")
                    return f"Response không có Body: {list(obj.keys())}"
                
                body = obj["Body"]
                if body is None:
                    print(f"⚠️ Body is None")
                    return f"Body của response là None"
                
                # Read the content
                try:
                    file_content = body.read()
                    # print(f"✅ File content read: {len(file_content)} bytes")
                except Exception as read_error:
                    print(f"⚠️ Error reading body: {read_error}")
                    return f"Lỗi đọc body: {read_error}"
                
                # Check if content is valid
                if not file_content:
                    print(f"⚠️ File content is empty")
                    return f"File content rỗng"
                
                # Try to parse as document
                try:
                    doc = Document(BytesIO(file_content))
                    # print(f"✅ Document parsed successfully")
                    
                    # Extract text
                    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
                    if not paragraphs:
                        print(f"⚠️ No text content in document")
                        return f"Document không có nội dung text"
                    
                    text = "\n".join(paragraphs)
                    # print(f"✅ Text extracted: {len(text)} characters")
                    return text
                    
                except Exception as doc_error:
                    print(f"⚠️ Error parsing document: {doc_error}")
                    return f"Lỗi parse document: {doc_error}"
                    
            except Exception as obj_error:
                print(f"⚠️ Error getting object: {obj_error}")
                return f"Lỗi lấy object: {obj_error}"
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return f"Lỗi không mong đợi: {str(e)}"


class CalNum:
    """
    Personal Numerology Calculator implementing Vietnamese numerology principles.

    Supports calculation of life path, soul number, personality number,
    and other key numerological indicators.
    """

    # Vietnamese alphabet mapping (A=1, B=2, ..., I=9, J=1, ...)
    ALPHABET = {
        # Basic letters
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
        'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,

        # Vietnamese vowels with diacritics
        'Ă': 1, 'Â': 1, 'Ê': 5, 'Ô': 6, 'Ơ': 6,

        # Vietnamese consonants with diacritics
        'Đ': 4,

        # Vowels with tone marks
        'Á': 1, 'À': 1, 'Ả': 1, 'Ã': 1, 'Ạ': 1,
        'Ắ': 1, 'Ằ': 1, 'Ẳ': 1, 'Ẵ': 1, 'Ặ': 1,
        'Ấ': 1, 'Ầ': 1, 'Ẩ': 1, 'Ẫ': 1, 'Ậ': 1,
        'É': 5, 'È': 5, 'Ẻ': 5, 'Ẽ': 5, 'Ẹ': 5,
        'Ế': 5, 'Ề': 5, 'Ể': 5, 'Ễ': 5, 'Ệ': 5,
        'Í': 9, 'Ì': 9, 'Ỉ': 9, 'Ĩ': 9, 'Ị': 9,
        'Ó': 6, 'Ò': 6, 'Ỏ': 6, 'Õ': 6, 'Ọ': 6,
        'Ố': 6, 'Ồ': 6, 'Ổ': 6, 'Ỗ': 6, 'Ộ': 6,
        'Ớ': 6, 'Ờ': 6, 'Ở': 6, 'Ỡ': 6, 'Ợ': 6,

        # U and its variants (considered separately)
        'Ú': 3, 'Ù': 3, 'Ủ': 3, 'Ũ': 3, 'Ụ': 3,
        'Ư': 3, 'Ứ': 3, 'Ừ': 3, 'Ử': 3, 'Ữ': 3, 'Ự': 3,

        # Y variants
        'Ý': 7, 'Ỳ': 7, 'Ỷ': 7, 'Ỹ': 7, 'Ỵ': 7
    }

    # Master numbers
    MASTER_NUMBERS = {11, 22, 33}

    # Karmic debt numbers
    KARMIC_NUMBERS = {13, 14, 16, 19}

    def __init__(self, dob: str, name: str, current_date: str = None):
        """
        Initialize calculator with date of birth, current date, and full name.

        Args:
            dob: Date of birth in 'dd/mm/yyyy' format
            current_date: Current date in 'dd/mm/yyyy' format
            name: Full name (first, middle, last names)
        """
        self.dob = dob
        self.current_date = current_date
        self.name = name.strip()

        # Parse dates
        self.dob_date = self._parse_date(dob, "date of birth")
        # self.current_datetime = self._parse_date(current_date, "current date")

        if self.current_date is None:
            # If no current date, use current time in Vietnam timezone
            vntz = pytz.timezone("Asia/Ho_Chi_Minh")
            self.current_datetime = datetime.now(vntz)
        else:
            self.current_datetime = self._parse_date(self.current_date, "current date")

        # Calculate name numbers
        self.name_numbers = self._name_to_numbers()

        # Parse date components
        self.day = self.dob_date.day
        self.month = self.dob_date.month
        self.year = self.dob_date.year

        # Calculate reduced date components
        self.day_r = self.reduce_number_with_masters(self.day)
        self.month_r = self.reduce_number_with_masters(self.month)
        self.year_r = self.reduce_number_with_masters(self.year)

        # Calculate date no master
        self.day_r_no_master = self.reduce_number_no_master(self.day)
        self.month_r_no_master = self.reduce_number_no_master(self.month)
        self.year_r_no_master = self.reduce_number_no_master(self.year)

    def _parse_date(self, date_str: str, date_type: str) -> datetime:
        """Parse date string to datetime object."""
        try:
            return datetime.strptime(date_str, '%d/%m/%Y')
        except ValueError:
            if date_type == "current date":
                # Use current time if current date is invalid
                vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
                return datetime.now(vn_timezone)
            else:
                raise ValueError(f"Invalid {date_type} format. Use 'dd/mm/yyyy' format.")

    def _name_to_numbers(self) -> List[int]:
        """Convert name to list of numbers using ALPHABET mapping."""
        # Remove spaces and convert to uppercase
        clean_name = ''.join(self.name.upper().split())
        return [self.ALPHABET.get(char, 0) for char in clean_name if char in self.ALPHABET]

    def reduce_number(self, n: int) -> int:
        """
        Reduce number to single digit or master number (11, 22).

        Args:
            n: Number to reduce

        Returns:
            Reduced number (1-9, 11, or 22)
        """
        while n > 9 and n not in {11, 22}:
            n = sum(int(digit) for digit in str(n))
        return n
    
    def reduce_number_no_master(self, n: int) -> int:
        """
        Reduce number to single digit.
        """
        while n > 9:
            n = sum(int(digit) for digit in str(n))
        return n

    def reduce_number_with_masters(self, n: int, masters: Set[int] = None) -> int:
        """
        Reduce number keeping master numbers (11, 22, 33).

        Args:
            n: Number to reduce
            masters: Set of master numbers to preserve (default: {11, 22, 33})

        Returns:
            Reduced number (1-9, 11, 22, or 33)
        """
        if masters is None:
            masters = self.MASTER_NUMBERS

        while n > 9 and n not in masters:
            n = sum(int(digit) for digit in str(n))
        return n

    def reduce_to_single_digit(self, n: int) -> int:
        """
        Always reduce to single digit (1-9).

        Args:
            n: Number to reduce

        Returns:
            Single digit (1-9)
        """
        while n > 9:
            n = sum(int(digit) for digit in str(n))
        return n

    def _is_vowel(self, char: str, current_word: str = None) -> bool:
        """
        Check if character is a vowel for soul number calculation.

        Rules:
        1. A, E, I, O, U, Y are vowels
        2. Variants with diacritics (Â, Ă, Ê, Ô, Ơ, etc.) are vowels
        3. Y is only a vowel when:
           - It's the only vowel in the word, OR
           - It stands alone
        4. All other cases with Y are consonants
        """
        char_upper = char.upper()

        # Basic vowels: A, E, I, O, U
        basic_vowels = {
            'A', 'E', 'I', 'O', 'U',
            # A variants with diacritics
            'Á', 'À', 'Ả', 'Ã', 'Ạ',
            'Ắ', 'Ằ', 'Ẳ', 'Ẵ', 'Ặ',
            'Ấ', 'Ầ', 'Ẩ', 'Ẫ', 'Ậ',
            'Ă', 'Â',
            # E variants with diacritics
            'É', 'È', 'Ẻ', 'Ẽ', 'Ẹ',
            'Ế', 'Ề', 'Ể', 'Ễ', 'Ệ',
            'Ê',
            # I variants with diacritics
            'Í', 'Ì', 'Ỉ', 'Ĩ', 'Ị',
            # O variants with diacritics
            'Ó', 'Ò', 'Ỏ', 'Õ', 'Ọ',
            'Ố', 'Ồ', 'Ổ', 'Ỗ', 'Ộ',
            'Ớ', 'Ờ', 'Ở', 'Ỡ', 'Ợ',
            'Ô', 'Ơ',
            # U variants with diacritics
            'Ú', 'Ù', 'Ủ', 'Ũ', 'Ụ',
            'Ứ', 'Ừ', 'Ử', 'Ữ', 'Ự',
            'Ư'
        }

        # Check if it's a basic vowel
        if char_upper in basic_vowels:
            return True

        # Special handling for Y
        if char_upper == 'Y' or char_upper in {'Ý', 'Ỳ', 'Ỷ', 'Ỹ', 'Ỵ'}:
            if current_word:
                return self._is_y_vowel_in_word(char, current_word)
            else:
                # Fallback: find the word containing this Y character
                word = self._find_word_with_char_at_position(char)
                return self._is_y_vowel_in_word(char, word)

        return False

    def _is_y_vowel_in_word(self, char: str, word: str) -> bool:
        """
        Check if Y is a vowel in the given word.

        Y is a vowel when:
        - It's the only vowel in the word, OR
        - It stands alone
        """
        if not word:
            return False

        # Count other vowels in the word (excluding this Y)
        other_vowels_count = 0
        for c in word:
            if c.upper() != 'Y':
                c_upper = c.upper()
                # Check if it's a vowel (A, E, I, O, U and their variants)
                if (c_upper in {'A', 'E', 'I', 'O', 'U', 'Ă', 'Â', 'Ê', 'Ô', 'Ơ', 'Ư'} or
                    c_upper in {'Á', 'À', 'Ả', 'Ã', 'Ạ', 'Ắ', 'Ằ', 'Ẳ', 'Ẵ', 'Ặ', 'Ấ', 'Ầ', 'Ẩ', 'Ẫ', 'Ậ',
                               'É', 'È', 'Ẻ', 'Ẽ', 'Ẹ', 'Ế', 'Ề', 'Ể', 'Ễ', 'Ệ',
                               'Í', 'Ì', 'Ỉ', 'Ĩ', 'Ị',
                               'Ó', 'Ò', 'Ỏ', 'Õ', 'Ọ', 'Ố', 'Ồ', 'Ổ', 'Ỗ', 'Ộ', 'Ớ', 'Ờ', 'Ở', 'Ỡ', 'Ợ',
                               'Ú', 'Ù', 'Ủ', 'Ũ', 'Ụ', 'Ứ', 'Ừ', 'Ử', 'Ữ', 'Ự'}):
                    other_vowels_count += 1

        # Y is vowel if it's the only vowel in the word
        return other_vowels_count == 0

    def _find_word_with_char_at_position(self, char: str) -> str:
        """
        Find the word containing the given character at its specific position.
        """
        name_parts = self._split_name_parts()

        # Find the position of this character in the original name
        char_pos = self.name.find(char)
        if char_pos == -1:
            return ""

        # Find which word contains this character at this position
        current_pos = 0
        for part in name_parts:
            part_start = current_pos
            part_end = current_pos + len(part)

            if part_start <= char_pos < part_end:
                return part

            current_pos = part_end + 1  # +1 for space

        return ""

    def _is_consonant(self, char: str, current_word: str = None) -> bool:
        """Check if character is a consonant."""
        return not self._is_vowel(char, current_word)

    def _split_name_parts(self) -> List[str]:
        """Split name into individual parts (words)."""
        return [part.strip() for part in self.name.split() if part.strip()]

    def calculate_life_path(self) -> int:
        """
        Calculate Life Path Number (Growth Cycle Profiler).

        Formula: reduce_number_with_masters(dayR + monthR + yearR) (giữ 11/22/33)
        """
        return self.reduce_number_with_masters(self.day_r + self.month_r + self.year_r)

    def calculate_life_purpose(self) -> int:
        """
        Calculate Life Purpose Number (Strategic Purpose Archetype).

        Formula: reduce_number(sum(nameNumbers)) (giữ 11/22)
        """
        return self.reduce_number_with_masters(sum(self.name_numbers))

    def calculate_balance(self) -> int:
        """
        Calculate Balance Number (Trajectory Bridge Index).
        
        Formula: reduce_to_single_digit(sum(first_letters)) (always 1 digit)
        Get the first letter of each word in the full name, add all of them
        """
        name_parts = self._split_name_parts()
        if len(name_parts) < 1:  # Only need at least 1 word
            return 0
            
        first_letters_sum = 0
        for part in name_parts:
            if part:
                first_letter = part[0].upper()
                first_letters_sum += self.ALPHABET.get(first_letter, 0)
        
        return self.reduce_to_single_digit(first_letters_sum)

    def calculate_soul(self) -> int:
        """
        Calculate Soul Number (Inner Drive Index).

        Formula: reduce_number_with_masters(sum(reduce_number_with_masters(sum(vowels(part))) for part in parts))
        """
        name_parts = self._split_name_parts()
        soul_sum = 0

        for part in name_parts:
            part_vowels_sum = sum(
                self.ALPHABET.get(char.upper(), 0)
                for char in part
                if self._is_vowel(char, part)
            )
            soul_sum += self.reduce_number_with_masters(part_vowels_sum)

        return self.reduce_number_with_masters(soul_sum)

    def calculate_personality(self) -> int:
        """
        Calculate Personality Number (Outer Expression Index).

        Formula: reduce_number_with_masters(sum(reduce_number_with_masters(sum(consonants(part))) for part in parts))
        """
        name_parts = self._split_name_parts()
        personality_sum = 0

        for part in name_parts:
            part_consonants_sum = sum(
                self.ALPHABET.get(char.upper(), 0)
                for char in part
                if self._is_consonant(char)
            )
            personality_sum += self.reduce_number_with_masters(part_consonants_sum)

        return self.reduce_number_with_masters(personality_sum)

    def calculate_birth_day(self) -> int:
        """
        Calculate Birth Day Number (Core Advantage Marker).

        Formula: reduce_number(day) (keep master number 11/22)
        """
        return self.reduce_number_with_masters(self.day)

    def calculate_subconscious_strength(self) -> int:
        """
        Calculate Subconscious Strength (Cognitive Response Pattern).

        Formula: 9 - count(missing_aspects)
        (missing_aspects are numbers 1..9 not in nameNumbers)
        """
        missing_aspects = self.get_missing_aspects()
        return 9 - len(missing_aspects)

    def calculate_maturity(self) -> int:
        """
        Calculate Maturity Number (Peak Performance Phase).

        Formula: reduce_number(life_path + life_purpose) (keep master number 11/22)
        """
        life_path = self.calculate_life_path()
        life_purpose = self.calculate_life_purpose()
        return self.reduce_number_with_masters(life_path + life_purpose)

    def get_missing_aspects(self) -> Set[int]:
        """
        Get missing aspects (Growth Barrier Insight).

        Returns:
            Set of numbers 1-9 not appearing in name_numbers
        """
        name_digits = set()
        for num in self.name_numbers:
            for digit in str(num):
                if digit.isdigit():
                    name_digits.add(int(digit))

        return sorted(set(range(1, 10)) - name_digits)

    def check_karmic_debt(self) -> str:
        """
        Check for Karmic Debt (shadow_challenge_code).

        Formula:
        - karmic = {13, 14, 16, 19}
        - dobSum = sum(all digits in day, month, year)
        - If dobSum ∈ karmic or sum(nameNumbers) ∈ karmic ⇒ "Has Karmic Debt"
        """
        # Sum of all digits in date of birth
        dob_sum = sum(int(digit) for digit in f"{self.day}{self.month}{self.year}")

        # Sum of name numbers
        name_sum = sum(self.name_numbers)

        if dob_sum in self.KARMIC_NUMBERS or name_sum in self.KARMIC_NUMBERS:
            return "Có Karmic Debt"
        return "Không có Karmic Debt"

    def calculate_passion(self) -> List[int]:
        """
        Calculate Passion Number (Crisis Coping Signature).

        Formula: Count frequency of numbers in nameNumbers, get the most frequent numbers
        """
        from collections import Counter

        digit_counts = Counter()
        for num in self.name_numbers:
            for digit in str(num):
                if digit.isdigit():
                    digit_counts[int(digit)] += 1

        if not digit_counts:
            return []

        max_freq = max(digit_counts.values())
        return sorted([num for num, freq in digit_counts.items() if freq == max_freq])

    def get_societal_adaptability_index(self) -> str:
        """
        Get societal adaptability index based on birth year.

        Formula:
        - 1981–1996: "Gen Y (Millennials) - Cân bằng công việc-cuộc sống, công nghệ"
        - 1997–2012: "Gen Z - Công nghệ số, đa dạng, thay đổi nhanh"
        - Khác: "Khác"
        """
        if 1981 <= self.year <= 1996:
            return "Gen Y (Millennials) - Cân bằng công việc-cuộc sống, công nghệ"
        elif 1997 <= self.year <= 2012:
            return "Gen Z - Công nghệ số, đa dạng, thay đổi nhanh"
        else:
            return "Khác"

    def calculate_emotional_response_style(self) -> int:
        """
        Calculate Emotional Response Style.

        Formula: reduceNumber(sum(first4Letters)) (giữ 11/22)
        """
        clean_name = ''.join(self.name.upper().split())
        first_4_sum = sum(
            self.ALPHABET.get(char, 0)
            for char in clean_name[:4]
            if char in self.ALPHABET
        )
        return self.reduce_number(first_4_sum)

    def calculate_link_connection(self) -> int:
        """
        Calculate Link Connection (Authenticity Alignment Index).

        Formula: reduceNumber(abs(soul - personality)) (Keep master number 11/22)
        """
        lifepath = self.calculate_life_path()
        life_purpose = self.calculate_life_purpose()
        return self.reduce_number(abs(lifepath - life_purpose))

    def calculate_soul_personality_link(self) -> int:
        """
        Calculate Soul-Personality Link.

        Formula: reduceToSingleDigit(abs(soul - personality)) (1 digit)
        """
        soul = self.calculate_soul()
        if soul in [11, 22, 33]:
            soul = sum(int(digit) for digit in str(soul))
        personality = self.calculate_personality()
        return self.reduce_to_single_digit(abs(soul - personality))

    def calculate_milestone_phase(self) -> Dict[str, int]:
        """
        Calculate Milestone Phase (PWI Evolution Milestones).

        Formula (keep master number 11/22 at each reduceNumber step):
        - dayM = reduceNumber(day); monthM = reduceNumber(month); yearM = reduceNumber(year)
        - milestone_1 = reduceNumber(monthM + dayM)     // Month + Day
        - milestone_2 = reduceNumber(dayM + yearM)      // Day + Year
        - milestone_3 = reduceNumber(milestone_1 + milestone_2)
        - milestone_4 = reduceNumber(monthM + yearM)    // Month + Year
        """
        day_m = self.reduce_number(self.day)
        month_m = self.reduce_number(self.month)
        year_m = self.reduce_number(self.year)

        milestone_1 = self.reduce_number(month_m + day_m)
        milestone_2 = self.reduce_number(day_m + year_m)
        milestone_3 = self.reduce_number(milestone_1 + milestone_2)
        milestone_4 = self.reduce_number(month_m + year_m)

        return {
            "milestone_1": milestone_1,
            "milestone_2": milestone_2,
            "milestone_3": milestone_3,
            "milestone_4": milestone_4
        }

    def calculate_challenge(self) -> Dict[str, int]:
        """
        Calculate Challenge Numbers (Adaptive Challenge Codes).

        Formula (keep dayR, monthR, yearR like life_path - keep master number 11/22/33):
        - challenge_1 = abs(dayR - monthR)
        - challenge_2 = abs(dayR - yearR)
        - challenge_3 = abs(challenge_1 - challenge_2)
        - challenge_4 = abs(monthR - yearR)
        """
        challenge_1 = abs(self.day_r_no_master - self.month_r_no_master)
        challenge_2 = abs(self.day_r_no_master - self.year_r_no_master)
        challenge_3 = abs(challenge_1 - challenge_2)
        challenge_4 = abs(self.month_r_no_master - self.year_r_no_master)

        return {
            "challenge_1": challenge_1,
            "challenge_2": challenge_2,
            "challenge_3": challenge_3,
            "challenge_4": challenge_4
        }

    def calculate_rational_thinking(self) -> int:
        """
        Calculate Rational Thinking.
        
        Formula: reduceNumberWithMasters(day + sum(letters_of_given_name)) (keep master number 11/22/33)
        Get the given name (last part in full name), add the value of each letter + day of birth (day)
        """
        name_parts = self._split_name_parts()
        if not name_parts:
            return 0
            
        given_name = name_parts[-1]  # Last part (given name)
        given_name_sum = sum(
            self.ALPHABET.get(char.upper(), 0)
            for char in given_name
            if char.upper() in self.ALPHABET
        )
        
        return self.reduce_number_with_masters(self.day + given_name_sum)

    def calculate_age_milestones(self) -> List[int]:
        """
        Calculate Age Milestones.

        Formula:
        - If life_path ∈ {11,22,33} ⇒ start = 36 - 4 = 32
        - Otherwise 36 - life_path
        - Array of 4 milestones: [start, start+9, start+18, start+27]
        """
        life_path = self.calculate_life_path()

        if life_path in self.MASTER_NUMBERS:
            start = 32  # 36 - 4
        else:
            start = 36 - life_path

        return [start, start + 9, start + 18, start + 27]

    def calculate_alignment_signals(self) -> Dict[str, int]:
        """
        Calculate Alignment Signals (Personal Year and Personal Day).

        Formula (with currentDate = dd/mm/yyyy):
        - personal_year = reduceNumber(day + month + currentYear)      // keep master number 11/22
        - personal_day = reduceNumber(currentDay + currentMonth + personal_year)
        """
        current_year = self.current_datetime.year
        current_month = self.current_datetime.month
        current_day = self.current_datetime.day

        # Personal Year
        personal_year = self.day + self.month + current_year

        if current_month < self.month or (current_month == self.month and current_day < self.day):
            personal_year -= 1
        
        personal_year = self.reduce_number_no_master(personal_year)

        # Personal Month
        personal_month = self.reduce_number_no_master(current_month + personal_year)

        # Personal Day
        personal_day = self.reduce_number_no_master(current_day + current_month + personal_year)

        return {
            "personal_year": personal_year,
            "personal_month": personal_month,
            "personal_day": personal_day
        }

    def get_personal_date_num(self) -> Dict[str, Union[int, str, List[int]]]:
        """
        Get comprehensive personal numerology calculations.

        Returns:
            Dictionary containing all calculated numerology numbers
        """
        return {
            "day_of_birth": self.dob_date.strftime("%d/%m/%Y"),
            "current_date": self.current_datetime.strftime("%d/%m/%Y"),
            "life_path": self.calculate_life_path(),
            "life_purpose": self.calculate_life_purpose(),
            "balance": self.calculate_balance(),
            "soul": self.calculate_soul(),
            "personality": self.calculate_personality(),
            "birth_day": self.calculate_birth_day(),
            "subconscious_strength": self.calculate_subconscious_strength(),
            "maturity": self.calculate_maturity(),
            "missing_aspects": list(self.get_missing_aspects()),
            "shadow_challenge_code": self.check_karmic_debt(),
            "passion": self.calculate_passion(),
            "societal_adaptability_index": self.get_societal_adaptability_index(),
            "emotional_response_style": self.calculate_emotional_response_style(),
            "lifepath_life_purpose_link": self.calculate_link_connection(),
            "soul_personality_link": self.calculate_soul_personality_link(),
            "milestone_phase": self.calculate_milestone_phase(),
            "challenge": self.calculate_challenge(),
            "rational_thinking": self.calculate_rational_thinking(),
            "age_milestones": self.calculate_age_milestones(),
            "alignment_signals": self.calculate_alignment_signals()
        }

