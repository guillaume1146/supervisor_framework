"""
Workflow registry for managing all phase definitions
"""

from typing import List
from .base import PhaseDefinition

from workflow_system.phases import (
    PHASE1_DEFINITION,
    REPORT_GENERATION_DEFINITION
)


class WorkflowRegistry:
    """Registry for managing workflow phases"""
    
    def __init__(self):
        self._phases = {}
        self._register_default_phases()
    
    def _register_default_phases(self):
        """Register all default phases"""
        default_phases = [
            PHASE1_DEFINITION,
            REPORT_GENERATION_DEFINITION
        ]
        
        for phase in default_phases:
            self.register_phase(phase)
    
    def register_phase(self, phase_definition: PhaseDefinition):
        """Register a new phase definition"""
        self._phases[phase_definition.name] = phase_definition
    
    def get_phase(self, name: str) -> PhaseDefinition:
        """Get a phase definition by name"""
        return self._phases.get(name)
    
    def get_all_phases(self) -> List[PhaseDefinition]:
        """Get all registered phase definitions"""
        return list(self._phases.values())
    
    def list_phase_names(self) -> List[str]:
        """Get list of all phase names"""
        return list(self._phases.keys())


# Global registry instance
_registry = WorkflowRegistry()

def get_workflow_registry() -> WorkflowRegistry:
    """Get the global workflow registry"""
    return _registry

def get_all_phase_definitions() -> List[PhaseDefinition]:
    """Get all phase definitions from registry"""
    return _registry.get_all_phases()

# For backward compatibility
PHASE_DEFINITIONS = get_all_phase_definitions()