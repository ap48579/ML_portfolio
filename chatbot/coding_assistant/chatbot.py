import streamlit as st
from streamlit_chat import message
import time
from model import app, State

st.set_page_config(page_title="Leetcode assistant", page_icon=":speech_balloon:")

# Initialize session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Sidebar for clearing the chat
clear_button = st.sidebar.button("Clear Conversation", key="clear")

if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

st.title("Leetcode assistant")

# Create a container for the chat history
response_container = st.container()

# Create a container for the user's text input
container = st.container()

# Function to simulate the chatbot's response (replace with actual LLM integration later)
def generate_response(user_question):
    state = State(user_q=user_question)

    result = app.invoke(state)
    if result['goto']=="QnA":
        return f"{result['qna_response']}"
    else:
        return f"This is the generated code: {result['code']} \n this is the generated unit test: {result['final_tests']} "

# User input
with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        st.session_state['past'].append(user_input)
        st.session_state['messages'].append({"role": "user", "content": user_input})
        
        response = generate_response(user_input)
        st.session_state['generated'].append(response)
        st.session_state['messages'].append({"role": "assistant", "content": response})

# Display chat history
if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))

# Floating input box at the bottom
st.markdown(
    """
    <style>
    .stApp {
        margin-bottom: 80px;
    }
    .fixed-input {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: white;
        padding: 20px;
        z-index: 1000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="fixed-input">
        <p>You:</p>
    </div>
    """,
    unsafe_allow_html=True
)
