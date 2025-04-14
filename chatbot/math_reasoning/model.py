# This file has agent infrastructure and model related files. 
from typing import Literal
from typing import Annotated, Optional, Dict, List
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState, END
from langgraph.types import Command
import subprocess


members = ["QnA", "python_planning"]

options = members + ["FINISH"]

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""

    next: Literal["QnA", "python_planning", "FINISH"]





llm = ChatOllama(
    model="llama3.2",  
    temperature=0.7  
)

class State(BaseModel):
    user_q: str
    goto:Optional[str] = None
    action: Optional[str] = None
    qna_response: Optional[str] = None
    plan: Optional[str] = None
    code: Optional[str] = None
    validation_tests: Optional[str] = None
    final_tests: Optional[str] = None
    test_results: Optional[Dict] = None
    errors: List[str] = []
    iteration: int = 0


def supervisor_node(state: State) -> State:
    print("--"*50)
    print("\n🔧 SUPERVISOR AGENT ACTIVATED")
    
    messages = [
        SystemMessage(content="You are a supervior to decide what is the user interested in between simple chat or coding task."),
        HumanMessage(content=f"""Given the below user question you have to choose between the following workers : {members} :
        {state.user_q}
        respond with the worker to act next. Each worker will perform a
   task and respond with their results and status. When finished,
   respond with FINISH.""")
    ]
    state.action = llm.with_structured_output(Router).invoke(messages)

    state.goto = state.action["next"]
    
    return state


def QnA_agent(state: State) -> State:
    print("--"*50)
    print("\n🔧 QnA AGENT ACTIVATED")
    
    messages = [
        SystemMessage(content="You are a simple question and answer bot. Be polite and respectful"),
        HumanMessage(content=f"""Given the below user question, start with greeting the user. Then follow up with answering the user question. Apart from your primary functions you also help the user with python coding tasks and unittest creation.
        {state.user_q}""")
    ]
    state.qna_response = llm.invoke(messages).content
    
    print(f"Model response: {state.qna_response}")
    return state


def decide_question_type(state):

    if state.goto == "FINISH":
        return END
    else:
        return state.goto


def planner_agent(state: State) -> State:
    print("--"*50)
    print("\n🔧 PLANNER AGENT ACTIVATED")
    
    messages = [
        SystemMessage(content="You are a senior software architect"),
        HumanMessage(content=f"""Create development plan for:
        {state.user_q}
        Include implementation steps and testing strategy.""")
    ]
    state.plan = llm.invoke(messages).content

    print(f"Generated plan:\n{state.plan}...")
    print("--"*50)
    print("--"*50)
    return state


def coder_agent(state: State) -> State:
    print("--"*50)
    print("\n🔧 CODER AGENT ACTIVATED")
    messages = [
        SystemMessage(content="You are a Python coding expert"),
        HumanMessage(content=f"""Write Python code for:
        {state.user_q}
        Follow this plan: {state.plan}""")
    ]
    state.code = llm.invoke(messages).content
    print(f"Generated Code:\n{state.code[:200]}...")
    print("--"*50)
    print("--"*50)
    return state


def tester_agent(state: State) -> State:
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

def executor_agent(state: State) -> State:
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

def debugger_agent(state: State) -> State:
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


def unittest_generator_agent(state: State) -> State:
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

workflow = StateGraph(State)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("QnA", QnA_agent)
workflow.add_node("python_planning", planner_agent)
workflow.add_node("coder", coder_agent)
workflow.add_node("tester", tester_agent)
workflow.add_node("executor", executor_agent)
workflow.add_node("debugger", debugger_agent)
workflow.add_node("unittest_gen", unittest_generator_agent)

workflow.set_entry_point("supervisor")
workflow.add_conditional_edges(
    "supervisor",
    decide_question_type
)

workflow.add_edge("QnA", END)

workflow.add_edge("python_planning", "coder")
workflow.add_edge("coder", "tester")
workflow.add_edge("tester", "executor")


def decide_next(state: State):
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



# state = State(user_q="""
# Hello. What can you do to help me today?
# """)

# result = app.invoke(state)

# print(f"Final Code:\n{result['code']}")
# print(f"Comprehensive Tests:\n{result['final_tests']}")
# print(f"Validation Results: {result['test_results']}")
# print(f"Iterations Used: {result['iteration']}")
