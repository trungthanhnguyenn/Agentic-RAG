from typing import Dict, Any, List

import pandas as pd


class DataValidator:
    """
    Basic data validator for incoming user inputs and trading Excel data.
    Provides actionable issues and suggestions instead of raising hard errors.
    """

    REQUIRED_COLUMNS = ["symbol", "side", "close_time", "net_profit"]

    def validate_excel_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        issues: List[str] = []
        suggestions: List[str] = []

        if df is None or df.empty:
            issues.append("DataFrame is empty")
            suggestions.append("Hãy kiểm tra lại file Excel và đảm bảo có dữ liệu giao dịch.")
            return {"is_valid": False, "issues": issues, "suggestions": suggestions}

        # Normalize columns
        columns = [str(c).strip() for c in df.columns]
        missing = [c for c in self.REQUIRED_COLUMNS if c not in columns]
        if missing:
            issues.append(f"Thiếu cột bắt buộc: {missing}")
            suggestions.append("Đảm bảo file có các cột: symbol, side, close_time, net_profit (có thể đặt tên theo mapping).")

        # Check types & parsability
        if "close_time" in df.columns:
            try:
                pd.to_datetime(df["close_time"], errors="raise", dayfirst=True)
            except Exception:
                issues.append("Cột close_time không thể parse datetime (dd/mm/yyyy).")
                suggestions.append("Hãy định dạng close_time theo dd/mm/yyyy HH:MM hoặc chuẩn datetime.")

        if "net_profit" in df.columns:
            if pd.to_numeric(df["net_profit"], errors="coerce").isna().any():
                issues.append("Cột net_profit chứa giá trị không phải số.")
                suggestions.append("Hãy đảm bảo net_profit là số, không chứa chuỗi lạ.")

        is_valid = len(issues) == 0
        return {"is_valid": is_valid, "issues": issues, "suggestions": suggestions}

    def validate_profile(self, user_name: str, birthday: str) -> Dict[str, Any]:
        issues: List[str] = []
        suggestions: List[str] = []
        if not user_name:
            issues.append("Thiếu user_name")
            suggestions.append("Cung cấp họ tên để tính toán chỉ số tên.")
        if not birthday:
            issues.append("Thiếu birthday")
            suggestions.append("Cung cấp ngày sinh dạng dd/mm/yyyy để tính các chỉ số.")
        return {"is_valid": len(issues) == 0, "issues": issues, "suggestions": suggestions}

