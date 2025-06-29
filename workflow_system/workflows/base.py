"""
Enhanced base classes and definitions for workflow phases with database integration
File: workflow_system/workflows/base.py (UPDATED)
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, Any, Type, Optional, List
from pydantic import BaseModel
from abc import ABC, abstractmethod

from workflow_system.models.database import DatabaseRecord


@dataclass
class PhaseDefinition:
    """Enhanced phase definition with database integration support"""
    name: str
    required_params: Type[BaseModel]
    workflow_function: Callable[[Dict[str, Any]], Dict[str, Any]]
    description: str
    timeout_seconds: int = 300
    retry_count: int = 3
    
    # Enhanced database integration fields
    database_table_name: Optional[str] = None
    supports_database_storage: bool = True
    database_schema_version: str = "1.0"
    
    # Data processing configuration
    supports_field_calculation: bool = True
    supports_data_conversion: bool = True
    supports_validation: bool = True
    
    # Workflow metadata
    phase_category: str = "general"  # e.g., "input_validation", "calculation", "reporting"
    dependencies: List[str] = field(default_factory=list)  # Other phases this depends on
    output_types: List[str] = field(default_factory=list)  # Types of output this phase produces
    
    def __post_init__(self):
        """Initialize default values after creation"""
        if self.database_table_name is None:
            # Auto-generate table name from phase name
            self.database_table_name = self.name.lower().replace(' ', '_')


class BasePhaseProcessor(ABC):
    """
    Abstract base class for phase processors with standard interface
    """
    
    def __init__(self, phase_definition: PhaseDefinition):
        self.phase_definition = phase_definition
        self.processing_errors = []
        self.processing_warnings = []
    
    @abstractmethod
    def validate_inputs(self, params: Dict[str, Any]) -> bool:
        """Validate input parameters for this phase"""
        pass
    
    @abstractmethod
    def process_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process the data for this phase"""
        pass
    
    @abstractmethod
    def generate_output(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the final output for this phase"""
        pass
    
    def create_database_record(self, data: Dict[str, Any], 
                             session_id: Optional[str] = None) -> Optional[DatabaseRecord]:
        """Create database record if supported"""
        if not self.phase_definition.supports_database_storage:
            return None
        
        # This should be implemented by specific phase processors
        return None
    
    def execute(self, params: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute the complete phase workflow"""
        try:
            # Clear previous errors/warnings
            self.processing_errors.clear()
            self.processing_warnings.clear()
            
            # Validate inputs
            if not self.validate_inputs(params):
                return {
                    "status": "failed",
                    "phase": self.phase_definition.name,
                    "error": "Input validation failed",
                    "validation_errors": self.processing_errors
                }
            
            # Process data
            processed_data = self.process_data(params)
            
            # Generate output
            output = self.generate_output(processed_data)
            
            # Create database record if supported
            if self.phase_definition.supports_database_storage:
                database_record = self.create_database_record(processed_data, session_id)
                if database_record:
                    output["database_record"] = database_record.get_insert_data()
                    output["formatted_data"] = database_record.get_formatted_data()
            
            return output
            
        except Exception as e:
            return {
                "status": "failed",
                "phase": self.phase_definition.name,
                "error": str(e),
                "error_type": type(e).__name__
            }


@dataclass
class WorkflowConfiguration:
    """Configuration for enhanced workflow execution"""
    enable_database_storage: bool = True
    enable_field_calculation: bool = True
    enable_data_conversion: bool = True
    enable_comprehensive_validation: bool = True
    
    # Performance settings
    max_concurrent_phases: int = 1  # For future parallel execution
    enable_caching: bool = False
    cache_ttl_seconds: int = 3600
    
    # Error handling
    fail_fast: bool = False  # Stop on first error vs continue with warnings
    max_retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    
    # Output formatting
    include_debug_info: bool = False
    include_performance_metrics: bool = False
    output_format: str = "comprehensive"  # "minimal", "standard", "comprehensive"


class EnhancedPhaseRegistry:
    """Registry for managing enhanced phase definitions"""
    
    def __init__(self):
        self._phases: Dict[str, PhaseDefinition] = {}
        self._processors: Dict[str, Type[BasePhaseProcessor]] = {}
        self._configuration = WorkflowConfiguration()
    
    def register_phase(self, phase_definition: PhaseDefinition, 
                      processor_class: Optional[Type[BasePhaseProcessor]] = None):
        """Register a phase definition with optional processor class"""
        self._phases[phase_definition.name] = phase_definition
        
        if processor_class:
            self._processors[phase_definition.name] = processor_class
    
    def get_phase(self, name: str) -> Optional[PhaseDefinition]:
        """Get phase definition by name"""
        return self._phases.get(name)
    
    def get_processor(self, name: str) -> Optional[Type[BasePhaseProcessor]]:
        """Get processor class by phase name"""
        return self._processors.get(name)
    
    def list_phases(self) -> List[PhaseDefinition]:
        """Get all registered phases"""
        return list(self._phases.values())
    
    def list_phases_by_category(self, category: str) -> List[PhaseDefinition]:
        """Get phases by category"""
        return [phase for phase in self._phases.values() if phase.phase_category == category]
    
    def get_phase_dependencies(self, phase_name: str) -> List[str]:
        """Get dependencies for a specific phase"""
        phase = self.get_phase(phase_name)
        return phase.dependencies if phase else []
    
    def validate_dependencies(self) -> Dict[str, List[str]]:
        """Validate all phase dependencies are satisfied"""
        issues = {}
        
        for phase_name, phase in self._phases.items():
            missing_deps = []
            for dep in phase.dependencies:
                if dep not in self._phases:
                    missing_deps.append(dep)
            
            if missing_deps:
                issues[phase_name] = missing_deps
        
        return issues
    
    def set_configuration(self, config: WorkflowConfiguration):
        """Set workflow configuration"""
        self._configuration = config
    
    def get_configuration(self) -> WorkflowConfiguration:
        """Get current workflow configuration"""
        return self._configuration


class PhaseExecutionResult:
    """Result of phase execution with enhanced metadata"""
    
    def __init__(self, phase_name: str, status: str, data: Dict[str, Any]):
        self.phase_name = phase_name
        self.status = status  # "completed", "failed", "pending", "skipped"
        self.data = data
        self.execution_time_ms: Optional[float] = None
        self.memory_usage_mb: Optional[float] = None
        self.database_record_id: Optional[str] = None
        self.warnings: List[str] = []
        self.errors: List[str] = []
    
    def is_successful(self) -> bool:
        """Check if execution was successful"""
        return self.status in ["completed", "pending"]
    
    def has_warnings(self) -> bool:
        """Check if execution has warnings"""
        return len(self.warnings) > 0
    
    def has_errors(self) -> bool:
        """Check if execution has errors"""
        return len(self.errors) > 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary"""
        return {
            "phase_name": self.phase_name,
            "status": self.status,
            "is_successful": self.is_successful(),
            "has_warnings": self.has_warnings(),
            "has_errors": self.has_errors(),
            "warning_count": len(self.warnings),
            "error_count": len(self.errors),
            "execution_time_ms": self.execution_time_ms,
            "memory_usage_mb": self.memory_usage_mb
        }


# Enhanced workflow execution context
class WorkflowExecutionContext:
    """Context for workflow execution with enhanced tracking"""
    
    def __init__(self, session_id: str, configuration: WorkflowConfiguration):
        self.session_id = session_id
        self.configuration = configuration
        self.execution_results: Dict[str, PhaseExecutionResult] = {}
        self.global_data: Dict[str, Any] = {}  # Shared data across phases
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def add_result(self, result: PhaseExecutionResult):
        """Add phase execution result"""
        self.execution_results[result.phase_name] = result
    
    def get_result(self, phase_name: str) -> Optional[PhaseExecutionResult]:
        """Get result for specific phase"""
        return self.execution_results.get(phase_name)
    
    def get_successful_phases(self) -> List[str]:
        """Get list of successfully completed phases"""
        return [
            name for name, result in self.execution_results.items()
            if result.is_successful()
        ]
    
    def get_failed_phases(self) -> List[str]:
        """Get list of failed phases"""
        return [
            name for name, result in self.execution_results.items()
            if not result.is_successful()
        ]
    
    def get_overall_status(self) -> str:
        """Get overall workflow status"""
        if not self.execution_results:
            return "pending"
        
        failed_phases = self.get_failed_phases()
        if failed_phases:
            return "failed"
        
        pending_phases = [
            name for name, result in self.execution_results.items()
            if result.status == "pending"
        ]
        if pending_phases:
            return "pending"
        
        return "completed"
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get comprehensive execution summary"""
        return {
            "session_id": self.session_id,
            "overall_status": self.get_overall_status(),
            "total_phases": len(self.execution_results),
            "successful_phases": len(self.get_successful_phases()),
            "failed_phases": len(self.get_failed_phases()),
            "phase_results": {
                name: result.get_summary()
                for name, result in self.execution_results.items()
            },
            "total_execution_time_ms": (
                (self.end_time - self.start_time) * 1000
                if self.start_time and self.end_time
                else None
            )
        }


# Backward compatibility - keep original PhaseDefinition as alias
LegacyPhaseDefinition = PhaseDefinition