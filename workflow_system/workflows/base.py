"""
Base classes and definitions for workflow phases.
"""

from dataclasses import dataclass
from typing import Callable, Dict, Any, Type
from pydantic import BaseModel


@dataclass
class PhaseDefinition:
    """Enhanced phase definition with metadata"""
    name: str
    required_params: Type[BaseModel]
    workflow_function: Callable[[Dict[str, Any]], Dict[str, Any]]
    description: str
    timeout_seconds: int = 300
    retry_count: int = 3