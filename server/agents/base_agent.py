import time
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from server.agents.schemas import AgentContext, AgentResponse

logger = logging.getLogger('base_agent')

class BaseAgent(ABC):
    """Abstract Base Class for all Hermes Specialised Agents providing identity, trace logging, and safe fallback handling."""

    def __init__(self, name: str, role_description: str):
        self.name = name
        self.role_description = role_description
        self.logger = logging.getLogger(f'agent.{name}')

    def execute(self, context: AgentContext, **kwargs) -> AgentResponse:
        """Standard execution wrapper capturing timing, logging, and exception boundaries."""
        start_time = time.time()
        self.logger.info(f"[{context.trace_id}] {self.name} starting execution for project '{context.project_name}' (Attempt {context.attempt_number})...")
        
        try:
            result_data = self.run(context, **kwargs)
            elapsed_ms = (time.time() - start_time) * 1000.0
            self.logger.info(f"[{context.trace_id}] {self.name} completed successfully in {elapsed_ms:.1f}ms")
            return AgentResponse(
                agent_name=self.name,
                status='SUCCESS',
                data=result_data,
                execution_time_ms=elapsed_ms
            )
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000.0
            self.logger.error(f"[{context.trace_id}] {self.name} failed after {elapsed_ms:.1f}ms: {e}", exc_info=True)
            fallback_data = self.get_fallback_output(context, str(e), **kwargs)
            return AgentResponse(
                agent_name=self.name,
                status='FALLBACK',
                data=fallback_data,
                error=str(e),
                execution_time_ms=elapsed_ms
            )

    @abstractmethod
    def run(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        """Subclass implementation of agent logic."""
        pass

    @abstractmethod
    def get_fallback_output(self, context: AgentContext, error_msg: str, **kwargs) -> Dict[str, Any]:
        """Provides a safe, non-blocking fallback dictionary when agent fails."""
        pass
