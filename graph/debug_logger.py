#!/usr/bin/env python3
"""
Debug Logger cho Agentic-RAG System
Lưu output của từng node ra file JSON để dễ debug
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class DebugLogger:
    """Logger để lưu debug information của từng node"""
    
    def __init__(self, output_dir: str = "debug_logs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Tạo session ID cho lần chạy này
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.output_dir / self.session_id
        self.session_dir.mkdir(exist_ok=True)
        
        # Lưu thông tin session
        self.session_info = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "nodes_executed": [],
            "final_result": None
        }
        
        # Counter cho node execution
        self.node_counter = 0
        
    def log_node_execution(self, node_name: str, input_state: Dict[str, Any], 
                          output_state: Dict[str, Any], execution_time: float = None,
                          error: Optional[str] = None) -> str:
        """Log thông tin execution của một node"""
        
        self.node_counter += 1
        node_id = f"{self.node_counter:03d}_{node_name}"
        
        # Tạo log entry
        log_entry = {
            "node_id": node_id,
            "node_name": node_name,
            "timestamp": datetime.now().isoformat(),
            "execution_time_seconds": execution_time,
            "input_state": self._sanitize_state(input_state),
            "output_state": self._sanitize_state(output_state),
            "error": error,
            "state_diff": self._get_state_diff(input_state, output_state)
        }
        
        # Lưu ra file riêng cho node này
        node_file = self.session_dir / f"{node_id}.json"
        with open(node_file, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, ensure_ascii=False, indent=2)
        
        # Cập nhật session info
        self.session_info["nodes_executed"].append({
            "node_id": node_id,
            "node_name": node_name,
            "timestamp": log_entry["timestamp"],
            "execution_time": execution_time,
            "error": error is not None
        })
        
        return node_id
    
    def log_final_result(self, final_state: Dict[str, Any], total_execution_time: float = None):
        """Log kết quả cuối cùng"""
        self.session_info["final_result"] = {
            "timestamp": datetime.now().isoformat(),
            "total_execution_time_seconds": total_execution_time,
            "final_state": self._sanitize_state(final_state),
            "summary": self._create_summary(final_state)
        }
        
        # Lưu session info
        session_file = self.session_dir / "session_info.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_info, f, ensure_ascii=False, indent=2)
        
        # Tạo summary file
        summary_file = self.session_dir / "summary.md"
        self._create_summary_markdown(summary_file)
        
        print(f"✓ Debug logs saved to: {self.session_dir}")
        print(f"  - Session info: {session_file}")
        print(f"  - Summary: {summary_file}")
        print(f"  - Node logs: {len(self.session_info['nodes_executed'])} files")
    
    def _sanitize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Làm sạch state để có thể serialize được"""
        if not isinstance(state, dict):
            return {"raw_value": str(state)}
        
        sanitized = {}
        for key, value in state.items():
            try:
                # Thử serialize để kiểm tra
                json.dumps(value, ensure_ascii=False)
                sanitized[key] = value
            except (TypeError, ValueError):
                # Nếu không serialize được, chuyển thành string
                sanitized[key] = str(value)
        
        return sanitized
    
    def _get_state_diff(self, input_state: Dict[str, Any], output_state: Dict[str, Any]) -> Dict[str, Any]:
        """Tính toán sự khác biệt giữa input và output state"""
        diff = {}
        
        # Tìm keys mới được thêm vào
        new_keys = set(output_state.keys()) - set(input_state.keys())
        for key in new_keys:
            diff[f"added_{key}"] = output_state[key]
        
        # Tìm keys bị thay đổi
        common_keys = set(input_state.keys()) & set(output_state.keys())
        for key in common_keys:
            if input_state[key] != output_state[key]:
                diff[f"changed_{key}"] = {
                    "from": input_state[key],
                    "to": output_state[key]
                }
        
        return diff
    
    def _create_summary(self, final_state: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo summary của kết quả cuối cùng"""
        summary = {
            "total_nodes_executed": len(self.session_info["nodes_executed"]),
            "nodes_with_errors": len([n for n in self.session_info["nodes_executed"] if n["error"]]),
            "final_answer_length": len(str(final_state.get("final_answer", ""))),
            "has_final_answer": "final_answer" in final_state,
            "has_plan": "plan" in final_state,
            "has_enrichment": "enrichment" in final_state,
            "has_tool_output": "tool_output" in final_state
        }
        
        # Thêm thông tin về các agent đã chạy
        agent_nodes = [n for n in self.session_info["nodes_executed"] 
                      if "node" in n["node_name"]]
        summary["agents_executed"] = [n["node_name"] for n in agent_nodes]
        
        return summary
    
    def _create_summary_markdown(self, summary_file: Path):
        """Tạo file summary dạng markdown"""
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Debug Session Summary\n\n")
            f.write(f"**Session ID:** {self.session_info['session_id']}\n")
            f.write(f"**Start Time:** {self.session_info['start_time']}\n")
            f.write(f"**Total Nodes:** {len(self.session_info['nodes_executed'])}\n\n")
            
            f.write("## Execution Flow\n\n")
            for node in self.session_info["nodes_executed"]:
                status = "❌" if node["error"] else "✅"
                f.write(f"{status} **{node['node_name']}** ({node['node_id']})\n")
                f.write(f"   - Time: {node['timestamp']}\n")
                if node["execution_time"]:
                    f.write(f"   - Duration: {node['execution_time']:.2f}s\n")
                f.write("\n")
            
            if self.session_info["final_result"]:
                f.write("## Final Result\n\n")
                summary = self.session_info["final_result"]["summary"]
                f.write(f"- **Total Nodes:** {summary['total_nodes_executed']}\n")
                f.write(f"- **Errors:** {summary['nodes_with_errors']}\n")
                f.write(f"- **Has Final Answer:** {summary['has_final_answer']}\n")
                f.write(f"- **Final Answer Length:** {summary['final_answer_length']} chars\n")
                f.write(f"- **Agents Executed:** {', '.join(summary['agents_executed'])}\n\n")
                
                if summary['has_final_answer']:
                    final_answer = self.session_info["final_result"]["final_state"].get("final_answer", "")
                    f.write("### Final Answer\n\n")
                    f.write(f"```\n{final_answer[:500]}{'...' if len(final_answer) > 500 else ''}\n```\n")


class GraphDebugWrapper:
    """Wrapper để wrap graph và tự động log debug information"""
    
    def __init__(self, graph, logger: DebugLogger):
        self.graph = graph
        self.logger = logger
        self.start_time = None
    
    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke graph với debug logging"""
        self.start_time = time.time()
        
        # Tạo một wrapper cho mỗi node để log
        original_nodes = {}
        
        def create_logging_node(node_name):
            def logging_node(state):
                node_start_time = time.time()
                try:
                    # Lưu input state
                    input_state = state.copy()
                    
                    # Gọi node gốc
                    result = original_nodes[node_name](state)
                    
                    # Tính execution time
                    execution_time = time.time() - node_start_time
                    
                    # Log success
                    self.logger.log_node_execution(
                        node_name, input_state, result, execution_time
                    )
                    
                    return result
                    
                except Exception as e:
                    # Log error
                    execution_time = time.time() - node_start_time
                    self.logger.log_node_execution(
                        node_name, state, state, execution_time, str(e)
                    )
                    raise
        
            return logging_node
        
        # Wrap tất cả nodes với logging
        for node_name in self.graph.nodes:
            if hasattr(self.graph, 'get_node'):
                original_nodes[node_name] = self.graph.get_node(node_name)
                # Note: Trong thực tế, việc wrap nodes có thể phức tạp hơn
                # Đây là approach đơn giản
        
        # Invoke graph
        try:
            result = self.graph.invoke(input_data)
            
            # Log final result
            total_time = time.time() - self.start_time
            self.logger.log_final_result(result, total_time)
            
            return result
            
        except Exception as e:
            # Log error
            total_time = time.time() - self.start_time
            self.logger.log_final_result({"error": str(e)}, total_time)
            raise


def create_debug_graph(graph, output_dir: str = "debug_logs"):
    """Factory function để tạo debug wrapper cho graph"""
    logger = DebugLogger(output_dir)
    return GraphDebugWrapper(graph, logger)
