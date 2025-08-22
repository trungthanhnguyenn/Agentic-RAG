from datetime import datetime, timedelta
import calendar
import re
from dateutil.relativedelta import relativedelta

class TimeCalculator:
    """
    Enhanced utility class for complex time and date calculations
    Provides methods to calculate dates based on various time references
    """
    
    def __init__(self):
        """Initialize with current date"""
        self.current_date = datetime.now()
    
    def get_current_date(self):
        """Get current date in formatted string"""
        return self.current_date.strftime("%Y-%m-%d")
    
    def get_current_weekday(self):
        """Get current weekday in Vietnamese"""
        weekdays = {
            0: "Thứ 2",
            1: "Thứ 3", 
            2: "Thứ 4",
            3: "Thứ 5",
            4: "Thứ 6",
            5: "Thứ 7",
            6: "Chủ nhật"
        }
        return weekdays[self.current_date.weekday()]
    
    def parse_complex_time_reference(self, text):
        """
        Parse complex Vietnamese time references and convert to target date
        
        Args:
            text (str): Text containing complex time reference
            
        Returns:
            dict: Date information including calculated date and metadata
        """
        text = text.lower().strip()
        
        # Handle "thứ X tuần sau" pattern (including text and abbreviations)
        weekday_next_pattern = r"thứ\s*(\d+)\s*tuần\s*sau"
        weekday_next_match = re.search(weekday_next_pattern, text)
        if weekday_next_match:
            return self._calculate_next_weekday(int(weekday_next_match.group(1)))
        
        # Handle "thứ X tuần trước" pattern (including text and abbreviations)
        weekday_prev_pattern = r"thứ\s*(\d+)\s*tuần\s*trước"
        weekday_prev_match = re.search(weekday_prev_pattern, text)
        if weekday_prev_match:
            return self._calculate_previous_weekday(int(weekday_prev_match.group(1)))
        
        # Handle "thứ X" pattern (current week or next occurrence)
        weekday_current_pattern = r"thứ\s*(\d+)"
        weekday_current_match = re.search(weekday_current_pattern, text)
        if weekday_current_match:
            return self._calculate_current_weekday(int(weekday_current_match.group(1)))
        
        # Handle "thứ X" with text numbers (hai, ba, tư, năm, sáu, bảy)
        text_weekday_pattern = r"thứ\s*(hai|ba|tư|năm|sáu|bảy)"
        text_weekday_match = re.search(text_weekday_pattern, text)
        if text_weekday_match:
            weekday_text = text_weekday_match.group(1)
            weekday_number = self._convert_text_to_weekday_number(weekday_text)
            return self._calculate_current_weekday(weekday_number)
        
        # Handle "chủ nhật" pattern
        if "chủ nhật" in text:
            return self._calculate_current_weekday(8)  # 8 for Chủ nhật
        
        # Handle "t2", "t3", "t4", "t5", "t6", "t7", "cn" abbreviations
        abbrev_weekday_pattern = r"\b(t[2-7]|cn)\b"
        abbrev_weekday_match = re.search(abbrev_weekday_pattern, text)
        if abbrev_weekday_match:
            abbrev = abbrev_weekday_match.group(1)
            weekday_number = self._convert_abbrev_to_weekday_number(abbrev)
            return self._calculate_current_weekday(weekday_number)
        
        # Handle "đầu tuần sau" pattern
        if "đầu tuần sau" in text:
            return self._calculate_start_of_next_week()
        
        # Handle "cuối tuần sau" pattern
        if "cuối tuần sau" in text:
            return self._calculate_end_of_next_week()
        
        # Handle "đầu tuần trước" pattern
        if "đầu tuần trước" in text:
            return self._calculate_start_of_previous_week()
        
        # Handle "cuối tuần trước" pattern
        if "cuối tuần trước" in text:
            return self._calculate_end_of_previous_week()
        
        # Handle "đầu năm sau" pattern
        if "đầu năm sau" in text:
            return self._calculate_start_of_next_year()
        
        # Handle "cuối năm sau" pattern
        if "cuối năm sau" in text:
            return self._calculate_end_of_next_year()
        
        # Handle "đầu năm trước" pattern
        if "đầu năm trước" in text:
            return self._calculate_start_of_previous_year()
        
        # Handle "cuối năm trước" pattern
        if "cuối năm trước" in text:
            return self._calculate_end_of_previous_year()
        
        # Handle "ngày này tháng sau" pattern
        if "ngày này tháng sau" in text:
            return self._calculate_same_day_next_month()
        
        # Handle "ngày này tháng trước" pattern
        if "ngày này tháng trước" in text:
            return self._calculate_same_day_previous_month()
        
        # Handle "ngày này năm sau" pattern
        if "ngày này năm sau" in text:
            return self._calculate_same_day_next_year()
        
        # Handle "ngày này năm trước" pattern
        if "ngày này năm trước" in text:
            return self._calculate_same_day_previous_year()
        
        # Handle "X năm nữa" pattern
        years_pattern = r"(\d+)\s*năm\s*nữa"
        years_match = re.search(years_pattern, text)
        if years_match:
            return self._calculate_years_ahead(int(years_match.group(1)))
        
        # Handle "X tháng nữa" pattern
        months_pattern = r"(\d+)\s*tháng\s*nữa"
        months_match = re.search(months_pattern, text)
        if months_match:
            return self._calculate_months_ahead(int(months_match.group(1)))
        
        # Handle "X tuần nữa" pattern
        weeks_pattern = r"(\d+)\s*tuần\s*nữa"
        weeks_match = re.search(weeks_pattern, text)
        if weeks_match:
            return self._calculate_weeks_ahead(int(weeks_match.group(1)))
        
        # Handle simple Vietnamese time references first (exact matches)
        simple_mapping = {
            "hôm nay": 0,
            "ngày mai": 1,
            "ngày mốt": 2,
            "ngày kia": 3,
        }
        
        for reference, days in simple_mapping.items():
            if reference in text:
                return self._calculate_days_ahead(days)
        
        # Handle "X ngày nữa" pattern (more flexible)
        days_pattern = r"(\d+)\s*ngày\s*nữa"
        days_match = re.search(days_pattern, text)
        if days_match:
            return self._calculate_days_ahead(int(days_match.group(1)))
        
        # Handle "cuối tháng" pattern
        if "cuối tháng" in text:
            return self._calculate_end_of_month()
        
        # Handle "đầu tháng" pattern
        if "đầu tháng" in text:
            return self._calculate_start_of_month()
        
        # Handle "cuối tuần" pattern
        if "cuối tuần" in text:
            return self._calculate_end_of_week()
        
        # Handle "đầu tuần" pattern
        if "đầu tuần" in text:
            return self._calculate_start_of_week()
        
        # Default to today if no match found
        return self._calculate_days_ahead(0)
    
    def _convert_text_to_weekday_number(self, text):
        """Convert Vietnamese text weekday to number"""
        text_to_number = {
            "hai": 2,
            "ba": 3,
            "tư": 4,
            "năm": 5,
            "sáu": 6,
            "bảy": 7
        }
        return text_to_number.get(text, 2)  # Default to Monday if not found
    
    def _convert_abbrev_to_weekday_number(self, abbrev):
        """Convert weekday abbreviation to number"""
        abbrev_to_number = {
            "t2": 2,
            "t3": 3,
            "t4": 4,
            "t5": 5,
            "t6": 6,
            "t7": 7,
            "cn": 8  # Chủ nhật
        }
        return abbrev_to_number.get(abbrev, 2)  # Default to Monday if not found
    
    def _calculate_current_weekday(self, target_weekday):
        """
        Calculate specific weekday in current week or next occurrence
        
        Args:
            target_weekday (int): Target weekday (2-8, where 2 is Monday, 8 is Sunday)
            
        Returns:
            dict: Date information for target weekday
        """
        # Convert Vietnamese weekday number to Python weekday (0-6, where 0 is Monday)
        python_weekday = self._convert_thu_to_python_weekday(target_weekday)
        
        # Calculate days until target weekday
        days_until_target = python_weekday - self.current_date.weekday()
        
        # If target weekday is today or has passed this week, get next occurrence
        if days_until_target <= 0:
            days_until_target += 7
        
        target_date = self.current_date + timedelta(days=days_until_target)
        days_ahead = days_until_target
        
        return {
            "time_reference": f"thứ {target_weekday}" if target_weekday != 8 else "chủ nhật",
            "calculated_date": target_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(target_date.weekday()),
            "days_from_now": days_ahead,
            "calculation_type": "current_weekday"
        }
    
    def _calculate_start_of_next_week(self):
        """Calculate Monday of next week"""
        # Find Monday of current week
        monday_this_week = self.current_date - timedelta(days=self.current_date.weekday())
        # Add 7 days to get Monday of next week
        monday_next_week = monday_this_week + timedelta(days=7)
        days_diff = (monday_next_week - self.current_date).days
        
        return {
            "time_reference": "đầu tuần sau",
            "calculated_date": monday_next_week.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(monday_next_week.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "start_of_next_week"
        }
    
    def _calculate_end_of_next_week(self):
        """Calculate Sunday of next week"""
        # Find Monday of current week
        monday_this_week = self.current_date - timedelta(days=self.current_date.weekday())
        # Add 13 days to get Sunday of next week (7 for next week + 6 for Sunday)
        sunday_next_week = monday_this_week + timedelta(days=13)
        days_diff = (sunday_next_week - self.current_date).days
        
        return {
            "time_reference": "cuối tuần sau",
            "calculated_date": sunday_next_week.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(sunday_next_week.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "end_of_next_week"
        }
    
    def _calculate_start_of_previous_week(self):
        """Calculate Monday of previous week"""
        # Find Monday of current week
        monday_this_week = self.current_date - timedelta(days=self.current_date.weekday())
        # Subtract 7 days to get Monday of previous week
        monday_previous_week = monday_this_week - timedelta(days=7)
        days_diff = (monday_previous_week - self.current_date).days
        
        return {
            "time_reference": "đầu tuần trước",
            "calculated_date": monday_previous_week.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(monday_previous_week.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "start_of_previous_week"
        }
    
    def _calculate_end_of_previous_week(self):
        """Calculate Sunday of previous week"""
        # Find Monday of current week
        monday_this_week = self.current_date - timedelta(days=self.current_date.weekday())
        # Subtract 1 day to get Sunday of previous week
        sunday_previous_week = monday_this_week - timedelta(days=1)
        days_diff = (sunday_previous_week - self.current_date).days
        
        return {
            "time_reference": "cuối tuần trước",
            "calculated_date": sunday_previous_week.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(sunday_previous_week.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "end_of_previous_week"
        }
    
    def _calculate_start_of_next_year(self):
        """Calculate January 1st of next year"""
        next_year = self.current_date.year + 1
        start_of_next_year = datetime(next_year, 1, 1)
        days_diff = (start_of_next_year - self.current_date).days
        
        return {
            "time_reference": "đầu năm sau",
            "calculated_date": start_of_next_year.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(start_of_next_year.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "start_of_next_year"
        }
    
    def _calculate_end_of_next_year(self):
        """Calculate December 31st of next year"""
        next_year = self.current_date.year + 1
        end_of_next_year = datetime(next_year, 12, 31)
        days_diff = (end_of_next_year - self.current_date).days
        
        return {
            "time_reference": "cuối năm sau",
            "calculated_date": end_of_next_year.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(end_of_next_year.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "end_of_next_year"
        }
    
    def _calculate_start_of_previous_year(self):
        """Calculate January 1st of previous year"""
        previous_year = self.current_date.year - 1
        start_of_previous_year = datetime(previous_year, 1, 1)
        days_diff = (start_of_previous_year - self.current_date).days
        
        return {
            "time_reference": "đầu năm trước",
            "calculated_date": start_of_previous_year.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(start_of_previous_year.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "start_of_previous_year"
        }
    
    def _calculate_end_of_previous_year(self):
        """Calculate December 31st of previous year"""
        previous_year = self.current_date.year - 1
        end_of_previous_year = datetime(previous_year, 12, 31)
        days_diff = (end_of_previous_year - self.current_date).days
        
        return {
            "time_reference": "cuối năm trước",
            "calculated_date": end_of_previous_year.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(end_of_previous_year.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "end_of_previous_year"
        }
    
    def _calculate_next_weekday(self, target_weekday):
        """
        Calculate specific weekday in next week (next week, not current week)
        
        Args:
            target_weekday (int): Target weekday (1-7, where 1 is Monday)
            
        Returns:
            dict: Date information for target weekday
        """
        # Convert Vietnamese weekday number to Python weekday (0-6, where 0 is Monday)
        python_weekday = self._convert_thu_to_python_weekday(target_weekday)
        
        # Find Monday of current week
        monday_this_week = self.current_date - timedelta(days=self.current_date.weekday())
        # Add 7 days to get Monday of next week
        monday_next_week = monday_this_week + timedelta(days=7)
        # Add the target weekday offset (0=Monday, 1=Tuesday, etc.)
        target_date = monday_next_week + timedelta(days=python_weekday)
        
        days_ahead = (target_date - self.current_date).days
        
        return {
            "time_reference": f"thứ {target_weekday} tuần sau",
            "calculated_date": target_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(target_date.weekday()),
            "days_from_now": days_ahead,
            "calculation_type": "next_weekday"
        }
    
    def _calculate_previous_weekday(self, target_weekday):
        """
        Calculate specific weekday in previous week (previous week, not current week)
        
        Args:
            target_weekday (int): Target weekday (1-7, where 1 is Monday)
            
        Returns:
            dict: Date information for target weekday
        """
        # Convert Vietnamese weekday number to Python weekday (0-6, where 0 is Monday)
        python_weekday = self._convert_thu_to_python_weekday(target_weekday)

        # Find the previous occurrence of the target weekday strictly before today
        days_back = self.current_date.weekday() - python_weekday
        if days_back <= 0:
            days_back += 7
        target_date = self.current_date - timedelta(days=days_back)

        return {
            "time_reference": f"thứ {target_weekday} tuần trước",
            "calculated_date": target_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(target_date.weekday()),
            "days_from_now": -days_back,
            "calculation_type": "previous_weekday"
        }

    def _convert_thu_to_python_weekday(self, thu_number: int) -> int:
        """
        Convert Vietnamese 'thứ' number to Python weekday index.
        Mapping:
        - Thứ 2 -> 0 (Monday)
        - Thứ 3 -> 1 (Tuesday)
        - Thứ 4 -> 2 (Wednesday)
        - Thứ 5 -> 3 (Thursday)
        - Thứ 6 -> 4 (Friday)
        - Thứ 7 -> 5 (Saturday)
        - Chủ nhật -> 6 (use thu_number = 8 internally)
        """
        if thu_number == 8:  # Chủ nhật
            return 6
        # thu_number expected in [2..7]
        return (thu_number - 2) % 7
        
        # Find Monday of current week
        monday_this_week = self.current_date - timedelta(days=self.current_date.weekday())
        # Subtract 7 days to get Monday of previous week
        monday_previous_week = monday_this_week - timedelta(days=7)
        # Add the target weekday offset
        target_date = monday_previous_week + timedelta(days=python_weekday)
        
        days_back = (self.current_date - target_date).days
        
        return {
            "time_reference": f"thứ {target_weekday} tuần trước",
            "calculated_date": target_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(target_date.weekday()),
            "days_from_now": -days_back,
            "calculation_type": "previous_weekday"
        }
    
    def _calculate_same_day_next_month(self):
        """Calculate same day in next month"""
        try:
            next_month_date = self.current_date + relativedelta(months=1)
        except ValueError:
            # Handle edge case where next month doesn't have current day
            # Move to last day of next month
            next_month = self.current_date.replace(day=1) + relativedelta(months=1)
            next_month_date = next_month - timedelta(days=1)
        
        days_diff = (next_month_date - self.current_date).days
        
        return {
            "time_reference": "ngày này tháng sau",
            "calculated_date": next_month_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(next_month_date.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "next_month_same_day"
        }
    
    def _calculate_same_day_previous_month(self):
        """Calculate same day in previous month"""
        try:
            prev_month_date = self.current_date - relativedelta(months=1)
        except ValueError:
            # Handle edge case where previous month doesn't have current day
            # Move to last day of previous month
            prev_month = self.current_date.replace(day=1) - relativedelta(months=1)
            prev_month_date = prev_month - timedelta(days=1)
        
        days_diff = (prev_month_date - self.current_date).days
        
        return {
            "time_reference": "ngày này tháng trước",
            "calculated_date": prev_month_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(prev_month_date.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "previous_month_same_day"
        }
    
    def _calculate_same_day_next_year(self):
        """Calculate same day in next year"""
        next_year_date = self.current_date + relativedelta(years=1)
        days_diff = (next_year_date - self.current_date).days
        
        return {
            "time_reference": "ngày này năm sau",
            "calculated_date": next_year_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(next_year_date.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "next_year_same_day"
        }
    
    def _calculate_same_day_previous_year(self):
        """Calculate same day in previous year"""
        prev_year_date = self.current_date - relativedelta(years=1)
        days_diff = (prev_year_date - self.current_date).days
        
        return {
            "time_reference": "ngày này năm trước",
            "calculated_date": prev_year_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(prev_year_date.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "previous_year_same_day"
        }
    
    def _calculate_years_ahead(self, years):
        """Calculate date X years from now"""
        target_date = self.current_date + relativedelta(years=years)
        days_diff = (target_date - self.current_date).days
        
        return {
            "time_reference": f"{years} năm nữa",
            "calculated_date": target_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(target_date.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "years_ahead"
        }
    
    def _calculate_months_ahead(self, months):
        """Calculate date X months from now with proper month handling"""
        try:
            target_date = self.current_date + relativedelta(months=months)
        except ValueError:
            # Handle edge case where target month doesn't have current day
            # Move to last day of target month
            target_month = self.current_date.replace(day=1) + relativedelta(months=months)
            target_date = target_month - timedelta(days=1)
        
        days_diff = (target_date - self.current_date).days
        
        return {
            "time_reference": f"{months} tháng nữa",
            "calculated_date": target_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(target_date.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "months_ahead"
        }
    
    def _calculate_weeks_ahead(self, weeks):
        """Calculate date X weeks from now"""
        target_date = self.current_date + timedelta(weeks=weeks)
        days_diff = (target_date - self.current_date).days
        
        return {
            "time_reference": f"{weeks} tuần nữa",
            "calculated_date": target_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(target_date.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "weeks_ahead"
        }
    
    def _calculate_days_ahead(self, days):
        """Calculate date X days from now"""
        target_date = self.current_date + timedelta(days=days)
        
        return {
            "time_reference": f"{days} ngày nữa" if days > 0 else "hôm nay",
            "calculated_date": target_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(target_date.weekday()),
            "days_from_now": days,
            "calculation_type": "days_ahead"
        }
    
    def _calculate_end_of_month(self):
        """Calculate last day of current month"""
        # Get last day of current month
        last_day = calendar.monthrange(self.current_date.year, self.current_date.month)[1]
        target_date = self.current_date.replace(day=last_day)
        days_diff = (target_date - self.current_date).days
        
        return {
            "time_reference": "cuối tháng",
            "calculated_date": target_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(target_date.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "end_of_month"
        }
    
    def _calculate_start_of_month(self):
        """Calculate first day of current month"""
        target_date = self.current_date.replace(day=1)
        days_diff = (target_date - self.current_date).days
        
        return {
            "time_reference": "đầu tháng",
            "calculated_date": target_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(target_date.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "start_of_month"
        }
    
    def _calculate_end_of_week(self):
        """Calculate Sunday (end of week)"""
        # Calculate days until Sunday (weekday 6)
        days_until_sunday = 6 - self.current_date.weekday()
        if days_until_sunday <= 0:  # Already Sunday or past Sunday
            days_until_sunday += 7
        
        target_date = self.current_date + timedelta(days=days_until_sunday)
        days_diff = (target_date - self.current_date).days
        
        return {
            "time_reference": "cuối tuần",
            "calculated_date": target_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(target_date.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "end_of_week"
        }
    
    def _calculate_start_of_week(self):
        """Calculate Monday (start of week)"""
        # Calculate days since Monday (weekday 0)
        days_since_monday = self.current_date.weekday()
        target_date = self.current_date - timedelta(days=days_since_monday)
        days_diff = (target_date - self.current_date).days
        
        return {
            "time_reference": "đầu tuần",
            "calculated_date": target_date.strftime("%Y-%m-%d"),
            "weekday": self._get_weekday_name(target_date.weekday()),
            "days_from_now": days_diff,
            "calculation_type": "start_of_week"
        }
    
    def _get_weekday_name(self, weekday):
        """Convert weekday number to Vietnamese name"""
        weekdays = {
            0: "Thứ 2",
            1: "Thứ 3",
            2: "Thứ 4",
            3: "Thứ 5",
            4: "Thứ 6",
            5: "Thứ 7",
            6: "Chủ nhật"
        }
        return weekdays[weekday]
    
    def get_date_info(self, time_reference):
        """
        Get comprehensive date information based on time reference
        
        Args:
            time_reference (str): Time reference text
            
        Returns:
            dict: Complete date information
        """
        return self.parse_complex_time_reference(time_reference)