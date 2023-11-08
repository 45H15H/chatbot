import streamlit as st
import os


# App title
st.set_page_config(
    page_title = "Chatbot", 
    page_icon = "c", layout = "wide", 
    initial_sidebar_state = "auto", 
    menu_items = None
)

# OpenAI Credentials
with st.sidebar:
    api_key = st.text_input('Enter your OpenAI API token:', type = 'password')
    if not (api_key.startswith('sk-') and len(api_key) == 51):
        st.warning('Please enter your credentials!', icon = '⚠️')
    else:
        st.success("Proceed to entering your prompt message!", icon = '✅')
    # os.environ['OPENAI_API_KEY'] = api_key

    st.subheader('Models and parameters')

    selected_model = st.sidebar.selectbox(
        ':blue[Choose a model]',
        ['gpt-3.5-turbo', 'davinci'], 
        index = None, 
        key = 'selected_model', 
        placeholder='select a model', 
        help = "A set of models that improve on GPT-3 and can understand as well as generate natural language or code")
    
    if selected_model == 'davinci':
        model_function = ''
    elif selected_model == 'gpt-turbo-3.5':
        model_function = ''
    temperature = st.sidebar.slider('temperature', min_value=0.0, max_value=2.0, value = 0.0, step = 0.01)
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8)

# Store LLM generated responses
if "message" not in st.session_state.keys():
    st.session_state.messages = [{
        "role": "assistant",
        "content": "How may I assist you today?"
    }]

# Display or clear chat messages 
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar='🤖'):
        st.write(message['content'])

def clear_chat_history():
    st.session_state.messages = [{
        "role": "assistant",
        "content": "How may I assist you today?"
    }]

st.sidebar.button('Clear Chat History', on_click = clear_chat_history)

# function for generating responses
def generate_response(message):
    import openai
    prompt = f'Conversation with a chatbot\n\nHuman: {message}\nAI:'
    response = openai.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = [{"role": "user",
                     "content": prompt}],
        temperature = temperature,
    )
    return response.choices[0].message.content

# user-provided prompt message
if prompt := st.chat_input(disabled = not api_key):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    with st.chat_message('user'):
        st.write(prompt)

# generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message('assistant'):
        with st.spinner("Thinking..."):
            response = generate_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)

    message = {
        "role": 'assistant',
        "content": full_response
    }
    st.session_state.messages.append(message)