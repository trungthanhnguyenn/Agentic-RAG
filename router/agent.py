from fastapi import APIRouter, HTTPException
from typing import Any, Dict

from app.schemas import (
    NumerologyRequest,
    NumerologyResponse,
    TradingRequest,
    TradingResponse,
)

# Reuse internal preparation functions for deterministic, structured outputs
from agents.numerology_agent import _prepare_data as prepare_numerology_data
from agents.trading_agent import _prepare_trading_data as prepare_trading_data


router = APIRouter()


@router.post("/numerology_agent", response_model=NumerologyResponse)
def numerology_agent_endpoint(req: NumerologyRequest) -> NumerologyResponse:
    try:
        payload: Dict[str, Any] = {
            "question": req.question,
            "user_name": req.user_name,
            "birthday": req.birthday,
        }
        data = prepare_numerology_data(payload)

        # indicators: expose a dict of key -> doc/meaning/value for quick use by UI/LLM
        indicators: Dict[str, Any] = {}
        for k in data.get("selected_keys", []):
            indicators[k] = data.get("docs", {}).get(k) or data.get("numbers", {}).get(k)

        return NumerologyResponse(
            indicators=indicators,
            selected_indicators=data.get("selected_keys", []),
            numbers=data.get("numbers", {}),
            meanings=data.get("meanings", {}),
            docs=data.get("docs", {}),
            milestone_info=data.get("milestone_info"),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/trading_agent", response_model=TradingResponse)
def trading_agent_endpoint(req: TradingRequest) -> TradingResponse:
    try:
        payload: Dict[str, Any] = {
            "question": req.question,
            "excel_path": req.excel_path,
        }
        data = prepare_trading_data(payload)

        # Standardize response structure while preserving diagnostics
        return TradingResponse(
            success=bool(data.get("success", False)),
            focused_report=data.get("focused_report"),
            trading_data=data.get("trading_data"),
            analysis_needs=data.get("analysis_needs"),
            data_summary=data.get("data_summary"),
            issues=data.get("issues"),
            suggestions=data.get("suggestions"),
            error=data.get("error"),
            error_type=data.get("error_type"),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


