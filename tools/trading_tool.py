# tools/trading_tool.py
import math
import pandas as pd
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

def read_trading_excel(file_path: str) -> pd.DataFrame:
    """
    Read trading history from Excel file and return a cleaned DataFrame.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Cleaned DataFrame with standardized column names
    """
    try:
        # Read Excel file
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.xls'):
            df = pd.read_excel(file_path, engine='xlrd')
        else:
            raise ValueError("File must be .xlsx or .xls format")
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Standardize column names to match expected format
        column_mapping = {
            'symbol': ['symbol', 'cặp tiền', 'cặp', 'pair', 'instrument'],
            'side': ['side', 'hướng', 'direction', 'loại', 'type'],
            'close_time': ['close_time', 'thời gian đóng', 'ngày đóng', 'date', 'time'],
            'net_profit': ['net_profit', 'lợi nhuận ròng', 'pnl', 'profit', 'lãi lỗ'],
            'profit_gross': ['profit_gross', 'lợi nhuận gộp', 'gross profit', 'lãi gộp'],
            'commission': ['commission', 'phí giao dịch', 'phí', 'fee'],
            'swap': ['swap', 'phí qua đêm', 'phí swap', 'overnight'],
            'balance_after': ['balance_after', 'số dư sau', 'balance', 'số dư'],
            'pips': ['pips', 'điểm', 'pip'],
            'volume_lots_closed': ['volume_lots_closed', 'khối lượng đóng', 'volume', 'lot'],
            'quantity_closed': ['quantity_closed', 'số lượng đóng', 'quantity', 'số lượng'],
            'open_price': ['open_price', 'giá mở', 'giá vào lệnh', 'entry price'],
            'close_price': ['close_price', 'giá đóng', 'giá thoát lệnh', 'exit price']
        }
        
        # Apply column mapping
        for standard_name, possible_names in column_mapping.items():
            for possible_name in possible_names:
                if possible_name in df.columns:
                    if standard_name not in df.columns:
                        df[standard_name] = df[possible_name]
                    break
        
        # Validate required columns
        required_columns = ['symbol', 'side', 'close_time', 'net_profit']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # print(f"✅ Successfully loaded {len(df)} trades from {file_path}")
        # print(f"📊 Available columns: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        raise

def analyze_user_question(question: str) -> Dict[str, Any]:
    """
    Analyze user question to determine what analysis is needed.
    
    Args:
        question: User's question in Vietnamese or English
        
    Returns:
        Dictionary with analysis requirements
    """
    question_lower = question.lower()
    
    analysis_needs = {
        'overview': False,
        'performance': False,
        'risk': False,
        'timing': False,
        'symbols': False,
        'behavioral': False,
        'monthly': False,
        'specific_metrics': []
    }
    
    # Overview analysis
    if any(word in question_lower for word in ['tổng quan', 'overview', 'tổng kết', 'summary']):
        analysis_needs['overview'] = True
    
    # Performance analysis
    if any(word in question_lower for word in ['hiệu suất', 'performance', 'thắng thua', 'win rate', 'lợi nhuận', 'profit']):
        analysis_needs['performance'] = True
    
    # Risk analysis
    if any(word in question_lower for word in ['rủi ro', 'risk', 'drawdown', 'thua lỗ', 'loss', 'consecutive']):
        analysis_needs['risk'] = True
    
    # Timing analysis
    if any(word in question_lower for word in ['thời gian', 'timing', 'giờ', 'hour', 'ngày', 'day', 'tháng', 'month']):
        analysis_needs['timing'] = True
    
    # Symbol analysis
    if any(word in question_lower for word in ['cặp tiền', 'symbol', 'pair', 'instrument', 'forex', 'gold', 'xauusd']):
        analysis_needs['symbols'] = True
    
    # Behavioral analysis
    if any(word in question_lower for word in ['hành vi', 'behavior', 'rapid fire', 'revenge', 'tâm lý', 'psychology']):
        analysis_needs['behavioral'] = True
    
    # Monthly analysis
    if any(word in question_lower for word in ['tháng', 'monthly', 'theo tháng', 'monthly performance']):
        analysis_needs['monthly'] = True
    
    # Specific metrics
    specific_metrics = []
    if 'win rate' in question_lower or 'tỷ lệ thắng' in question_lower:
        specific_metrics.append('win_rate_pct')
    if 'profit factor' in question_lower or 'hệ số lợi nhuận' in question_lower:
        specific_metrics.append('profit_factor')
    if 'drawdown' in question_lower or 'sụt giảm' in question_lower:
        specific_metrics.append('max_drawdown_pct')
    if 'expectancy' in question_lower or 'kỳ vọng' in question_lower:
        specific_metrics.append('avg_profit_per_trade')
    if 'pips' in question_lower:
        specific_metrics.append('total_pips')
    
    analysis_needs['specific_metrics'] = specific_metrics
    
    return analysis_needs

