from typing import TypedDict, List, Dict, Any, Literal, Annotated, Optional, Callable, Type
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
import datetime, json, re
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.7)

class SupervisorOut(TypedDict):
    next_phase: str
    intent: str

class WorkflowState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    params: Dict[str, Dict[str, Any]]
    results: Dict[str, Dict[str, Any]]
    supervisor_out: Optional[SupervisorOut]
    current_phase: Optional[str]
    awaiting_input: bool

class PhaseDefinition(TypedDict):
    name: str
    required_params: Type[BaseModel] 
    workflow_function: Callable[[Dict[str, Any]], Dict[str, Any]]
    description: str

class GenerateReportParams(BaseModel):
    user_name: str = Field(
        description="Extract the user's name (look for names like 'Alice', 'John', 'for user X')",
        examples=["Alice", "John", "Sarah"]
    )
    report_type: str = Field(
        description="Extract report type (monthly, quarterly, annual, daily, weekly)",
        examples=["monthly", "quarterly", "annual", "daily", "weekly"]
    )

class ProcessDataParams(BaseModel):
    data_source: str = Field(
        description="Extract data source (sales, user_metrics, analytics, sales_data, etc.)",
        examples=["sales_data", "user_metrics", "analytics", "financial_data"]
    )
    analysis_type: str = Field(
        description="Extract analysis type (trend, performance, comparison, forecast, etc.)",
        examples=["trend", "performance", "comparison", "forecast"]
    )

