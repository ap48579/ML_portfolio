# Agentic AI setup to process images and answer questions. 
# chatollama is deprecated and hence doesnt support vision models. 

from typing import Literal
from typing import Annotated, Optional, Dict, List
from typing_extensions import TypedDict
from pathlib import Path
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState, END
from langgraph.types import Command
import ollama
import subprocess
import base64, httpx


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    


members = ["QnA", "OCR"]

options = members + ["FINISH"]

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""

    next: Literal["QnA", "OCR", "FINISH"]



llm1 = ChatOllama(
    model="llama3.2",  
    temperature=0.7  
)

llm2 = ChatOllama(
    model="llama3.2-vision",  
    temperature=0.7   
)

class State(BaseModel):
    user_q: str
    goto:Optional[str] = None
    action: Optional[str] = None
    qna_response: Optional[str] = None
    ocr_response: Optional[str] = None


def supervisor_node(state: State) -> State:
    print("--"*50)
    print("\n🔧 SUPERVISOR AGENT ACTIVATED")

    messages=[
            {'role': 'system', 'content': f"""You are a supervisor that picks if the user is asking about food label route to : {members[1]} or route to {members[0]} Return ONLY the worker name or 'FINISH'."""},
            {'role': 'user', 'content': f'Answer this user question: {state.user_q}',
    'images': [encode_image(Path("images")/"sample_image.jpeg")]}
        ]
    
    state.action = llm2.with_structured_output(Router).invoke(messages)

    state.goto = state.action["next"]

    print(f"Supervisor action : {state.action}")

    print(f"Next step : {state.goto}")
    
    return state


def QnA_agent(state: State) -> State:
    print("--"*50)
    print("\n🔧 QnA AGENT ACTIVATED")


    # messages=[
    #         {'role': 'system', 'content': f"""You are a simple question and answer bot. Be polite and respectful"""},
    #         {'role': 'user', 'content': f"""Given the below user question, start with greeting the user. Then follow up with answering the user question.
    #                  {state.user_q}""",
    # 'images': [encode_image(Path("images")/"sample_image.jpeg")]}
    #     ]
    
    state.qna_response = ollama.chat(
    model='llama3.2-vision',
    messages = [{'role': 'system', 'content': f"""You are a simple question and answer bot. Be polite and respectful"""},
                {'role': 'user', 'content': 'what is this image about?','images': [encode_image(Path("images")/"sample_image.jpeg")]}])['message']['content']
    
    print(f"Model response: {state.qna_response}")
    return state


def OCR_agent(state: State) -> State:
    print("--"*50)
    print("\n🔧 OCR AGENT ACTIVATED")
    
    # messages=[
    #             {'role': 'system', 'content': f"""Extract nutrition facts as JSON. Return only valid JSON."""},
    #             {'role': 'user', 'content': f"""Process this food label:""",'images': [encode_image(Path("images")/"sample_image.jpeg")]}
    #         ]

    state.ocr_response =  ollama.chat(
    model='llama3.2-vision',
    messages = [{'role': 'system', 'content': f"""Extract nutrition facts as JSON. Return only valid JSON."""},
                {'role': 'user', 'content': f"""Process this food label:""",'images': [encode_image(Path("images")/"sample_image.jpeg")]}])['message']['content']
    
    
    print(f"Model response: {state.ocr_response}")
    return state


def decide_question_type(state):

    if state.goto == "FINISH":
        return END
    else:
        return state.goto


workflow = StateGraph(State)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("QnA", QnA_agent)
workflow.add_node("OCR", OCR_agent)

workflow.set_entry_point("supervisor")
workflow.add_conditional_edges(
    "supervisor",
    decide_question_type
)

workflow.add_edge("QnA", END)

workflow.add_edge("OCR", END)


app = workflow.compile()



state = State(user_q="""
Does the item have sugar and how much? 
""")

result = app.invoke(state)

# print(f"Final Code:\n{result['code']}")
# print(f"Comprehensive Tests:\n{result['final_tests']}")
# print(f"Validation Results: {result['test_results']}")
# print(f"Iterations Used: {result['iteration']}")

