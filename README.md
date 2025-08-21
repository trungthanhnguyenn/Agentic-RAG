# Agentic-RAG System: Investment Advice & Numerology

## Overview

This system is an integrated **investment advice and numerology**, using Agentic-RAG architecture with LangGraph to process complex user queries. The system combines real-world transaction data with numerology analysis to provide comprehensive advice.

## System Structure

```
Initial Node → ContextEnricher → Planner Agent → Router Agent → Specialized Agents → Synthesizer Agent → Final Answer
```

### Activity Flow

1. **Initial Node**: Initialize initial state
2. **ContextEnricher**: Analyze and enrich question context
3. **Planner Agent**: Plan routing (combo priority)
4. **Router Agent**: Execute according to plan
5. **Specialized Agents**: Run in order (NumerologyAgent, TradingAgent)
6. **Synthesizer Agent**: Synthesize results (if needed)
7. **Final Node**: Return answer

## Agents

### 1. ContextEnricherAgent
```python
# Input
{
"question": "I What style should I trade?", 
"user_name": "Nguyen Huu Thanh Trung", 
"birthday": "January 3, 2003", 
"excel_path": "trading_data/test_sample.xlsx"
}

# Output
{ 
"intent": "Learn the right trading style", 
"needs": { 
"numerology": true, 
"trading": true, 
"synthesis": true 
}, 
"missing_inputs": [], 
"suggested_questions": [], 
"complexity": "moderate", 
"recommended_approach": "combo"
}
```

### 2. PlannerAgent
```python
# Input: question + enrichment
# Output
{ 
"kind": "combo", 
"agents": ["NumerologyAgent", "TradingAgent"], 
"skip_synth": false, 
"description": "Comprehensive consulting combining numerology and trading"
}
```

### 3. NumerologyAgent
- **Input**: question, user_name, birthday
- **Tools**: calculate_all_numerology_indicators, get_numerology_interpretation
- **Output**: Structured JSON with numbers, meanings, milestone_info

### 4. TradingAgent
- **Input**: question, excel_path
- **Tools**: read_trading_excel, calculate_trade_index, analyze_user_question, generate_focused_report
- **Output**: Structured JSON with trading_data, data_summary, focused_report

### 5. SynthesizerAgent
- **Input**: numerology + trading results + question
- **Tools**: ContextValidator, PatternAnalyzer
- **Output**: Final answer with enhanced insights

## Routing Rules

### 1. Prefer Combo
Always prefer `combo` when:
- The goal is comprehensive advice
- Need to make recommendations based on both personality and performance
- Questions about "fit" or "combination"
- Lack of clarity about the type of analysis needed

### 2. Decision Logic
```python
if "numerology" in keywords and "trading" in keywords:
return {"kind": "combo", "agents": ["NumerologyAgent", "TradingAgent"], "skip_synth": false}
elif "numerology" in keywords:
return {"kind": "single", "agents": ["NumerologyAgent"], "skip_synth": not needs_synthesis}
elif "trading" in keywords:
return {"kind": "single", "agents": ["TradingAgent"], "skip_synth": not needs_synthesis}
else:
return {"kind": "simple", "agents": [], "skip_synth": true}
```

## How to Use

### 1. Create .env File
```bash
cd study/rag-agentic
touch .env
```

### 2. Use in Code
```python
from graph.graph import build_graph

# Build graph
graph = build_graph()

# Test with question
test_input = {
"question": "What trading style should I follow to be suitable?",
"user_name": "Nguyen Huu Thanh Trung",
"birthday": "03/01/2003",
"excel_path": "this_path_to_excel_file"
}

# Run the system
result = graph.invoke(test_input)
print(result.get("final_answer"))
```


## Configuration

### 1. API Keys
Make sure you have the necessary API keys in `.env`:
```bash
# OpenRouter Configuration
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=path_to_openrouter
MODEL_NAME=your_model_name

# GEMINI Configuration
GOOGLE_API_KEY=your_api_key

# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=your_region
BUCKET_NAME=your_bucket_name
AWS_ENDPOINT_URL=your_endpoint_url
# ... other keys
```

### 2. Dependencies
```bash
pip install -r requirements.txt
```

## Benefits of the New System

### 1. Smart
- LLM-driven routing instead of rule-based
- Context enrichment for better understanding of needs
- Combos for comprehensive advice

### 2. Flexible
- Handle complex questions
- Automatically detect synthesis needs
- Graceful fallback for missing data

### 3. Consistent
- Structured outputs for all agents
- Validation data quality
- Error handling robust

### 4. Scalable
- Add new agents easily
- Modular architecture
- Clear separation of concerns
