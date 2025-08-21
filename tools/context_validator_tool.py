# tools/context_validator_tool.py
"""
Context Validation Tool for detecting inconsistencies between numerology data and trading behavior.
This tool helps identify contradictions and suggests balance strategies.
"""

from typing import Dict, List, Any, Tuple
import pandas as pd
from datetime import datetime

class ContextValidator:
    """
    Validates consistency between numerology data and trading behavior.
    Detects contradictions and suggests balance strategies.
    """
    
    def __init__(self):
        # Define personality-trading behavior mappings
        self.personality_trading_mapping = {
            "cẩn trọng": {
                "expected_behaviors": ["low_risk", "small_positions", "conservative"],
                "contradictory_behaviors": ["high_risk", "large_positions", "aggressive", "rapid_fire"]
            },
            "mạo hiểm": {
                "expected_behaviors": ["high_risk", "large_positions", "aggressive"],
                "contradictory_behaviors": ["low_risk", "small_positions", "conservative", "hesitant"]
            },
            "cân bằng": {
                "expected_behaviors": ["moderate_risk", "balanced_positions"],
                "contradictory_behaviors": ["extreme_risk", "very_small_positions"]
            }
        }
        
        # Define life path number characteristics
        self.life_path_characteristics = {
            1: {"traits": ["lãnh đạo", "độc lập"], "trading_style": "aggressive", "risk_level": "high"},
            2: {"traits": ["hợp tác", "nhạy cảm"], "trading_style": "collaborative", "risk_level": "low"},
            3: {"traits": ["sáng tạo", "giao tiếp"], "trading_style": "innovative", "risk_level": "medium"},
            4: {"traits": ["ổn định", "thực tế"], "trading_style": "conservative", "risk_level": "low"},
            5: {"traits": ["thay đổi", "phiêu lưu"], "trading_style": "dynamic", "risk_level": "high"},
            6: {"traits": ["trách nhiệm", "nuôi dưỡng"], "trading_style": "protective", "risk_level": "low"},
            7: {"traits": ["phân tích", "tâm linh"], "trading_style": "analytical", "risk_level": "medium"},
            8: {"traits": ["quyền lực", "vật chất"], "trading_style": "ambitious", "risk_level": "high"},
            9: {"traits": ["nhân đạo", "hoàn thiện"], "trading_style": "idealistic", "risk_level": "medium"},
            11: {"traits": ["trực giác", "tâm linh"], "trading_style": "intuitive", "risk_level": "medium"},
            22: {"traits": ["xây dựng", "thực tế"], "trading_style": "builder", "risk_level": "medium"},
            33: {"traits": ["phục vụ", "tâm linh"], "trading_style": "service", "risk_level": "low"}
        }
    
    def validate_consistency(self, numerology_data: Dict[str, Any], trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate consistency between numerology data and trading behavior.
        
        Args:
            numerology_data: Numerology calculation results
            trading_data: Trading analysis results
            
        Returns:
            Dictionary containing validation results and insights
        """
        validation_results = {
            "is_consistent": True,
            "inconsistencies": [],
            "insights": [],
            "recommendations": []
        }
        
        # Check life path vs trading style consistency
        life_path = numerology_data.get("life_path")
        if life_path and life_path in self.life_path_characteristics:
            expected_style = self.life_path_characteristics[life_path]["trading_style"]
            expected_risk = self.life_path_characteristics[life_path]["risk_level"]
            
            # Analyze actual trading behavior
            actual_risk = self._analyze_trading_risk(trading_data)
            actual_style = self._analyze_trading_style(trading_data)
            
            # Check for inconsistencies
            if self._is_risk_inconsistent(expected_risk, actual_risk):
                validation_results["is_consistent"] = False
                inconsistency = {
                    "type": "risk_level_mismatch",
                    "expected": expected_risk,
                    "actual": actual_risk,
                    "life_path": life_path,
                    "description": f"Chỉ số đường đời {life_path} cho thấy bạn nên có mức rủi ro {expected_risk}, nhưng thực tế giao dịch lại ở mức {actual_risk}"
                }
                validation_results["inconsistencies"].append(inconsistency)
                
                # Generate insight
                insight = self._generate_risk_insight(life_path, expected_risk, actual_risk)
                validation_results["insights"].append(insight)
                
                # Generate recommendation
                recommendation = self._generate_balance_recommendation(life_path, expected_risk, actual_risk)
                validation_results["recommendations"].append(recommendation)
        
        # Check personality vs trading behavior
        personality = numerology_data.get("personality")
        if personality:
            personality_traits = self._get_personality_traits(personality)
            if personality_traits:
                trading_behavior = self._analyze_trading_behavior(trading_data)
                personality_consistency = self._check_personality_consistency(personality_traits, trading_behavior)
                
                if not personality_consistency["is_consistent"]:
                    validation_results["is_consistent"] = False
                    validation_results["inconsistencies"].extend(personality_consistency["inconsistencies"])
                    validation_results["insights"].extend(personality_consistency["insights"])
                    validation_results["recommendations"].extend(personality_consistency["recommendations"])
        
        # Check balance number vs emotional control
        balance = numerology_data.get("balance")
        if balance:
            emotional_control = self._analyze_emotional_control(trading_data)
            balance_consistency = self._check_balance_consistency(balance, emotional_control)
            
            if not balance_consistency["is_consistent"]:
                validation_results["is_consistent"] = False
                validation_results["inconsistencies"].extend(balance_consistency["inconsistencies"])
                validation_results["insights"].extend(balance_consistency["insights"])
                validation_results["recommendations"].extend(balance_consistency["recommendations"])
        
        return validation_results
    
    def _analyze_trading_risk(self, trading_data: Dict[str, Any]) -> str:
        """Analyze actual trading risk level from trading data."""
        max_drawdown = trading_data.get("max_drawdown_pct", 0)
        max_consecutive_losses = trading_data.get("max_consecutive_losses", 0)
        avg_profit_per_trade = trading_data.get("avg_profit_per_trade", 0)
        
        if max_drawdown > 20 or max_consecutive_losses > 5:
            return "high"
        elif max_drawdown > 10 or max_consecutive_losses > 3:
            return "medium"
        else:
            return "low"
    
    def _analyze_trading_style(self, trading_data: Dict[str, Any]) -> str:
        """Analyze actual trading style from trading data."""
        rapid_fire_ratio = trading_data.get("behavioral", {}).get("rapid_fire_ratio", 0)
        avg_trades_per_day = trading_data.get("risk_kpi", {}).get("avgTradesPerDay", 0)
        
        if rapid_fire_ratio > 0.3 or avg_trades_per_day > 10:
            return "aggressive"
        elif rapid_fire_ratio > 0.1 or avg_trades_per_day > 5:
            return "moderate"
        else:
            return "conservative"
    
    def _is_risk_inconsistent(self, expected: str, actual: str) -> bool:
        """Check if risk levels are inconsistent."""
        risk_levels = {"low": 1, "medium": 2, "high": 3}
        expected_level = risk_levels.get(expected, 2)
        actual_level = risk_levels.get(actual, 2)
        
        # Consider inconsistent if difference is more than 1 level
        return abs(expected_level - actual_level) > 1
    
    def _generate_risk_insight(self, life_path: int, expected: str, actual: str) -> str:
        """Generate insight about risk level mismatch."""
        if expected == "low" and actual == "high":
            return f"Chỉ số đường đời {life_path} cho thấy bạn nên giao dịch cẩn trọng, nhưng thực tế bạn đang chấp nhận rủi ro cao. Điều này có thể dẫn đến stress và mất cân bằng."
        elif expected == "high" and actual == "low":
            return f"Chỉ số đường đời {life_path} cho thấy bạn có thể chấp nhận rủi ro cao, nhưng thực tế bạn đang giao dịch quá cẩn trọng. Bạn có thể đang bỏ lỡ cơ hội."
        else:
            return f"Chỉ số đường đời {life_path} và phong cách giao dịch hiện tại có sự khác biệt về mức độ rủi ro."
    
    def _generate_balance_recommendation(self, life_path: int, expected: str, actual: str) -> str:
        """Generate recommendation to balance risk levels."""
        if expected == "low" and actual == "high":
            return f"Để cân bằng với chỉ số đường đời {life_path}, hãy giảm khối lượng giao dịch và tăng stop loss. Tập trung vào chất lượng thay vì số lượng lệnh."
        elif expected == "high" and actual == "low":
            return f"Để phát huy tiềm năng của chỉ số đường đời {life_path}, hãy tăng dần khối lượng giao dịch và chấp nhận rủi ro có kiểm soát."
        else:
            return f"Xem xét điều chỉnh phong cách giao dịch để phù hợp hơn với chỉ số đường đời {life_path}."
    
    def _get_personality_traits(self, personality: int) -> List[str]:
        """Get personality traits based on personality number."""
        # Simplified mapping - in practice, this would be more comprehensive
        personality_mapping = {
            1: ["độc lập", "lãnh đạo"],
            2: ["hợp tác", "nhạy cảm"],
            3: ["sáng tạo", "giao tiếp"],
            4: ["ổn định", "thực tế"],
            5: ["thay đổi", "phiêu lưu"],
            6: ["trách nhiệm", "nuôi dưỡng"],
            7: ["phân tích", "tâm linh"],
            8: ["quyền lực", "vật chất"],
            9: ["nhân đạo", "hoàn thiện"]
        }
        return personality_mapping.get(personality, [])
    
    def _analyze_trading_behavior(self, trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trading behavior patterns."""
        return {
            "rapid_fire_ratio": trading_data.get("behavioral", {}).get("rapid_fire_ratio", 0),
            "revenge_trades": trading_data.get("behavioral", {}).get("revenge_trades", 0),
            "avg_trades_per_day": trading_data.get("risk_kpi", {}).get("avgTradesPerDay", 0),
            "max_consecutive_losses": trading_data.get("max_consecutive_losses", 0)
        }
    
    def _check_personality_consistency(self, traits: List[str], behavior: Dict[str, Any]) -> Dict[str, Any]:
        """Check consistency between personality traits and trading behavior."""
        result = {
            "is_consistent": True,
            "inconsistencies": [],
            "insights": [],
            "recommendations": []
        }
        
        # Check for rapid fire behavior vs personality
        if "cẩn trọng" in traits and behavior["rapid_fire_ratio"] > 0.2:
            result["is_consistent"] = False
            result["inconsistencies"].append({
                "type": "personality_behavior_mismatch",
                "trait": "cẩn trọng",
                "behavior": "rapid_fire_trading",
                "description": "Bạn có tính cách cẩn trọng nhưng lại giao dịch nhanh, điều này có thể dẫn đến quyết định thiếu suy nghĩ."
            })
            result["insights"].append("Tính cách cẩn trọng của bạn đang bị xung đột với phong cách giao dịch nhanh.")
            result["recommendations"].append("Hãy dành thời gian phân tích kỹ lưỡng trước khi vào lệnh, phù hợp với tính cách cẩn trọng của bạn.")
        
        # Check for revenge trading vs personality
        if "cân bằng" in traits and behavior["revenge_trades"] > 0:
            result["is_consistent"] = False
            result["inconsistencies"].append({
                "type": "personality_behavior_mismatch",
                "trait": "cân bằng",
                "behavior": "revenge_trading",
                "description": "Bạn có tính cách cân bằng nhưng lại có xu hướng giao dịch trả thù, điều này mâu thuẫn với bản chất của bạn."
            })
            result["insights"].append("Tính cách cân bằng của bạn đang bị ảnh hưởng bởi cảm xúc giao dịch.")
            result["recommendations"].append("Hãy duy trì sự cân bằng bằng cách không để cảm xúc chi phối quyết định giao dịch.")
        
        return result
    
    def _analyze_emotional_control(self, trading_data: Dict[str, Any]) -> str:
        """Analyze emotional control from trading data."""
        max_consecutive_losses = trading_data.get("max_consecutive_losses", 0)
        revenge_trades = trading_data.get("behavioral", {}).get("revenge_trades", 0)
        
        if max_consecutive_losses > 5 or revenge_trades > 0:
            return "poor"
        elif max_consecutive_losses > 3:
            return "moderate"
        else:
            return "good"
    
    def _check_balance_consistency(self, balance: int, emotional_control: str) -> Dict[str, Any]:
        """Check consistency between balance number and emotional control."""
        result = {
            "is_consistent": True,
            "inconsistencies": [],
            "insights": [],
            "recommendations": []
        }
        
        # Balance numbers 1-4 typically indicate good emotional control
        expected_control = "good" if balance <= 4 else "moderate"
        
        if emotional_control == "poor" and expected_control in ["good", "moderate"]:
            result["is_consistent"] = False
            result["inconsistencies"].append({
                "type": "balance_emotional_mismatch",
                "balance_number": balance,
                "expected_control": expected_control,
                "actual_control": emotional_control,
                "description": f"Chỉ số cân bằng {balance} cho thấy bạn có khả năng kiểm soát cảm xúc tốt, nhưng thực tế giao dịch lại cho thấy kiểm soát cảm xúc kém."
            })
            result["insights"].append(f"Chỉ số cân bằng {balance} của bạn chưa được phát huy đầy đủ trong giao dịch.")
            result["recommendations"].append("Hãy rèn luyện khả năng kiểm soát cảm xúc để phát huy tiềm năng của chỉ số cân bằng.")
        
        return result
    
    def generate_comprehensive_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate a comprehensive validation report."""
        if validation_results["is_consistent"]:
            report = "✅ **TÍNH NHẤT QUÁN CAO**\n\n"
            report += "Phong cách giao dịch của bạn hoàn toàn phù hợp với các chỉ số thần số học.\n"
            report += "Hãy tiếp tục duy trì sự nhất quán này để đạt hiệu quả tối ưu."
        else:
            report = "⚠️ **PHÁT HIỆN SỰ KHÔNG NHẤT QUÁN**\n\n"
            
            # Add inconsistencies
            for inconsistency in validation_results["inconsistencies"]:
                report += f"**{inconsistency['type'].replace('_', ' ').title()}:**\n"
                report += f"{inconsistency['description']}\n\n"
            
            # Add insights
            if validation_results["insights"]:
                report += "**NHẬN ĐỊNH:**\n"
                for insight in validation_results["insights"]:
                    report += f"• {insight}\n"
                report += "\n"
            
            # Add recommendations
            if validation_results["recommendations"]:
                report += "**KHUYẾN NGHỊ CÂN BẰNG:**\n"
                for recommendation in validation_results["recommendations"]:
                    report += f"• {recommendation}\n"
        
        return report
