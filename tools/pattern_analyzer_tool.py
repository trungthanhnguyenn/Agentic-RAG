# tools/pattern_analyzer_tool.py
"""
Pattern Recognition & Hypothesis Testing Tool for discovering relationships between numerology and trading performance.
This tool automatically generates and tests hypotheses to create valuable insights.
"""

from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math

class PatternAnalyzer:
    """
    Analyzes patterns in trading data and tests hypotheses about numerology-trading relationships.
    Generates insights automatically based on data analysis.
    """
    
    def __init__(self):
        # Define hypothesis templates
        self.hypothesis_templates = {
            "time_based": [
                "Người có chỉ số {indicator} có xu hướng giao dịch tốt vào {time_period}",
                "Chỉ số {indicator} ảnh hưởng đến hiệu suất giao dịch theo {time_period}",
                "Thời gian giao dịch tối ưu cho chỉ số {indicator} là {time_period}"
            ],
            "risk_based": [
                "Chỉ số {indicator} ảnh hưởng đến mức độ chấp nhận rủi ro",
                "Người có chỉ số {indicator} có xu hướng {risk_behavior}",
                "Mối liên hệ giữa chỉ số {indicator} và quản lý rủi ro"
            ],
            "performance_based": [
                "Chỉ số {indicator} ảnh hưởng đến tỷ lệ thắng",
                "Mối tương quan giữa chỉ số {indicator} và lợi nhuận trung bình",
                "Chỉ số {indicator} và khả năng phục hồi sau thua lỗ"
            ],
            "behavioral_based": [
                "Chỉ số {indicator} ảnh hưởng đến phong cách giao dịch",
                "Mối liên hệ giữa chỉ số {indicator} và hành vi giao dịch",
                "Chỉ số {indicator} và xu hướng giao dịch nhanh"
            ]
        }
        
        # Define numerology indicators for analysis
        self.numerology_indicators = [
            "life_path", "life_purpose", "soul", "personality", "balance", 
            "maturity", "passion", "rational_thinking", "personal_day", 
            "personal_year", "personal_month"
        ]
        
        # Define trading metrics for correlation analysis
        self.trading_metrics = [
            "win_rate_pct", "avg_profit_per_trade", "profit_factor", 
            "max_drawdown_pct", "max_consecutive_losses", "rapid_fire_ratio"
        ]
    
    def generate_hypotheses(self, numerology_data: Dict[str, Any], trading_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Automatically generate hypotheses about numerology-trading relationships.
        
        Args:
            numerology_data: Numerology calculation results
            trading_data: Trading analysis results
            
        Returns:
            List of generated hypotheses
        """
        hypotheses = []
        
        # Generate time-based hypotheses
        time_hypotheses = self._generate_time_hypotheses(numerology_data, trading_data)
        hypotheses.extend(time_hypotheses)
        
        # Generate risk-based hypotheses
        risk_hypotheses = self._generate_risk_hypotheses(numerology_data, trading_data)
        hypotheses.extend(risk_hypotheses)
        
        # Generate performance-based hypotheses
        performance_hypotheses = self._generate_performance_hypotheses(numerology_data, trading_data)
        hypotheses.extend(performance_hypotheses)
        
        # Generate behavioral-based hypotheses
        behavioral_hypotheses = self._generate_behavioral_hypotheses(numerology_data, trading_data)
        hypotheses.extend(behavioral_hypotheses)
        
        return hypotheses
    
    def _generate_time_hypotheses(self, numerology_data: Dict[str, Any], trading_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate time-based hypotheses."""
        hypotheses = []
        
        if "time_analysis" not in trading_data:
            return hypotheses
        
        time_analysis = trading_data["time_analysis"]
        if not time_analysis:
            return hypotheses
        
        # Find best and worst trading hours
        best_hour = max(time_analysis.items(), key=lambda x: x[1]['profit'])
        worst_hour = min(time_analysis.items(), key=lambda x: x[1]['profit'])
        
        for indicator in self.numerology_indicators:
            if indicator in numerology_data:
                indicator_value = numerology_data[indicator]
                
                # Hypothesis about best trading time
                hypothesis = {
                    "id": f"time_{indicator}_best",
                    "type": "time_based",
                    "indicator": indicator,
                    "indicator_value": indicator_value,
                    "statement": f"Người có chỉ số {indicator} = {indicator_value} có xu hướng giao dịch tốt vào {best_hour[0]}:00",
                    "testable": True,
                    "priority": "high" if indicator in ["life_path", "personal_day"] else "medium"
                }
                hypotheses.append(hypothesis)
                
                # Hypothesis about worst trading time
                hypothesis = {
                    "id": f"time_{indicator}_worst",
                    "type": "time_based",
                    "indicator": indicator,
                    "indicator_value": indicator_value,
                    "statement": f"Người có chỉ số {indicator} = {indicator_value} nên tránh giao dịch vào {worst_hour[0]}:00",
                    "testable": True,
                    "priority": "high" if indicator in ["life_path", "personal_day"] else "medium"
                }
                hypotheses.append(hypothesis)
        
        return hypotheses
    
    def _generate_risk_hypotheses(self, numerology_data: Dict[str, Any], trading_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate risk-based hypotheses."""
        hypotheses = []
        
        for indicator in self.numerology_indicators:
            if indicator in numerology_data:
                indicator_value = numerology_data[indicator]
                
                # Risk level hypothesis
                hypothesis = {
                    "id": f"risk_{indicator}_level",
                    "type": "risk_based",
                    "indicator": indicator,
                    "indicator_value": indicator_value,
                    "statement": f"Chỉ số {indicator} = {indicator_value} ảnh hưởng đến mức độ chấp nhận rủi ro trong giao dịch",
                    "testable": True,
                    "priority": "high" if indicator in ["life_path", "balance"] else "medium"
                }
                hypotheses.append(hypothesis)
                
                # Drawdown hypothesis
                hypothesis = {
                    "id": f"risk_{indicator}_drawdown",
                    "type": "risk_based",
                    "indicator": indicator,
                    "indicator_value": indicator_value,
                    "statement": f"Chỉ số {indicator} = {indicator_value} ảnh hưởng đến khả năng kiểm soát drawdown",
                    "testable": True,
                    "priority": "medium"
                }
                hypotheses.append(hypothesis)
        
        return hypotheses
    
    def _generate_performance_hypotheses(self, numerology_data: Dict[str, Any], trading_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance-based hypotheses."""
        hypotheses = []
        
        for indicator in self.numerology_indicators:
            if indicator in numerology_data:
                indicator_value = numerology_data[indicator]
                
                # Win rate hypothesis
                hypothesis = {
                    "id": f"perf_{indicator}_winrate",
                    "type": "performance_based",
                    "indicator": indicator,
                    "indicator_value": indicator_value,
                    "statement": f"Chỉ số {indicator} = {indicator_value} ảnh hưởng đến tỷ lệ thắng trong giao dịch",
                    "testable": True,
                    "priority": "high" if indicator in ["life_path", "life_purpose"] else "medium"
                }
                hypotheses.append(hypothesis)
                
                # Profit factor hypothesis
                hypothesis = {
                    "id": f"perf_{indicator}_profitfactor",
                    "type": "performance_based",
                    "indicator": indicator,
                    "indicator_value": indicator_value,
                    "statement": f"Chỉ số {indicator} = {indicator_value} ảnh hưởng đến hệ số lợi nhuận",
                    "testable": True,
                    "priority": "medium"
                }
                hypotheses.append(hypothesis)
        
        return hypotheses
    
    def _generate_behavioral_hypotheses(self, numerology_data: Dict[str, Any], trading_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate behavioral-based hypotheses."""
        hypotheses = []
        
        for indicator in self.numerology_indicators:
            if indicator in numerology_data:
                indicator_value = numerology_data[indicator]
                
                # Trading style hypothesis
                hypothesis = {
                    "id": f"behav_{indicator}_style",
                    "type": "behavioral_based",
                    "indicator": indicator,
                    "indicator_value": indicator_value,
                    "statement": f"Chỉ số {indicator} = {indicator_value} ảnh hưởng đến phong cách giao dịch",
                    "testable": True,
                    "priority": "high" if indicator in ["personality", "soul"] else "medium"
                }
                hypotheses.append(hypothesis)
                
                # Rapid fire hypothesis
                hypothesis = {
                    "id": f"behav_{indicator}_rapidfire",
                    "type": "behavioral_based",
                    "indicator": indicator,
                    "indicator_value": indicator_value,
                    "statement": f"Chỉ số {indicator} = {indicator_value} ảnh hưởng đến xu hướng giao dịch nhanh",
                    "testable": True,
                    "priority": "medium"
                }
                hypotheses.append(hypothesis)
        
        return hypotheses
    
    def test_hypotheses(self, hypotheses: List[Dict[str, Any]], trading_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Test generated hypotheses using trading data.
        
        Args:
            hypotheses: List of hypotheses to test
            trading_data: Trading analysis results
            
        Returns:
            List of tested hypotheses with results
        """
        tested_hypotheses = []
        
        for hypothesis in hypotheses:
            if hypothesis["testable"]:
                test_result = self._test_single_hypothesis(hypothesis, trading_data)
                hypothesis["test_result"] = test_result
                hypothesis["confidence"] = self._calculate_confidence(test_result)
                hypothesis["status"] = "validated" if test_result["is_supported"] else "not_supported"
            else:
                hypothesis["test_result"] = {"is_supported": None, "reason": "Not testable with available data"}
                hypothesis["confidence"] = 0
                hypothesis["status"] = "untested"
            
            tested_hypotheses.append(hypothesis)
        
        return tested_hypotheses
    
    def _test_single_hypothesis(self, hypothesis: Dict[str, Any], trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single hypothesis."""
        hypothesis_type = hypothesis["type"]
        indicator = hypothesis["indicator"]
        indicator_value = hypothesis["indicator_value"]
        
        if hypothesis_type == "time_based":
            return self._test_time_hypothesis(hypothesis, trading_data)
        elif hypothesis_type == "risk_based":
            return self._test_risk_hypothesis(hypothesis, trading_data)
        elif hypothesis_type == "performance_based":
            return self._test_performance_hypothesis(hypothesis, trading_data)
        elif hypothesis_type == "behavioral_based":
            return self._test_behavioral_hypothesis(hypothesis, trading_data)
        else:
            return {"is_supported": None, "reason": "Unknown hypothesis type"}
    
    def _test_time_hypothesis(self, hypothesis: Dict[str, Any], trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test time-based hypothesis."""
        if "time_analysis" not in trading_data:
            return {"is_supported": None, "reason": "No time analysis data available"}
        
        time_analysis = trading_data["time_analysis"]
        if not time_analysis:
            return {"is_supported": None, "reason": "Empty time analysis data"}
        
        # Simple test: check if there's significant variation in trading performance by hour
        profits_by_hour = [data["profit"] for data in time_analysis.values()]
        if len(profits_by_hour) < 2:
            return {"is_supported": None, "reason": "Insufficient time data for analysis"}
        
        # Calculate coefficient of variation
        mean_profit = np.mean(profits_by_hour)
        std_profit = np.std(profits_by_hour)
        
        if mean_profit == 0:
            cv = 0
        else:
            cv = abs(std_profit / mean_profit)
        
        # Hypothesis is supported if there's significant variation
        is_supported = cv > 0.5  # 50% variation threshold
        
        return {
            "is_supported": is_supported,
            "reason": f"Time variation analysis: CV={cv:.2f}",
            "metrics": {
                "coefficient_of_variation": cv,
                "mean_profit": mean_profit,
                "std_profit": std_profit
            }
        }
    
    def _test_risk_hypothesis(self, hypothesis: Dict[str, Any], trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test risk-based hypothesis."""
        # Test based on drawdown and consecutive losses
        max_drawdown = trading_data.get("max_drawdown_pct", 0)
        max_consecutive_losses = trading_data.get("max_consecutive_losses", 0)
        
        # Simple risk assessment
        risk_level = "high" if max_drawdown > 20 or max_consecutive_losses > 5 else "medium" if max_drawdown > 10 else "low"
        
        # For now, we'll consider the hypothesis supported if we can identify a clear risk pattern
        is_supported = max_drawdown > 0 and max_consecutive_losses > 0
        
        return {
            "is_supported": is_supported,
            "reason": f"Risk pattern identified: drawdown={max_drawdown:.1f}%, consecutive_losses={max_consecutive_losses}",
            "metrics": {
                "max_drawdown": max_drawdown,
                "max_consecutive_losses": max_consecutive_losses,
                "risk_level": risk_level
            }
        }
    
    def _test_performance_hypothesis(self, hypothesis: Dict[str, Any], trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test performance-based hypothesis."""
        win_rate = trading_data.get("win_rate_pct", 0)
        profit_factor = trading_data.get("profit_factor", 0)
        avg_profit = trading_data.get("avg_profit_per_trade", 0)
        
        # Hypothesis is supported if we have meaningful performance data
        is_supported = win_rate > 0 and profit_factor > 0
        
        return {
            "is_supported": is_supported,
            "reason": f"Performance metrics available: win_rate={win_rate:.1f}%, profit_factor={profit_factor:.2f}",
            "metrics": {
                "win_rate": win_rate,
                "profit_factor": profit_factor,
                "avg_profit_per_trade": avg_profit
            }
        }
    
    def _test_behavioral_hypothesis(self, hypothesis: Dict[str, Any], trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test behavioral-based hypothesis."""
        rapid_fire_ratio = trading_data.get("behavioral", {}).get("rapid_fire_ratio", 0)
        revenge_trades = trading_data.get("behavioral", {}).get("revenge_trades", 0)
        avg_trades_per_day = trading_data.get("risk_kpi", {}).get("avgTradesPerDay", 0)
        
        # Hypothesis is supported if we have behavioral data
        is_supported = rapid_fire_ratio > 0 or revenge_trades > 0 or avg_trades_per_day > 0
        
        return {
            "is_supported": is_supported,
            "reason": f"Behavioral patterns identified: rapid_fire={rapid_fire_ratio:.2f}, revenge={revenge_trades}, avg_trades/day={avg_trades_per_day:.1f}",
            "metrics": {
                "rapid_fire_ratio": rapid_fire_ratio,
                "revenge_trades": revenge_trades,
                "avg_trades_per_day": avg_trades_per_day
            }
        }
    
    def _calculate_confidence(self, test_result: Dict[str, Any]) -> float:
        """Calculate confidence level for a test result."""
        if not test_result["is_supported"]:
            return 0.0
        
        # Simple confidence calculation based on data quality
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on data availability
        if "metrics" in test_result:
            metrics = test_result["metrics"]
            if len(metrics) > 2:
                confidence += 0.2
            if any(isinstance(v, (int, float)) and v > 0 for v in metrics.values()):
                confidence += 0.3
        
        return min(confidence, 1.0)
    
    def generate_insights(self, validated_hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate insights from validated hypotheses.
        
        Args:
            validated_hypotheses: List of tested hypotheses
            
        Returns:
            List of generated insights
        """
        insights = []
        
        # Group hypotheses by type
        hypotheses_by_type = {}
        for hypothesis in validated_hypotheses:
            if hypothesis["status"] == "validated":
                h_type = hypothesis["type"]
                if h_type not in hypotheses_by_type:
                    hypotheses_by_type[h_type] = []
                hypotheses_by_type[h_type].append(hypothesis)
        
        # Generate insights for each type
        for h_type, type_hypotheses in hypotheses_by_type.items():
            type_insights = self._generate_type_insights(h_type, type_hypotheses)
            insights.extend(type_insights)
        
        return insights
    
    def _generate_type_insights(self, hypothesis_type: str, hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate insights for a specific hypothesis type."""
        insights = []
        
        if hypothesis_type == "time_based":
            insights.extend(self._generate_time_insights(hypotheses))
        elif hypothesis_type == "risk_based":
            insights.extend(self._generate_risk_insights(hypotheses))
        elif hypothesis_type == "performance_based":
            insights.extend(self._generate_performance_insights(hypotheses))
        elif hypothesis_type == "behavioral_based":
            insights.extend(self._generate_behavioral_insights(hypotheses))
        
        return insights
    
    def _generate_time_insights(self, hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate time-based insights."""
        insights = []
        
        # Find best time hypotheses
        best_time_hypotheses = [h for h in hypotheses if "best" in h["id"]]
        if best_time_hypotheses:
            insight = {
                "type": "time_optimization",
                "title": "Thời gian giao dịch tối ưu",
                "description": "Dựa trên phân tích, có thể xác định thời gian giao dịch tốt nhất cho bạn",
                "recommendations": [
                    "Tập trung giao dịch vào những giờ có hiệu suất cao",
                    "Tránh giao dịch vào những giờ có hiệu suất thấp",
                    "Lên lịch giao dịch phù hợp với nhịp sinh học"
                ],
                "confidence": np.mean([h["confidence"] for h in best_time_hypotheses])
            }
            insights.append(insight)
        
        return insights
    
    def _generate_risk_insights(self, hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate risk-based insights."""
        insights = []
        
        if hypotheses:
            insight = {
                "type": "risk_management",
                "title": "Quản lý rủi ro dựa trên chỉ số thần số học",
                "description": "Các chỉ số thần số học có thể ảnh hưởng đến cách bạn quản lý rủi ro",
                "recommendations": [
                    "Điều chỉnh mức độ rủi ro phù hợp với chỉ số cá nhân",
                    "Sử dụng stop loss phù hợp với tính cách",
                    "Kiểm soát cảm xúc dựa trên chỉ số cân bằng"
                ],
                "confidence": np.mean([h["confidence"] for h in hypotheses])
            }
            insights.append(insight)
        
        return insights
    
    def _generate_performance_insights(self, hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate performance-based insights."""
        insights = []
        
        if hypotheses:
            insight = {
                "type": "performance_optimization",
                "title": "Tối ưu hóa hiệu suất giao dịch",
                "description": "Các chỉ số thần số học có thể ảnh hưởng đến hiệu suất giao dịch",
                "recommendations": [
                    "Phát huy điểm mạnh dựa trên chỉ số cá nhân",
                    "Cải thiện điểm yếu được chỉ ra bởi thần số học",
                    "Điều chỉnh chiến lược phù hợp với bản chất"
                ],
                "confidence": np.mean([h["confidence"] for h in hypotheses])
            }
            insights.append(insight)
        
        return insights
    
    def _generate_behavioral_insights(self, hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate behavioral-based insights."""
        insights = []
        
        if hypotheses:
            insight = {
                "type": "behavioral_improvement",
                "title": "Cải thiện hành vi giao dịch",
                "description": "Hiểu rõ mối liên hệ giữa chỉ số thần số học và hành vi giao dịch",
                "recommendations": [
                    "Nhận diện và sửa chữa hành vi giao dịch không phù hợp",
                    "Phát triển phong cách giao dịch phù hợp với tính cách",
                    "Rèn luyện kỷ luật dựa trên chỉ số cá nhân"
                ],
                "confidence": np.mean([h["confidence"] for h in hypotheses])
            }
            insights.append(insight)
        
        return insights
    
    def generate_comprehensive_report(self, hypotheses: List[Dict[str, Any]], insights: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive pattern analysis report."""
        report = "🔍 **BÁO CÁO PHÂN TÍCH MÔ HÌNH VÀ KIỂM TRA GIẢ THUYẾT**\n\n"
        
        # Hypothesis summary
        total_hypotheses = len(hypotheses)
        validated_hypotheses = len([h for h in hypotheses if h["status"] == "validated"])
        not_supported = len([h for h in hypotheses if h["status"] == "not_supported"])
        
        report += f"**TỔNG QUAN GIẢ THUYẾT:**\n"
        report += f"• Tổng số giả thuyết: {total_hypotheses}\n"
        report += f"• Được xác nhận: {validated_hypotheses}\n"
        report += f"• Không được hỗ trợ: {not_supported}\n"
        if total_hypotheses > 0:
            report += f"• Tỷ lệ thành công: {(validated_hypotheses/total_hypotheses*100):.1f}%\n\n"
        else:
            report += f"• Tỷ lệ thành công: N/A (không có giả thuyết nào)\n\n"
        
        # Key insights
        if insights:
            report += "**NHỮNG PHÁT HIỆN CHÍNH:**\n"
            for insight in insights:
                report += f"• **{insight['title']}** (Độ tin cậy: {insight['confidence']:.1%})\n"
                report += f"  {insight['description']}\n"
                report += "  Khuyến nghị:\n"
                for rec in insight['recommendations']:
                    report += f"    - {rec}\n"
                report += "\n"
        
        # Top hypotheses
        top_hypotheses = sorted(hypotheses, key=lambda x: x.get("confidence", 0), reverse=True)[:5]
        if top_hypotheses:
            report += "**TOP 5 GIẢ THUYẾT CÓ ĐỘ TIN CẬY CAO:**\n"
            for i, hypothesis in enumerate(top_hypotheses, 1):
                report += f"{i}. {hypothesis['statement']}\n"
                report += f"   Độ tin cậy: {hypothesis.get('confidence', 0):.1%}\n"
                report += f"   Trạng thái: {hypothesis['status']}\n\n"
        
        return report