def generate_focused_report(result: Dict[str, Any], analysis_needs: Dict[str, Any]) -> str:
    """
    Generate a focused report based on user's specific needs.
    
    Args:
        result: Full trading analysis result
        analysis_needs: What the user wants to know
        
    Returns:
        Focused report string
    """
    # Ensure all keys exist with default values
    analysis_needs = {
        'overview': False,
        'performance': False,
        'risk': False,
        'timing': False,
        'symbols': False,
        'behavioral': False,
        'monthly': False,
        'specific_metrics': [],
        **analysis_needs  # Override with provided values
    }
    
    report_parts = []
    
    # Overview section
    if analysis_needs['overview']:
        report_parts.append("📊 TỔNG QUAN GIAO DỊCH")
        report_parts.append(f"• Tổng số lệnh: {result['trades']}")
        report_parts.append(f"• Tổng lợi nhuận: {result['net_profit']:,.2f}")
        report_parts.append(f"• Tỷ lệ thắng: {result['win_rate_pct']}%")
        report_parts.append(f"• Lợi nhuận trung bình/lệnh: {result['avg_profit_per_trade']:,.2f}")
    
    # Performance section
    if analysis_needs['performance']:
        report_parts.append("\n🎯 PHÂN TÍCH HIỆU SUẤT")
        report_parts.append(f"• Lệnh thắng trung bình: {result['avg_profit_win']:,.2f}")
        report_parts.append(f"• Lệnh thua trung bình: {result['avg_loss_loss']:,.2f}")
        report_parts.append(f"• Hệ số lợi nhuận: {result['profit_factor']}")
        report_parts.append(f"• Lệnh thắng nhất: {result['best_trade']:,.2f}")
        report_parts.append(f"• Lệnh thua nhất: {result['worst_trade']:,.2f}")
    
    # Risk section
    if analysis_needs['risk']:
        report_parts.append("\n⚠️ PHÂN TÍCH RỦI RO")
        report_parts.append(f"• Sụt giảm tối đa: {result['max_drawdown_pct']}%")
        report_parts.append(f"• Số lệnh thua liên tiếp tối đa: {result['max_consecutive_losses']}")
        report_parts.append(f"• Giới hạn rủi ro/lệnh: {result['risk_kpi']['max_risk_per_trade']:,.2f}")
        report_parts.append(f"• Giới hạn thua lỗ/ngày: {result['risk_kpi']['limit_daily_stop']:,.2f}")
    
    # Timing section
    if analysis_needs['timing']:
        report_parts.append("\n⏰ PHÂN TÍCH THỜI GIAN")
        if result['time_analysis']:
            best_hour = max(result['time_analysis'].items(), key=lambda x: x[1]['profit'])
            worst_hour = min(result['time_analysis'].items(), key=lambda x: x[1]['profit'])
            report_parts.append(f"• Giờ giao dịch tốt nhất: {best_hour[0]}:00 (lợi nhuận: {best_hour[1]['profit']:,.2f})")
            report_parts.append(f"• Giờ giao dịch kém nhất: {worst_hour[0]}:00 (lợi nhuận: {worst_hour[1]['profit']:,.2f})")
    
    # Symbol section
    if analysis_needs['symbols']:
        report_parts.append("\n💱 PHÂN TÍCH CẶP TIỀN")
        if result['symbol_analysis']:
            best_symbol = max(result['symbol_analysis'].items(), key=lambda x: x[1]['profit'])
            report_parts.append(f"• Cặp tiền tốt nhất: {best_symbol[0]} (lợi nhuận: {best_symbol[1]['profit']:,.2f})")
    
    # Behavioral section
    if analysis_needs['behavioral']:
        report_parts.append("\n🧠 PHÂN TÍCH HÀNH VI")
        report_parts.append(f"• Lệnh rapid fire: {result['behavioral']['rapid_fire_trades']} ({result['behavioral']['rapid_fire_ratio']:.1%})")
        report_parts.append(f"• Lệnh revenge: {result['behavioral']['revenge_trades']}")
    
    # Monthly section
    if analysis_needs['monthly']:
        report_parts.append("\n📅 PHÂN TÍCH THEO THÁNG")
        if result['monthly']:
            monthly_data = result['monthly']
            for i, period in enumerate(monthly_data['periods']):
                report_parts.append(f"• {period}: Lợi nhuận {monthly_data['varpc'][i]:,.2f}, Chỉ số {monthly_data['index'][i]}")
    
    # Specific metrics
    if analysis_needs['specific_metrics']:
        report_parts.append("\n📈 CHỈ SỐ CỤ THỂ")
        for metric in analysis_needs['specific_metrics']:
            if metric in result:
                if metric == 'win_rate_pct':
                    report_parts.append(f"• Tỷ lệ thắng: {result[metric]}%")
                elif metric == 'profit_factor':
                    report_parts.append(f"• Hệ số lợi nhuận: {result[metric]}")
                elif metric == 'max_drawdown_pct':
                    report_parts.append(f"• Sụt giảm tối đa: {result[metric]}%")
                elif metric == 'avg_profit_per_trade':
                    report_parts.append(f"• Lợi nhuận trung bình/lệnh: {result[metric]:,.2f}")
                elif metric == 'total_pips':
                    report_parts.append(f"• Tổng pips: {result[metric]:,.2f}")
    
    # Recommendations
    report_parts.append("\n💡 KHUYẾN NGHỊ")
    if result['avg_profit_per_trade'] <= 0:
        report_parts.append("⚠️ Lợi nhuận trung bình ≤ 0: Cần cải thiện chiến lược")
    else:
        report_parts.append("✅ Lợi nhuận trung bình > 0: Chiến lược đang hiệu quả")
    
    if result['max_consecutive_losses'] >= 5:
        report_parts.append("⚠️ Số lệnh thua liên tiếp ≥ 5: Cần kiểm soát rủi ro tốt hơn")
    elif result['max_consecutive_losses'] <= 2:
        report_parts.append("✅ Số lệnh thua liên tiếp ≤ 2: Kiểm soát rủi ro tốt")
    else:
        report_parts.append("⚠️ Số lệnh thua liên tiếp: Cần theo dõi và cải thiện")
    
    return "\n".join(report_parts)

