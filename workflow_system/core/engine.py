"""
Core workflow engine implementation.
"""

import json
import logging
from typing import List, Optional, Dict, Any, Type

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from pydantic import BaseModel

from ..config.settings import (
    WorkflowConfig, WorkflowStatus, ParameterExtractionError, 
    ValidationError, StateTransitionError
)
from ..models.state import WorkflowState, SupervisorOutPydantic
from ..workflows.base import PhaseDefinition

logger = logging.getLogger(__name__)


class EnhancedParameterWorkflow:
    """
    Enhanced workflow with intelligent parameter collection and improved reliability.
    
    Key improvements:
    - Structured output for parameter extraction
    - Configurable settings
    - Better error handling and recovery
    - Simplified state management
    - Enhanced logging and debugging
    """
    
    def __init__(self, phase_definitions: List[PhaseDefinition], config: Optional[WorkflowConfig] = None):
        """
        Initialize the enhanced parameter workflow.
        
        Args:
            phase_definitions: List of workflow phase definitions
            config: Optional configuration object
        """
        self.config = config or WorkflowConfig()
        self.phase_definitions = {pd.name: pd for pd in phase_definitions}
        self.phase_names = list(self.phase_definitions.keys())
        
        # Initialize LLMs with configuration
        base_llm = ChatGroq(
            model_name=self.config.default_llm_model, 
            temperature=self.config.default_temperature
        )
        
        # Use the proper Pydantic model for structured output
        self.supervisor_llm = ChatGroq(
            model_name=self.config.default_llm_model,
            temperature=self.config.supervisor_temperature
        ).with_structured_output(SupervisorOutPydantic)
        
        self.parameter_extractor_llm = base_llm
        self.graph = self._build_graph()
        
        logger.info(f"Enhanced workflow initialized with {len(self.phase_definitions)} phases")
    
    def _extract_parameters_with_fallback(self, message: str, phase_name: str) -> Dict[str, Any]:
        """
        Fallback parameter extraction using regular LLM when structured output fails.
        
        Args:
            message: Natural language message to extract parameters from
            phase_name: Name of the workflow phase
            
        Returns:
            Dictionary of extracted parameters
        """
        logger.info(f"Using fallback extraction for {phase_name} from: '{message}'")
        
        phase_def = self.phase_definitions[phase_name]
        param_model = phase_def.required_params
        
        # Create field descriptions
        field_descriptions = []
        for field_name, field_info in param_model.model_fields.items():
            description = field_info.description or f"extract the {field_name.replace('_', ' ')}"
            examples = getattr(field_info, 'examples', [])
            example_text = f" Examples: {examples}" if examples else ""
            field_descriptions.append(f"- {field_name}: {description}{example_text}")
        
        extraction_prompt = f"""
        Extract parameters for {phase_name} from this message: "{message}"
        
        Required parameters:
        {chr(10).join(field_descriptions)}
        
        Return a JSON object with extracted parameters. Use null for parameters that cannot be determined.
        Only return the JSON object, nothing else.
        
        Example: {{"user_name": "Alice", "report_type": null}}
        """
        
        try:
            response = self.parameter_extractor_llm.invoke(extraction_prompt)
            content = response.content.strip()
            
            # Clean up the response to extract JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            # Find JSON boundaries
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start != -1 and json_end != 0:
                content = content[json_start:json_end]
            
            # Parse JSON
            extracted = json.loads(content)
            
            # Clean up values
            cleaned_dict = {}
            for k, v in extracted.items():
                if isinstance(v, str) and v.lower() in ["none", "null", ""]:
                    cleaned_dict[k] = None
                else:
                    cleaned_dict[k] = v
            
            # Filter out None values
            valid_params = {
                k: v for k, v in cleaned_dict.items() 
                if v is not None and v != "" and str(v).strip() != ""
            }
            
            logger.info(f"Fallback extraction successful: {valid_params}")
            return valid_params
            
        except Exception as e:
            logger.warning(f"Fallback extraction also failed: {e}")
            return {}
    
    def _extract_parameters_with_structured_output(self, message: str, phase_name: str) -> Dict[str, Any]:
        """
        Extract parameters using structured output for better reliability.
        
        Args:
            message: Natural language message to extract parameters from
            phase_name: Name of the workflow phase
            
        Returns:
            Dictionary of extracted parameters
            
        Raises:
            ParameterExtractionError: If extraction fails after retries
        """
        logger.info(f"Extracting parameters for {phase_name} from: '{message}'")
        
        phase_def = self.phase_definitions[phase_name]
        param_model = phase_def.required_params
        
        # Create a structured output LLM for this specific parameter model
        structured_llm = self.parameter_extractor_llm.with_structured_output(param_model)
        
        # Create a detailed prompt for parameter extraction
        field_descriptions = []
        for field_name, field_info in param_model.model_fields.items():
            description = field_info.description or f"extract the {field_name.replace('_', ' ')}"
            examples = getattr(field_info, 'examples', [])
            example_text = f" Examples: {examples}" if examples else ""
            field_descriptions.append(f"- {field_name}: {description}{example_text}")
        
        extraction_prompt = f"""
        Extract parameters for {phase_name} from this message: "{message}"
        
        Required parameters:
        {chr(10).join(field_descriptions)}
        
        IMPORTANT: 
        - If a parameter cannot be clearly determined from the message, set it to null
        - Only extract parameters that are explicitly mentioned or clearly implied
        - Do not guess or make assumptions about missing information
        """
        
        for attempt in range(self.config.parameter_extraction_retries):
            try:
                extracted_params = structured_llm.invoke(extraction_prompt)
                
                # Convert to dict and clean up values
                if hasattr(extracted_params, 'model_dump'):
                    param_dict = extracted_params.model_dump()
                else:
                    param_dict = dict(extracted_params)
                
                # Clean up the parameter values - convert string "None" to actual None
                cleaned_dict = {}
                for k, v in param_dict.items():
                    if isinstance(v, str) and v.lower() in ["none", "null", ""]:
                        cleaned_dict[k] = None
                    else:
                        cleaned_dict[k] = v
                
                # Filter out None values, empty strings, and string "None"
                valid_params = {
                    k: v for k, v in cleaned_dict.items() 
                    if v is not None and v != "" and v != "null" and v != "None" 
                    and str(v).lower() != "none" and str(v).strip() != ""
                }
                
                if self.config.debug_mode:
                    filtered_out = {k: v for k, v in cleaned_dict.items() if k not in valid_params}
                    if filtered_out:
                        logger.info(f"Filtered out invalid parameters: {filtered_out}")
                
                logger.info(f"Successfully extracted parameters (attempt {attempt + 1}): {valid_params}")
                return valid_params
                
            except Exception as e:
                logger.warning(f"Parameter extraction attempt {attempt + 1} failed: {e}")
                if attempt == self.config.parameter_extraction_retries - 1:
                    # Try fallback method before giving up
                    logger.info("Trying fallback extraction method...")
                    try:
                        return self._extract_parameters_with_fallback(message, phase_name)
                    except Exception as fallback_error:
                        logger.warning(f"Fallback extraction failed: {fallback_error}")
                        raise ParameterExtractionError(f"Failed to extract parameters after {self.config.parameter_extraction_retries} attempts and fallback: {e}")
        
        return {}
    
    def _validate_parameters(self, params: Dict[str, Any], param_model: Type[BaseModel]) -> Dict[str, Any]:
        """
        Validate parameters against the model schema.
        
        Args:
            params: Parameters to validate
            param_model: Pydantic model for validation
            
        Returns:
            Validated parameters dictionary
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            validated = param_model.model_validate(params)
            return validated.model_dump()
        except Exception as e:
            raise ValidationError(f"Parameter validation failed: {e}")
    
    def _get_missing_parameters(self, current_params: Dict[str, Any], param_model: Type[BaseModel]) -> List[str]:
        """Get list of missing required parameters (phase-aware)"""
        
        # Try to get user input fields from the parameter model
        if hasattr(param_model, 'get_user_input_fields'):
            user_input_fields = param_model.get_user_input_fields()
        else:
            # Fallback: all fields that don't have exclude=True
            user_input_fields = []
            for field_name, field_info in param_model.model_fields.items():
                if not getattr(field_info, 'exclude', False):
                    user_input_fields.append(field_name)
        
        # Check which user input fields are missing
        missing_fields = []
        for field in user_input_fields:
            value = current_params.get(field)
            if (value is None or 
                value == "" or 
                str(value).lower() in ["none", "not specified", "null"] or
                str(value).strip() == ""):
                missing_fields.append(field)
        
        return missing_fields
    
    def _create_parameter_request_message(self, missing_params: List[str], param_model: Type[BaseModel], phase_name: str, is_retry: bool = False) -> str:
        """Create parameter request message (only for user input fields)"""
        
        if is_retry:
            intro = "Let me help you provide the correct information:"
        else:
            intro = f"I need some additional information for your {phase_name.replace('_', ' ')}:"

        # Get computed fields to exclude
        computed_fields = set()
        if hasattr(param_model, 'get_computed_fields'):
            computed_fields = set(param_model.get_computed_fields())
        
        param_requests = []
        for param in missing_params:
            # Skip computed fields
            if param in computed_fields:
                continue
                
            # Skip fields marked with exclude=True
            if param in param_model.model_fields:
                field_info = param_model.model_fields[param]
                if getattr(field_info, 'exclude', False):
                    continue
                    
                description = field_info.description or f"the {param.replace('_', ' ')}"
                examples = getattr(field_info, 'examples', [])
                example_text = f" (e.g., {', '.join(map(str, examples[:3]))})" if examples else ""
                param_requests.append(f"• **{param.replace('_', ' ').title()}**: {description}{example_text}")
        
        if not param_requests:
            return "All required information has been collected. Processing your request..."
        
        return f"""{intro}
    {chr(10).join(param_requests)}
    Please provide these details and I'll continue with the workflow.
    """.strip()
    
    def _build_graph(self) -> StateGraph:
        """Build the enhanced workflow graph with improved error handling"""
        builder = StateGraph(WorkflowState)
        
        # Add nodes
        builder.add_node("supervisor", self._supervisor_node)
        for phase_name, phase_def in self.phase_definitions.items():
            builder.add_node(phase_name, self._create_enhanced_phase_node(phase_def))
        
        # Add edges
        builder.add_edge(START, "supervisor")
        for phase_name in self.phase_names:
            builder.add_edge(phase_name, END)
        
        return builder.compile(checkpointer=MemorySaver())
    
    def _supervisor_node(self, state: WorkflowState) -> Command:
        """Enhanced supervisor node with better decision making"""
        try:
            # Get latest human message
            latest_message = ""
            for msg in reversed(state["messages"]):
                if hasattr(msg, 'content') and msg.__class__.__name__ == "HumanMessage":
                    latest_message = msg.content or ""
                    break
            
            if not latest_message.strip():
                logger.error("Empty or whitespace-only message provided")
                state["status"] = WorkflowStatus.FAILED.value
                state["error_count"] = state.get("error_count", 0) + 1
                raise StateTransitionError("Empty message provided - cannot determine workflow intent")
            
            # Create supervisor prompt
            phase_descriptions = "\n".join([
                f"- **{name}**: {defn.description}" 
                for name, defn in self.phase_definitions.items()
            ])
            
            supervisor_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=f"""You are an intelligent workflow supervisor. Analyze the user's request and decide which workflow phase to execute.

    Available workflow phases:
    {phase_descriptions}

    ROUTING GUIDELINES:
    - Use 'financial_input_validation' for: financial product analysis, pension/SIPP/ISA analysis, investment valuation, portfolio analysis
    - Use 'generate_report' for: creating reports, generating documents

    Return your decision with:
    - next_phase: one of {self.phase_names}
    - intent: brief summary of what the user wants to accomplish  
    - confidence: float between 0.0 and 1.0 indicating your confidence in the decision

    Choose the most appropriate phase based on keywords, context, and user intent."""),
                MessagesPlaceholder("messages"),
            ])
            
            # Get supervisor decision
            supervisor_decision_pydantic = self.supervisor_llm.invoke(
                supervisor_prompt.format_messages(messages=state["messages"])
            )
            
            # Convert Pydantic model to dict for state management
            supervisor_decision = supervisor_decision_pydantic.model_dump()
            
            logger.info(f"Supervisor decision: {supervisor_decision}")
            
            # Validate decision
            if supervisor_decision["next_phase"] not in self.phase_names:
                logger.warning(f"Invalid phase selected: {supervisor_decision['next_phase']}, defaulting to first phase")
                supervisor_decision["next_phase"] = self.phase_names[0]
                supervisor_decision["confidence"] = 0.5
            
            # Update state
            state["supervisor_out"] = supervisor_decision
            state["current_phase"] = supervisor_decision["next_phase"]
            state["status"] = WorkflowStatus.COLLECTING_PARAMS.value
            
            # Extract initial parameters
            if latest_message:
                try:
                    extracted_params = self._extract_parameters_with_structured_output(
                        latest_message, supervisor_decision["next_phase"]
                    )
                    
                    phase_name = supervisor_decision["next_phase"]
                    if phase_name not in state["params"]:
                        state["params"][phase_name] = {}
                    
                    state["params"][phase_name].update(extracted_params)
                    logger.info(f"Initial parameter extraction for {phase_name}: {extracted_params}")
                    
                except ParameterExtractionError as e:
                    logger.warning(f"Initial parameter extraction failed: {e}")
                    # Continue anyway, parameters will be requested in the phase node
            
            return Command(goto=supervisor_decision["next_phase"])
            
        except Exception as e:
            logger.error(f"Supervisor node error: {e}")
            error_count = state.get("error_count", 0) + 1
            
            # For critical errors like empty messages, return error state directly
            if "Empty message" in str(e):
                error_msg = f"❌ **Error**: {str(e)}"
                logger.info("Returning immediate failure for critical error")
                
                return {
                    "messages": [AIMessage(content=error_msg)],
                    "awaiting_input": False,
                    "status": WorkflowStatus.FAILED.value,
                    "error_count": error_count,
                    "error_message": error_msg,
                    "current_phase": None,
                    "supervisor_out": {"next_phase": "error", "intent": "critical_error", "confidence": 0.0}
                }
            
            # For other errors, default to first phase but mark as failed
            default_phase = self.phase_names[0]
            state["current_phase"] = default_phase
            state["status"] = WorkflowStatus.FAILED.value
            state["error_count"] = error_count
            state["supervisor_out"] = {"next_phase": default_phase, "intent": "error_recovery", "confidence": 0.1}
            return Command(goto=default_phase)
        
    def _create_validation_error_message(self, error_str: str, phase_name: str, param_model: Type[BaseModel]) -> str:
        """
        Create a helpful validation error message that guides the user to provide correct input.
        
        Args:
            error_str: Original validation error message
            phase_name: Name of the current phase
            param_model: Pydantic model for this phase
            
        Returns:
            User-friendly error message with guidance
        """
        
        # Parse common validation errors and provide specific guidance
        if "age" in error_str.lower():
            return """
            ❌ **Invalid Age Provided**

            The age you entered is not valid. Please provide your age as:
            - A number between 0 and 120
            - Examples: "45", "thirty-five", "aged 45"

            Please tell me your correct age.
                    """.strip()
        
        elif "currency" in error_str.lower() or "amount" in error_str.lower():
            return """
                ❌ **Invalid Amount Provided**

                The amount you entered is not valid. Please provide amounts as:
                - £50000 or £50,000
                - 50k or 50000
                - "fifty thousand pounds"

                Please provide the correct amount.
                        """.strip()
        
        elif "date" in error_str.lower():
            return """
    ❌ **Invalid Date Provided**

    The date you entered is not valid. Please provide dates as:
    - dd/mm/yyyy format (e.g., 15/03/2024)
    - "today" for current date
    - Month Year (e.g., "March 2024")

    Please provide the correct date.
            """.strip()
        
        else:
            # Generic validation error message
            return f"""
    ❌ **Invalid Input Provided**

    {error_str}

    Please provide the correct information for {phase_name.replace('_', ' ')}.
            """.strip()
    
    def _create_enhanced_phase_node(self, phase_def: PhaseDefinition):
        """Create an enhanced phase execution node with better error handling"""
        
        def enhanced_phase_node(state: WorkflowState) -> WorkflowState:
            phase_name = phase_def.name
            logger.info(f"Starting enhanced execution of {phase_name}")
            if state.get("status") == WorkflowStatus.FAILED.value:
                error_msg = state.get("error_message", "❌ **Error**: Workflow failed")
                logger.info(f"Phase {phase_name} detected failed state from supervisor, returning error")
                return {
                    "messages": [AIMessage(content=error_msg)],
                    "awaiting_input": False,
                    "status": WorkflowStatus.FAILED.value,
                    "error_count": state.get("error_count", 1)
                }
            
            try:
                # Initialize phase parameters if not present
                if phase_name not in state["params"]:
                    state["params"][phase_name] = {}
                
                phase_params = state["params"][phase_name].copy()
                param_model = phase_def.required_params
                
                # Remove internal flags
                clean_params = {k: v for k, v in phase_params.items() if not k.startswith("__")}
                
                # Check for missing parameters
                missing_params = self._get_missing_parameters(clean_params, param_model)
                
                if missing_params:
                    logger.info(f"Missing parameters for {phase_name}: {missing_params}")
                    
                    # Create parameter request message
                    request_message = self._create_parameter_request_message(
                        missing_params, param_model, phase_name
                    )
                    
                    # Mark that we've requested parameters
                    phase_params["__parameter_request_sent__"] = True
                    state["params"][phase_name] = phase_params
                    state["awaiting_input"] = True
                    state["status"] = WorkflowStatus.COLLECTING_PARAMS.value
                    
                    return {
                        "messages": [AIMessage(content=request_message)],
                        "awaiting_input": True,
                        "current_phase": phase_name,
                        "params": state["params"],
                        "status": WorkflowStatus.COLLECTING_PARAMS.value
                    }
                
                # All parameters available - validate and execute
                logger.info(f"All parameters available for {phase_name}, proceeding with execution")
                
                try:
                    validated_params = self._validate_parameters(clean_params, param_model)
                    state["status"] = WorkflowStatus.EXECUTING.value

                    result = phase_def.workflow_function(validated_params)
                    # Handle different status types
                    phase_status = result.get('status', 'completed')
                    
                    if phase_status in ['completed', 'completed_with_warnings']:
                        # SUCCESS - workflow completed
                        success_message = result.get('completion_message',  f"✅ {phase_name.replace('_', ' ').title()} completed successfully!")
                        logger.info(f"Workflow {phase_name} completed with status: {phase_status}")
                        return {
                            "messages": [AIMessage(content=success_message)],
                            "awaiting_input": False,
                            "current_phase": None,
                            "results": {phase_name: result},
                            "status": WorkflowStatus.COMPLETED.value
                        }
                        
                    elif phase_status == 'incomplete':
                        # INCOMPLETE - missing required information
                        incomplete_message = result.get('completion_message', f"⚠️ {phase_name.replace('_', ' ').title()} needs additional information")
                        logger.info(f"Workflow {phase_name} incomplete - requesting more information")
                        return {
                            "messages": [AIMessage(content=incomplete_message)],
                            "awaiting_input": True,
                            "current_phase": phase_name,
                            "params": state["params"],
                            "status": WorkflowStatus.COLLECTING_PARAMS.value
                        }
                        
                    elif phase_status == 'failed':
                        # FAILED - validation or execution errors
                        error_message = result.get('completion_message', f"❌ {phase_name.replace('_', ' ').title()} failed validation")
                        logger.error(f"Workflow {phase_name} failed")
                        return {
                            "messages": [AIMessage(content=error_message)],
                            "awaiting_input": False,
                            "status": WorkflowStatus.FAILED.value,
                            "error_count": state.get("error_count", 0) + 1
                        }
                    else:
                        # UNKNOWN STATUS - treat as completed
                        logger.warning(f"Unknown status '{phase_status}' for {phase_name}, treating as completed")
                        return {
                            "messages": [AIMessage(content=result.get('completion_message', 'Workflow completed'))],
                            "awaiting_input": False,
                            "current_phase": None,
                            "results": {phase_name: result},
                            "status": WorkflowStatus.COMPLETED.value
                        }
                except ValidationError as e:
                    logger.error(f"Parameter validation failed for {phase_name}: {e}")
                    # Create helpful error message with specific guidance
                    validation_error_message = self._create_validation_error_message(
                        str(e), phase_name, param_model
                    )
                    
                    # Mark the parameter that failed validation for re-collection
                    state["params"][phase_name]["__validation_failed__"] = True
                    state["params"][phase_name]["__last_validation_error__"] = str(e)
                    return {
                        "messages": [AIMessage(content=validation_error_message)],
                        "awaiting_input": True,  # ✅ KEEP CONVERSATION GOING
                        "current_phase": phase_name,  # ✅ STAY IN SAME PHASE
                        "status": WorkflowStatus.COLLECTING_PARAMS.value,  # ✅ STILL COLLECTING
                        "params": state["params"],
                        "error_count": state.get("error_count", 0) + 1
                    }
                except Exception as e:
                    logger.error(f"Workflow execution failed for {phase_name}: {e}")
                    error_message = f"❌ **Error in {phase_name.replace('_', ' ')}**: {str(e)}"
                    return {
                        "messages": [AIMessage(content=error_message)],
                        "awaiting_input": False,
                        "status": WorkflowStatus.FAILED.value,
                        "error_count": state.get("error_count", 0) + 1
                    }
            except Exception as e:
                logger.error(f"Unexpected error in {phase_name}: {e}")
                error_message = f"❌ **Unexpected error** in {phase_name.replace('_', ' ')}: {str(e)}"
                return {
                    "messages": [AIMessage(content=error_message)],
                    "awaiting_input": False,
                    "status": WorkflowStatus.FAILED.value,
                    "error_count": state.get("error_count", 0) + 1
                }
        return enhanced_phase_node
    
    def run_workflow(self, initial_message: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        Run the workflow with enhanced parameter collection.
        
        Args:
            initial_message: Initial user message
            thread_id: Thread identifier for state persistence
            
        Returns:
            Workflow execution result
        """
        logger.info(f"Starting enhanced workflow with message: '{initial_message}' (thread: {thread_id})")
        initial_state = {
            "messages": [HumanMessage(content=initial_message)],
            "params": {},
            "results": {},
            "supervisor_out": None,
            "current_phase": None,
            "awaiting_input": False,
            "status": WorkflowStatus.PENDING.value,
            "error_count": 0,
            "iteration_count": 0,
            "error_message": None
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            result = self.graph.invoke(initial_state, config)
            if self.config.enable_auto_continuation:
                iteration = 0
                while (result.get("awaiting_input", False) and 
                       iteration < self.config.max_iterations and 
                       not result.get("results", {})):
                    
                    iteration += 1
                    logger.info(f"Auto-continuation iteration {iteration}")
                    
                    current_phase = result.get("current_phase")
                    if current_phase and current_phase in result.get("params", {}):
                        phase_params = result["params"][current_phase]
                        param_model = self.phase_definitions[current_phase].required_params
                        
                        missing = self._get_missing_parameters(
                            {k: v for k, v in phase_params.items() if not k.startswith("__")},
                            param_model
                        )
                        
                        if not missing:
                            logger.info("All parameters available, continuing execution")
                            result["messages"].append(HumanMessage(content="continue with execution"))
                            result = self.graph.invoke(result, config)
                        else:
                            logger.info(f"Still missing parameters: {missing}")
                            break
                    else:
                        break
            return result
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            return {
                "error": str(e), 
                "status": WorkflowStatus.FAILED.value,
                "results": {}
            }
    
    def add_user_input(self, user_input: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        Add user input to continue the workflow with simplified state management.
        
        Args:
            user_input: User input message
            thread_id: Thread identifier
            
        Returns:
            Updated workflow state
        """
        logger.info(f"Adding user input: '{user_input}' to thread: {thread_id}")
        
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Get current state
            current_state = self.graph.get_state(config)
            
            if not current_state or not current_state.values:
                logger.warning("No existing state found, starting fresh workflow")
                return self.run_workflow(user_input, thread_id)
            
            state = current_state.values
            current_phase = state.get("current_phase")
            
            if not current_phase:
                logger.warning("No current phase in state, starting fresh workflow")
                return self.run_workflow(user_input, thread_id)
            
            try:
                new_params = self._extract_parameters_with_structured_output(user_input, current_phase)
                if current_phase not in state["params"]:
                    state["params"][current_phase] = {}
                
                phase_params = state["params"][current_phase].copy()
                if "__parameter_request_sent__" in phase_params:
                    del phase_params["__parameter_request_sent__"]
                
                phase_params.update(new_params)
                state["params"][current_phase] = phase_params
                logger.info(f"Updated parameters for {current_phase}: {phase_params}")
            except ParameterExtractionError as e:
                logger.warning(f"Failed to extract parameters from user input: {e}")
            
            new_messages = state.get("messages", []) + [HumanMessage(content=user_input)]
            updated_state = {
                **state,
                "messages": new_messages,
                "awaiting_input": False,
                "iteration_count": state.get("iteration_count", 0) + 1
            }
            phase_def = self.phase_definitions[current_phase]
            phase_node = self._create_enhanced_phase_node(phase_def)
            result = phase_node(updated_state)
            if isinstance(result, dict):
                final_state = {**updated_state, **result}
            else:
                final_state = updated_state
            self.graph.update_state(config, final_state)
            return final_state
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return {
                "error": str(e), 
                "status": WorkflowStatus.FAILED.value,
                "messages": [AIMessage(content=f"Error processing input: {str(e)}")]
            }