def generate_report_workflow(params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a user report"""
    print(f"[generate_report_workflow] Executing with params: {params}")
    user_name = params["user_name"]
    report_type = params["report_type"]
    chart_data = [{"month": i+1, "value": len(user_name) * (i+1) * 10} for i in range(6)]
    result = {
        "status": "completed",
        "report_title": f"{report_type} Report for {user_name}",
        "chart_data": chart_data,
        "generated_at": datetime.datetime.utcnow().isoformat()
    }
    print(f"[generate_report_workflow] Generated result: {result}")
    return result

def process_data_workflow(params: Dict[str, Any]) -> Dict[str, Any]:
    """Process data analysis"""
    print(f"[process_data_workflow] Executing with params: {params}")
    data_source = params["data_source"]
    analysis_type = params["analysis_type"]

    result = {
        "status": "completed",
        "data_source": data_source,
        "analysis_type": analysis_type,
        "records_processed": 1000,
        "insights": ["Trend analysis completed", "Anomalies detected: 5", "Performance improved by 15%"],
        "processed_at": datetime.datetime.utcnow().isoformat()
    }
    print(f"[process_data_workflow] Generated result: {result}")
    return result

PHASE_DEFINITIONS: List[PhaseDefinition] = [
    {
        "name": "generate_report",
        "required_params": GenerateReportParams,
        "workflow_function": generate_report_workflow,
        "description": "Generate user reports and analytics"
    },
    {
        "name": "process_data",
        "required_params": ProcessDataParams,
        "workflow_function": process_data_workflow,
        "description": "Process and analyze data from various sources"
    }
]

class GenericSupervisorWorkflow:
    def __init__(self, phase_definitions: List[PhaseDefinition]):
        self.phase_definitions = {pd["name"]: pd for pd in phase_definitions}
        self.phase_names = list(self.phase_definitions.keys())
        self.supervisor_llm = llm.with_structured_output(SupervisorOut)
        self.parameter_extractor_llm = llm
        self.graph = self._build_graph()
    
    def _extract_parameters_from_message(self, message: str, phase_name: str) -> Dict[str, Any]:
        """Extract parameters from natural language message using LLM with Pydantic schema"""
        print(f"[PARAM_EXTRACTOR] Extracting parameters for {phase_name} from: '{message}'")
        phase_def = self.phase_definitions[phase_name]
        param_model = phase_def["required_params"]
        field_descriptions = []
        for field_name, field_info in param_model.model_fields.items():
            description = field_info.description or f"extract the {field_name.replace('_', ' ')}"
            examples = getattr(field_info, 'examples', [])
            example_text = f" Examples: {examples}" if examples else ""
            field_descriptions.append(f"- {field_name} ({field_info.annotation.__name__}): {description}{example_text}")
        
        extraction_prompt = f"""Extract the following parameters from this message: "{message}"
            Required parameters for {phase_name}:
            {chr(10).join(field_descriptions)}
            Return ONLY a JSON object with the extracted parameters. If a parameter cannot be extracted, use null.
            Example: {{"user_name": "Alice", "report_type": "monthly"}}
            Message to analyze: "{message}"
        """
        try:
            response = self.parameter_extractor_llm.invoke(extraction_prompt)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start != -1 and json_end != 0:
                content = content[json_start:json_end]
            extracted = json.loads(content)
            print(f"[PARAM_EXTRACTOR] Extracted parameters: {extracted}")
            required_field_names = list(param_model.model_fields.keys())
            try:
                valid_params = {k: v for k, v in extracted.items() if k in required_field_names and v is not None and v != "null"}
                if valid_params:
                    temp_data = {}
                    for field_name in required_field_names:
                        if field_name in valid_params:
                            temp_data[field_name] = valid_params[field_name]
                    
                    if temp_data:
                        param_model.model_validate(temp_data)
                        print(f"[PARAM_EXTRACTOR] Parameters validated successfully")
                filtered_params = valid_params
            except Exception as validation_error:
                print(f"[PARAM_EXTRACTOR] Validation warning: {validation_error}")
                filtered_params = {k: v for k, v in extracted.items() if k in required_field_names and v is not None and v != "null"}
            print(f"[PARAM_EXTRACTOR] Filtered parameters: {filtered_params}")
            return filtered_params
        except Exception as e:
            print(f"[PARAM_EXTRACTOR] Error extracting parameters: {e}")
            return {}
    
    def _build_graph(self) -> StateGraph:
        builder = StateGraph(WorkflowState)
        builder.add_node("supervisor", self._supervisor_node)
        for phase_name, phase_def in self.phase_definitions.items():
            builder.add_node(phase_name, self._create_phase_node(phase_def))
        builder.add_edge(START, "supervisor")
        for phase_name in self.phase_names:
            builder.add_edge(phase_name, END)
        return builder.compile(checkpointer=MemorySaver())
    
    def _supervisor_node(self, state: WorkflowState) -> Command:
        latest_message = ""
        for msg in reversed(state["messages"]):
            if hasattr(msg, 'content') and msg.__class__.__name__ == "HumanMessage":
                latest_message = msg.content
                break
        
        phase_descriptions = "\n".join([
            f"- {name}: {defn['description']}" 
            for name, defn in self.phase_definitions.items()
        ])
        
        supervisor_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""You are a workflow supervisor. Analyze the user's request and decide which phase to execute.

Available phases:
{phase_descriptions}

Return JSON with:
- next_phase: one of {self.phase_names}
- intent: brief summary of what the user wants to do

Choose the most appropriate phase based on the user's request."""),
            MessagesPlaceholder("messages"),
        ])
        
        try:
            supervisor_decision = self.supervisor_llm.invoke(
                supervisor_prompt.format_messages(messages=state["messages"])
            )
            print(f"[SUPERVISOR] Decision: {supervisor_decision}")
            
            if supervisor_decision["next_phase"] not in self.phase_names:
                print(f"[SUPERVISOR] Invalid phase selected, defaulting to first phase")
                supervisor_decision["next_phase"] = self.phase_names[0]
            
            state["supervisor_out"] = supervisor_decision
            state["current_phase"] = supervisor_decision["next_phase"]
            
            if latest_message:
                extracted_params = self._extract_parameters_from_message(
                    latest_message, supervisor_decision["next_phase"]
                )
                
                phase_name = supervisor_decision["next_phase"]
                if phase_name not in state["params"]:
                    state["params"][phase_name] = {}
                
                state["params"][phase_name].update(extracted_params)
                print(f"[SUPERVISOR] Updated params for {phase_name}: {state['params'][phase_name]}")
            
            print(f"[SUPERVISOR] Routing to phase: {supervisor_decision['next_phase']}")
            return Command(goto=supervisor_decision["next_phase"])
            
        except Exception as e:
            print(f"[SUPERVISOR] Error in decision making: {e}")
            default_phase = self.phase_names[0]
            state["supervisor_out"] = {"next_phase": default_phase, "intent": "default"}
            state["current_phase"] = default_phase
            return Command(goto=default_phase)
    
    def _create_phase_node(self, phase_def: PhaseDefinition):
        """Create a generic phase node"""
        phase_name = phase_def["name"]
        workflow_function = phase_def["workflow_function"]
        def phase_node(state: WorkflowState) -> WorkflowState:
            print(f"[{phase_name.upper()}] Starting phase execution")
            param_model = phase_def["required_params"]
            required_param_names = list(param_model.model_fields.keys())
            print(f"[{phase_name.upper()}] Required params: {required_param_names}")
            if phase_name not in state["params"]:
                state["params"][phase_name] = {}
            
            phase_params = state["params"][phase_name]
            print(f"[{phase_name.upper()}] Current params: {phase_params}")
            missing_params = [param for param in required_param_names if param not in phase_params or phase_params[param] is None]
            if missing_params:
                print(f"[{phase_name.upper()}] Missing parameters: {missing_params}")
                if "__confirmation_requested__" not in phase_params:
                    print(f"[{phase_name.upper()}] Attempting to extract missing parameters from message history")
                    for msg in reversed(state["messages"]):
                        if hasattr(msg, 'content') and msg.__class__.__name__ == "HumanMessage":
                            extracted = self._extract_parameters_from_message(msg.content, phase_name)
                            if extracted:
                                phase_params.update(extracted)
                                print(f"[{phase_name.upper()}] Updated params after extraction: {phase_params}")
                                break
                    
                    missing_params = [param for param in required_param_names if param not in phase_params or phase_params[param] is None]
                
                if missing_params:
                    param_requests = []
                    for param in missing_params:
                        field_info = param_model.model_fields[param]
                        description = field_info.description or f"the {param.replace('_', ' ')}"
                        param_type = field_info.annotation.__name__
                        examples = getattr(field_info, 'examples', [])
                        example_text = f" (e.g., {', '.join(map(str, examples[:3]))})" if examples else ""
                        param_requests.append(f"• {param} ({param_type}): {description}{example_text}")
                    message = f"""
                    To proceed with {phase_name.replace('_', ' ')}, I need the following information: 
                    {chr(10).join(param_requests)} 
                    Please provide these details."""  
                    phase_params["__confirmation_requested__"] = True
                    state["awaiting_input"] = True
                    return {"messages": [AIMessage(content=message)]}
            
            print(f"[{phase_name.upper()}] All parameters available, validating and executing workflow")
            try:
                clean_params = {k: v for k, v in phase_params.items() if not k.startswith("__")}
                try:
                    validated_params = param_model.model_validate(clean_params)
                    print(f"[{phase_name.upper()}] Parameters validated successfully")
                    clean_params = validated_params.model_dump()
                except Exception as validation_error:
                    print(f"[{phase_name.upper()}] Validation error: {validation_error}")
                    error_message = f"❌ Parameter validation failed for {phase_name.replace('_', ' ')}: {str(validation_error)}"
                    return {"messages": [AIMessage(content=error_message)]}
                
                result = workflow_function(clean_params)
                if "results" not in state:
                    state["results"] = {}
                state["results"][phase_name] = result
                print(f"[{phase_name.upper()}] Workflow completed successfully")
                print(f"[{phase_name.upper()}] Result keys: {list(result.keys())}")
                success_message = f"""
                ✅ {phase_name.replace('_', ' ').title()} completed successfully!
                Results Summary:
                - Status: {result.get('status', 'Completed')}
                - Processed at: {result.get('generated_at', result.get('processed_at', 'N/A'))}
                The workflow has been completed and results are available."""
                state["awaiting_input"] = False
                return {"messages": [AIMessage(content=success_message)]}
            except Exception as e:
                print(f"[{phase_name.upper()}] Error executing workflow: {e}")
                error_message = f"❌ Error in {phase_name.replace('_', ' ')}: {str(e)}"
                return {"messages": [AIMessage(content=error_message)]}
        return phase_node
    
    def run_workflow(self, initial_message: str, thread_id: str = "default") -> Dict[str, Any]:
        initial_state = {
            "messages": [HumanMessage(content=initial_message)],
            "params": {},
            "results": {},
            "supervisor_out": None,
            "current_phase": None,
            "awaiting_input": False
        }
        
        try:
            result = self.graph.invoke(initial_state, {"configurable": {"thread_id": thread_id}})
            max_iterations = 3
            iteration = 0
            
            while (result.get("awaiting_input", False) and  iteration < max_iterations and  result.get("results", {}) == {}):
                iteration += 1
                current_phase = result.get("current_phase")
                if current_phase and current_phase in result.get("params", {}):
                    phase_params = result["params"][current_phase]
                    param_model = self.phase_definitions[current_phase]["required_params"]
                    required_param_names = list(param_model.model_fields.keys())
                    missing = [p for p in required_param_names if p not in phase_params or phase_params[p] is None]
                    if not missing:
                        print(f"[WORKFLOW] All parameters available, continuing workflow...")
                        result["messages"].append(HumanMessage(content="continue"))
                        result = self.graph.invoke(result, {"configurable": {"thread_id": thread_id}})
                    else:
                        print(f"[WORKFLOW] Still missing parameters: {missing}")
                        break
                else:
                    break
            return result
        except Exception as e:
            print(f"[WORKFLOW] Error in workflow execution: {e}")
            return {"error": str(e), "results": {}}
    
    def add_user_input(self, user_input: str, thread_id: str = "default") -> Dict[str, Any]:
        input_state = { "messages": [HumanMessage(content=user_input)], "params": {} , "results": {} ,"supervisor_out": None ,"current_phase": None , "awaiting_input": False }
        try:
            result = self.graph.invoke(input_state, {"configurable": {"thread_id": thread_id}})
            return result
        except Exception as e:
            print(f"[WORKFLOW] Error processing user input: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    workflow = GenericSupervisorWorkflow(PHASE_DEFINITIONS)
    test_cases = [
        {
            "name": "Report Generation Test - Explicit",
            "message": "I need to generate a monthly report for user Alice",
            "thread_id": "test_report_explicit"
        },
        {
            "name": "Data Processing Test - Explicit", 
            "message": "Please analyze the sales_data with trend analysis",
            "thread_id": "test_data_explicit"
        },
        {
            "name": "Report Generation Test - Implicit",
            "message": "Create a quarterly report for John",
            "thread_id": "test_report_implicit"
        },
        {
            "name": "Data Processing Test - Implicit",
            "message": "I want to do performance analysis on user_metrics data",
            "thread_id": "test_data_implicit"
        }
    ]
    
    for test in test_cases:
        result = workflow.run_workflow(test["message"], test["thread_id"])
        if "error" in result:
            print(f"❌ Test failed with error: {result['error']}")
        elif "results" in result and result["results"]:
            print("✅ Test completed successfully with results:")
            for phase_name, phase_result in result["results"].items():
                print(f"\n📊 {phase_name.upper()} RESULTS:")
                print(json.dumps(phase_result, indent=2))
        else:
            print("⚠️  Test completed but may require additional input")
            if "messages" in result and result["messages"]:
                last_message = result["messages"][-1]
                if hasattr(last_message, 'content'):
                    print(f"💬 Last message: {last_message.content}")
            if "params" in result and result["params"]:
                print(f"📝 Extracted parameters: {result['params']}")
        
    demo_workflow = GenericSupervisorWorkflow(PHASE_DEFINITIONS)
    demo_messages = [
        "Generate annual report for user Sarah",
        "Create weekly analytics for Bob",
        "Process financial_data with comparison analysis",
        "Analyze customer_metrics using forecast method"
    ]
    
    for msg in demo_messages:
        print(f"\n📝 Testing extraction for: '{msg}'")
        for phase_name in ["generate_report", "process_data"]:
            extracted = demo_workflow._extract_parameters_from_message(msg, phase_name)
            if extracted:
                print(f"🔍 {phase_name}: {extracted}")

    print("\n--- 🚀 Extended Missing-Param Tests ---")
    # 1️⃣ Missing both params for generate_report
    state = workflow.run_workflow("Generate report")
    print(state["messages"][-1].content)  
    # ➜ Should ask for user_name and report_type

    # 2️⃣ Now user supplies only user_name
    state = workflow.run_workflow("Alice")
    print(state["messages"][-1].content)  
    # ➜ Should still ask for report_type

    # 3️⃣ Then user provides report_type
    state = workflow.run_workflow("report_type: monthly")
    # ➜ Should continue and complete successfully
    for msg in state["messages"]:
        print("→", msg.content)

    # 4️⃣ Missing one param (data_source) for process_data
    state = workflow.run_workflow("Process data")
    print(state["messages"][-1].content)
    # ➜ Should ask for data_source & analysis_type

    # 5️⃣ Provide both in one go:
    state = workflow.run_workflow("data_source: sales_data, analysis_type: trend")
    for msg in state["messages"]:
        print("→", msg.content)

    # ✅ Final assert: all phases completed with results
    print("\nOverall results:", state.get("results"))

