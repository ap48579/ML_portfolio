# This file has agent infrastructure and model related files. 

from typing import Annotated, Optional, Dict, List
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
import subprocess


llm = ChatOllama(
    model="llama3.2",  
    temperature=0.7  
)

class CodingState(BaseModel):
    problem: str
    plan: Optional[str] = None
    code: Optional[str] = None
    validation_tests: Optional[str] = None
    final_tests: Optional[str] = None
    test_results: Optional[Dict] = None
    errors: List[str] = []
    iteration: int = 0

def planner_agent(state: CodingState) -> CodingState:
    print("--"*50)
    print("\n🔧 PLANNER AGENT ACTIVATED")
    
    messages = [
        SystemMessage(content="You are a senior software architect"),
        HumanMessage(content=f"""Create development plan for:
        {state.problem}
        Include implementation steps and testing strategy.""")
    ]
    state.plan = llm.invoke(messages).content

    
    
    print(f"Generated plan:\n{state.plan}...")
    print("--"*50)
    print("--"*50)
    return state


def coder_agent(state: CodingState) -> CodingState:
    print("--"*50)
    print("\n🔧 CODER AGENT ACTIVATED")
    messages = [
        SystemMessage(content="You are a Python coding expert"),
        HumanMessage(content=f"""Write Python code for:
        {state.problem}
        Follow this plan: {state.plan}""")
    ]
    state.code = llm.invoke(messages).content
    print(f"Generated Code:\n{state.code[:200]}...")
    print("--"*50)
    print("--"*50)
    return state


def tester_agent(state: CodingState) -> CodingState:
    print("--"*50)
    print("\n🔧 TESTER AGENT ACTIVATED")
    messages = [
        SystemMessage(content="You are a Python coding expert"),
        HumanMessage(content=f"""Create basic validation tests for:
    {state.code}
    Focus on core functionality only.""")
    ]
    
    state.validation_tests = llm.invoke(messages).content
    print(f"Generated validation tests:\n{state.validation_tests[:200]}...")
    print("--"*50)
    print("--"*50)
    return state

def executor_agent(state: CodingState) -> CodingState:
    print("--"*50)
    print('Execution agent is activated')
    try:
        
        result = subprocess.run(["python", "-c", state.code + "\n" + state.validation_tests],capture_output=True,text=True,timeout=30)
        state.test_results = {"passed": True}
    except subprocess.TimeoutExpired:
        state.errors.append("Execution timed out after 30 seconds")
    except subprocess.CalledProcessError as e:
        state.errors.append(f"Test failed: {e.stderr}")
    print(f"Current state of execution is:\n{state.test_results}")
    print("--"*50)
    print("--"*50)
    return state

def debugger_agent(state: CodingState) -> CodingState:
    print("--"*50)
    print('Debugger agent is activated')
    messages = [
        SystemMessage(content="You are a senior debugger"),
        HumanMessage(content=f"""Fix this code:
        {state.code}
        Error: {state.errors[-1]}
        Tests: {state.validation_tests}""")
    ]
    state.code = llm.invoke(messages).content
    state.iteration += 1
    print(f"Current debugging step is:{state.iteration}")
    print("--"*50)
    print("--"*50)
    return state


def unittest_generator_agent(state: CodingState) -> CodingState:
    print("--"*50)
    print("Finished with code generation and working on unittest creation!!!")
    messages = [
        SystemMessage(content="You are a senior python coder"),
        HumanMessage(content=f"""Generate comprehensive pytest unit tests for:
    {state.code}
    Include parameterized tests, edge cases, and descriptive test names.""")
    ]

    state.final_tests = llm.invoke(messages).content
    print("--"*50)
    print("--"*50)
    return state

workflow = StateGraph(CodingState)

workflow.add_node("planner", planner_agent)
workflow.add_node("coder", coder_agent)
workflow.add_node("tester", tester_agent)
workflow.add_node("executor", executor_agent)
workflow.add_node("debugger", debugger_agent)
workflow.add_node("unittest_gen", unittest_generator_agent)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "coder")
workflow.add_edge("coder", "tester")
workflow.add_edge("tester", "executor")


def decide_next(state: CodingState):
    print("--"*50)
    if state.test_results["passed"]:
        print("Passed all tests")
        return "unittest_gen"
    if state.iteration >= 3:
        print(f"Max iterations reached!!!")
        return "end"
    return "debugger"



workflow.add_conditional_edges(
    "executor",
    decide_next,
    {"end": END, "debugger": "debugger", "unittest_gen": "unittest_gen"}
)
workflow.add_edge("debugger", "coder")
workflow.add_edge("unittest_gen", END)

app = workflow.compile()



# state = CodingState(problem="""
# Create a Python function to check prime numbers.
# Handle edge cases and provide efficient implementation.
# """)

# result = app.invoke(state)

# print(f"Final Code:\n{result['code']}")
# print(f"Comprehensive Tests:\n{result['final_tests']}")
# print(f"Validation Results: {result['test_results']}")
# print(f"Iterations Used: {result['iteration']}")