def get_trading_data_from_excel(file_path: str = None) -> pd.DataFrame:
    """
    Get trading data from Excel file. If no file path provided, look for common locations.
    
    Args:
        file_path: Optional path to Excel file
        
    Returns:
        DataFrame with trading data
    """
    if file_path and os.path.exists(file_path):
        return read_trading_excel(file_path)
    
    # Look for common locations
    common_paths = [
        "trading_data/test_sample.xlsx",
        "data/trading_history.xlsx",
        "trading_history.xlsx",
        "trading_data.xlsx"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"📁 Found trading data at: {path}")
            return read_trading_excel(path)
    
    # If no file found, create sample data for demonstration
    print("⚠️ No trading data file found. Using sample data for demonstration.")
    return pd.DataFrame([
        {"symbol": "XAUUSD", "side": "BUY", "close_time": "01/01/2024 10:00", "net_profit": 50, "commission": -2, "swap": -1},
        {"symbol": "XAUUSD", "side": "SELL", "close_time": "01/01/2024 11:00", "net_profit": -30, "commission": -2, "swap": -1},
    ])

def calculate_trade_index(df: pd.DataFrame):
    """
    Calculate trade index and analytics from user's trade history (per requirements).

    The function is resilient to leading/trailing spaces in column headers and
    expects, at minimum, the following columns (string/numeric accepted):
      - symbol
      - side (values: 'Mua'/'Bán' or 'BUY'/'SELL')
      - close_time (datetime-like string)
      - net_profit (per-trade net P/L)
      - profit_gross (optional)
      - commission
      - swap
      - balance_after (optional, used for alternative DD)
      - pips (optional)
      - volume_lots_closed or quantity_closed (optional, for volume)

    Returns a dictionary including summary, performance, equity/drawdown series,
    time/symbol/side analyses, behavioral metrics, risk KPIs, and chart data.
    """

    # Normalize column names: strip spaces to match the Excel provided
    if hasattr(df, 'columns'):
        df = df.rename(columns={c: c.strip() for c in df.columns})

    # Map Vietnamese side values to English; keep existing if already English
    if 'side' in df.columns:
        df['side'] = df['side'].replace({'Mua': 'BUY', 'Bán': 'SELL'})

    # Parse close_time to datetime and derive hour/day
    if 'close_time' in df.columns:
        df['close_time'] = pd.to_datetime(df['close_time'], errors='coerce', dayfirst=True)
        df['hour'] = df['close_time'].dt.hour
        df['date'] = df['close_time'].dt.date

    # Coerce numeric fields
    numeric_cols = [
        'commission', 'swap', 'profit_gross', 'net_profit', 'balance_after',
        'pips', 'volume_lots_closed', 'quantity_closed', 'open_price', 'close_price'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Determine volume column (optional)
    volume_col = 'volume_lots_closed' if 'volume_lots_closed' in df.columns else (
        'quantity_closed' if 'quantity_closed' in df.columns else None
    )

    # Number of trades
    trades = int(len(df))

    # Totals and fees (use absolute for fees per requirement examples)
    total_commission = float(df['commission'].sum()) if 'commission' in df.columns else 0.0
    total_swap = float(df['swap'].sum()) if 'swap' in df.columns else 0.0
    total_fees = abs(total_commission) + abs(total_swap)

    # Win/Loss partitions
    if 'net_profit' not in df.columns:
        raise KeyError("Expected column 'net_profit' not found")
    win_trades_df = df[df['net_profit'] > 0]
    loss_trades_df = df[df['net_profit'] < 0]
    wins_sum = float(win_trades_df['net_profit'].sum())
    losses_sum = float(loss_trades_df['net_profit'].sum())  # negative number

    win_rate_pct = (len(win_trades_df) / trades * 100.0) if trades > 0 else 0.0
    avg_profit_win = float(win_trades_df['net_profit'].mean()) if not win_trades_df.empty else 0.0
    avg_loss_loss = float(loss_trades_df['net_profit'].mean()) if not loss_trades_df.empty else 0.0

    best_trade = float(df['net_profit'].max()) if trades > 0 else 0.0
    worst_trade = float(df['net_profit'].min()) if trades > 0 else 0.0

    # Expectancy (avg profit per trade)
    expectancy = float(df['net_profit'].mean()) if trades > 0 else 0.0

    # Profit factor based on net profits as per requirement examples
    gross_profit_wins = wins_sum
    gross_loss_losses_abs = abs(losses_sum)
    profit_factor = (gross_profit_wins / gross_loss_losses_abs) if gross_loss_losses_abs > 0 else math.inf

    # Pips
    total_pips = float(df['pips'].sum()) if 'pips' in df.columns else 0.0
    avg_pips_per_trade = float(df['pips'].mean()) if 'pips' in df.columns and trades > 0 else 0.0

    # Equity & Drawdown (using cumulative net_profit per requirement for RB_k)
    equity_rb = df['net_profit'].cumsum().tolist()
    # Drawdown from RB series
    peak = []
    running_peak = -float('inf')
    for val in equity_rb:
        running_peak = max(running_peak, val)
        peak.append(running_peak)
    dd_abs = [p - v for p, v in zip(peak, equity_rb)]
    dd_pct = [((p - v) / p * 100.0) if p != 0 else 0.0 for p, v in zip(peak, equity_rb)]
    max_drawdown_pct = max(dd_pct) if dd_pct else 0.0

    # Alternative DD from balance_after if available (not returned by default)
    # max_equity_bal = df['balance_after'].cummax() if 'balance_after' in df.columns else None

    # Max consecutive losses
    loss_flags = (df['net_profit'] < 0).tolist()
    max_consecutive_losses = 0
    current_streak = 0
    for is_loss in loss_flags:
        if is_loss:
            current_streak += 1
            max_consecutive_losses = max(max_consecutive_losses, current_streak)
        else:
            current_streak = 0

    # Time analysis by hour
    time_analysis = {}
    if 'hour' in df.columns:
        grouped = df.groupby('hour', dropna=True)
        for h, g in grouped:
            time_analysis[int(h)] = {
                'trades': int(len(g)),
                'profit': float(g['net_profit'].sum()),
                'wins': int((g['net_profit'] > 0).sum()),
                'losses': int((g['net_profit'] < 0).sum()),
            }

    # Symbol analysis
    symbol_analysis = {}
    if 'symbol' in df.columns:
        grouped = df.groupby('symbol', dropna=True)
        for sym, g in grouped:
            symbol_analysis[str(sym)] = {
                'trades': int(len(g)),
                'profit': float(g['net_profit'].sum()),
                'volume': float(g[volume_col].sum()) if volume_col and volume_col in g.columns else 0.0,
                'wins': int((g['net_profit'] > 0).sum()),
                'losses': int((g['net_profit'] < 0).sum()),
            }

    # Side analysis
    side_analysis = {}
    if 'side' in df.columns:
        grouped = df.groupby('side', dropna=True)
        for s, g in grouped:
            side_analysis[str(s)] = {
                'trades': int(len(g)),
                'profit': float(g['net_profit'].sum()),
                'volume': float(g[volume_col].sum()) if volume_col and volume_col in g.columns else 0.0,
                'wins': int((g['net_profit'] > 0).sum()),
                'losses': int((g['net_profit'] < 0).sum()),
            }

    # Behavioral analysis (heuristics)
    rapid_fire_trades = 0
    revenge_trades = 0
    rapid_fire_threshold_min = 5
    if 'close_time' in df.columns:
        times = df['close_time'].tolist()
        for i in range(1, len(times)):
            prev_time = times[i - 1]
            curr_time = times[i]
            if pd.notna(prev_time) and pd.notna(curr_time):
                delta_min = (curr_time - prev_time).total_seconds() / 60.0
                if delta_min <= rapid_fire_threshold_min:
                    rapid_fire_trades += 1
    # Revenge trades: định nghĩa theo docs ví dụ → lệnh ngay sau một lệnh lỗ
    for i in range(1, len(df)):
        if df.iloc[i - 1]['net_profit'] < 0:
            revenge_trades += 1
    rapid_fire_ratio = (rapid_fire_trades / trades) if trades > 0 else 0.0

    # Risk/KPI recommendations (simple heuristics based on requirements examples)
    if 'date' in df.columns:
        daily_pnl = df.groupby('date')['net_profit'].sum()
        min_daily_loss = float(daily_pnl.min()) if not daily_pnl.empty else 0.0
        days_count = max(len(daily_pnl), 1)
        avg_trades_per_day = trades / days_count
    else:
        min_daily_loss = 0.0
        avg_trades_per_day = float(trades)

    avg_trade_size = 0.0
    if volume_col and volume_col in df.columns:
        avg_trade_size = float(df[volume_col].mean())

    max_loss = float(df['net_profit'].min()) if trades > 0 else 0.0
    risk_per_trade_limit = round(abs(max_loss) * 0.8, 2)
    daily_stop_limit = round(abs(min_daily_loss) * 0.8, 2)
    max_trades_per_day = int(math.ceil(avg_trades_per_day * 1.5)) if avg_trades_per_day > 0 else 0

    # Monthly table: varpc/dividend/rt/index (gộp theo tháng)
    monthly = []
    if 'close_time' in df.columns:
        df_sorted = df.sort_values('close_time')
        df_sorted['year_month'] = df_sorted['close_time'].dt.to_period('M')

        # Tạo chuỗi số dư cuối kỳ theo trade để suy ra số dư đầu kỳ mỗi tháng
        # balance_after có thể thiếu → bỏ qua RT nếu không có
        month_groups = df_sorted.groupby('year_month', sort=True)
        months = []
        varpc_list = []
        dividend_list = []
        rt_list = []
        index_list = []
        index_value = 100.0

        # Lấy map: số dư cuối kỳ mỗi tháng (trade cuối cùng của tháng)
        last_balance_by_month = month_groups['balance_after'].last() if 'balance_after' in df_sorted.columns else None
        # Lấy số dư đầu kỳ mỗi tháng: số dư cuối kỳ của tháng trước
        prev_month_end_balance = None

        for ym, g in month_groups:
            months.append(str(ym))
            varpc_m = float(g['net_profit'].sum())
            # dividend_m: tổng phí theo tháng (dấu âm) theo ví dụ → dùng -(|commission|+|swap|)
            comm_m = float(g['commission'].abs().sum()) if 'commission' in g.columns else 0.0
            swap_m = float(g['swap'].abs().sum()) if 'swap' in g.columns else 0.0
            dividend_m = -(comm_m + swap_m)

            varpc_list.append(varpc_m)
            dividend_list.append(dividend_m)

            # Tính RT dựa trên số dư đầu kỳ nếu có số dư
            if prev_month_end_balance is None:
                rt_m = None
            else:
                denom = float(prev_month_end_balance)
                if denom and denom != 0:
                    rt_m = (varpc_m - dividend_m) / denom
                else:
                    rt_m = None
            rt_list.append(None if rt_m is None else float(rt_m))

            # Cập nhật chỉ số index
            if rt_m is None:
                index_value = 100.0
            else:
                index_value = index_value * (1.0 + rt_m)
            index_list.append(round(index_value, 2))

            # Cập nhật prev_month_end_balance cho tháng tiếp theo
            if last_balance_by_month is not None:
                prev_month_end_balance = last_balance_by_month.loc[ym]
            else:
                prev_month_end_balance = None

        monthly = {
            'periods': months,
            'varpc': varpc_list,
            'dividend': dividend_list,
            'rt': rt_list,
            'index': index_list,
        }

    # Build result
    result = {
        'trades': trades,
        'net_profit': float(df['net_profit'].sum()),
        # gross_profit: ưu tiên sum(profit_gross) nếu có, nếu không → net_profit + total_fees
        'gross_profit': (float(df['profit_gross'].sum()) if 'profit_gross' in df.columns and df['profit_gross'].notna().any()
                         else float(df['net_profit'].sum()) + total_fees),
        'total_commission': total_commission,
        'total_swap': total_swap,
        'total_fees': total_fees,
        'win_rate_pct': round(win_rate_pct, 2),
        'avg_profit_win': round(avg_profit_win, 2),
        'avg_loss_loss': round(avg_loss_loss, 2),
        'best_trade': best_trade,
        'worst_trade': worst_trade,
        'avg_profit_per_trade': round(expectancy, 2),  # expectancy
        'profit_factor': round(profit_factor, 2) if math.isfinite(profit_factor) else float('inf'),
        'total_pips': round(total_pips, 2),
        'avg_pips_per_trade': round(avg_pips_per_trade, 2),
        'max_drawdown_pct': round(max_drawdown_pct, 2),
        'max_consecutive_losses': max_consecutive_losses,
        'equity': {
            'rb': equity_rb,
            'peak': peak,
            'dd_abs': dd_abs,
            'dd_pct': [round(x, 2) for x in dd_pct],
        },
        'time_analysis': time_analysis,
        'symbol_analysis': symbol_analysis,
        'side_analysis': side_analysis,
        'behavioral': {
            'rapid_fire_trades': rapid_fire_trades,
            'rapid_fire_ratio': round(rapid_fire_ratio, 2),
            'revenge_trades': revenge_trades,
        },
        'risk_kpi': {
            'avgTradesPerDay': round(avg_trades_per_day, 2),
            'max_trades_per_day': max_trades_per_day,
            'maxDailyLoss': round(min_daily_loss, 2),
            'limit_daily_stop': daily_stop_limit,
            'avgTradeSize': round(avg_trade_size, 2),
            'recommended_position_size': round(avg_trade_size, 2),
            'maxLoss': round(max_loss, 2),
            'max_risk_per_trade': risk_per_trade_limit,
        },
        'chart': {
            'labels': list(range(1, trades + 1)),
            'equity': equity_rb,
            'drawdown_pct': [round(x, 2) for x in dd_pct],
        },
        'monthly': monthly,
    }

    return result

# Function to print a beautiful trade report
def print_trade_report(result):
    """Print a beautiful trade report"""
    
    print("=" * 50)
    print("           TRADE REPORT ANALYSIS")
    print("=" * 50)
    
    print(f"Total trades: {result['trades']}")
    print(f"Win rate: {result['win_rate_pct']}%")
    print(f"Average profit/trade: {result['avg_profit_per_trade']}")
    
    print("\n--- DETAIL PROFIT ---")   
    print(f"Best trade: {result['best_trade']}")
    print(f"Worst trade: {result['worst_trade']}")
    print(f"Average profit/winning trade: {result['avg_profit_win']}")
    print(f"Average loss/losing trade: {result['avg_loss_loss']}")
    
    print("\n--- TRANSACTION COSTS ---")
    print(f"Total commission: {result['total_commission']}")
    print(f"Total swap: {result['total_swap']}")
    print(f"Total fees: {result['total_fees']}")
    
    print("\n--- RISK ---")
    print(f"Maximum drawdown: {result['max_drawdown_pct']}%")
    print(f"Maximum consecutive losses: {result['max_consecutive_losses']}")
    
    print("\n--- EVALUATION ---")
    print(result['avg_profit_per_trade'])
    if result['avg_profit_per_trade'] <= 0:
        print("⚠️  Expectancy/trade <= 0: NOT GOOD")
    elif result['avg_profit_per_trade'] > 0:
        print("✅ Expectancy/trade > 0: ACCEPTABLE")
    
    if result['max_consecutive_losses'] >= 5:
        print("⚠️  Consecutive losses >= 5: NOT GOOD")
    elif result['max_consecutive_losses'] <= 2:
        print("✅ Consecutive losses <= 2: GOOD")
    else:
        print("⚠️  Consecutive losses: NEED TO FOLLOW")