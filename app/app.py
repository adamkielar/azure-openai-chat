import base64
import os
import streamlit as st
import streamlit_authenticator as stauth
import yaml

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate
from yaml.loader import SafeLoader
from streamlit_option_menu import option_menu
from langchain.chat_models import AzureChatOpenAI

from constants import SVG


def setup_auth():
    with open(os.path.join(os.path.dirname(__file__), 'config.yaml')) as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    authenticator.login('Login', 'main')

    return authenticator

@st.cache_resource
def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)

def main_menu():
    with st.sidebar:
        selected = option_menu(
            "Main Menu",
            ["Chat", "Logout"],
            icons=["chat", "logout"],
            menu_icon="cast",
            default_index=0,
        )

    return selected


def get_prompt():
    _template = """Use the following pieces of context and chat history to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Context: {context}

    Chat History: {chat_history}

    Human: {question}

    Assistant:"""
    prompt = PromptTemplate(template=_template, input_variables=["context", "chat_history", "question"])
    return prompt

@st.cache_resource
def get_openai_model():
    openai_key = os.getenv("AZURE_OPENAI_KEY")
    openai_base_url = os.getenv("AZURE_OPENAI_BASE_URL")

    llm = AzureChatOpenAI(
        base_url=openai_base_url,
        openai_api_version="2023-07-01-preview",
        openai_api_key=openai_key,
        openai_api_type="azure"
    )

    return llm

@st.cache_resource
def init_memory():
    return StreamlitChatMessageHistory(key="langchain_messages")

def chat():
    llm_prompt = get_prompt()
    openai_llm = get_openai_model()
    msgs = init_memory()
    if len(msgs.messages) == 0 or st.sidebar.button("Clear chat history"):
        msgs.clear()
        msgs.add_ai_message("How can I help you?")

    for msg in msgs.messages:
        st.chat_message(msg.type).write(msg.content)

    llm_chain = LLMChain(llm=openai_llm, prompt=llm_prompt, verbose=True)

    if prompt := st.chat_input():
        st.chat_message("human").write(prompt)
        msgs.add_user_message(prompt)
        history = " ".join([msg.content for msg in msgs.messages if msg.type == "ai"])
        response = llm_chain.run({"context": "", "chat_history": history, "question": prompt})
        st.chat_message("ai").write(response)
        msgs.add_ai_message(response)


def main():
    st.set_page_config(page_title="Chat with your data")
    load_dotenv()
    ss = st.session_state
    authenticator = setup_auth()


    if ss["authentication_status"]:
        render_svg(SVG)
        st.title("Chatbot R&D")
        st.write(f"Welcome *{ss['name']}*. I'm here to assist you.")
        selected = main_menu()
        if selected == "Chat":
            chat()
        elif selected == "Logout":
            authenticator.logout('Logout', 'main')
    elif ss["authentication_status"] == False:
        st.error('Username/password is incorrect')
    elif ss["authentication_status"] == None:
        st.warning('Please enter your username and password')


if __name__ == '__main__':
    main()