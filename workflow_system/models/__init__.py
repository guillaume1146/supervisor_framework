"""
Enhanced models package with database integration support
File: workflow_system/models/__init__.py (UPDATED)
"""

# Import state management models
from .state import (
    WorkflowState, 
    SupervisorOut, 
    SupervisorOutPydantic
)

# Import database models
from .database import (
    DatabaseField,
    DatabaseRecord,
    Phase1DatabaseRecord
)

# Import base model if exists
try:
    from .base import *
except ImportError:
    # base.py might be empty or not exist
    pass

__all__ = [
    # State management
    "WorkflowState",
    "SupervisorOut",
    "SupervisorOutPydantic",
    
    # Database models
    "DatabaseField",
    "DatabaseRecord", 
    "Phase1DatabaseRecord"
]

# Version and metadata
__version__ = "2.0.0"
__description__ = "Enhanced workflow models with database integration"