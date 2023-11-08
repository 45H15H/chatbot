import streamlit as st
import os

# App title
st.set_page_config(
    page_title = "Chatbot", 
    page_icon = "D:\chatbot\openai-white-logomark.svg" , layout = "wide", 
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

    st.subheader('Models and Parameters')

    selected_model = st.sidebar.selectbox(
        ':blue[Choose a Model]',
        ['gpt-3.5-turbo', 'gpt-3.5-turbo-1106', 'text-davinci-002'], 
        index = None, 
        key = 'selected_model', 
        placeholder='select a model', 
        help = "A set of models that improve on GPT-3 and can understand as well as generate natural language or code"
        )

    temperature = st.sidebar.slider(':blue[Temperature]', min_value=0.0, max_value=2.0, value = 0.0, step = 0.01, help = 'Controls the randomness of the model\'s output.')
    
    max_length = st.sidebar.slider(':blue[Maximum Length]', min_value=32, max_value=128, value=120, step=8, help = 'Controls the maximum length of the model\'s response.')

    independent_completions = st.sidebar.text_input(":blue[Independent Completions]", value=1, help = 'Number of independent completions to generate from the same prompt.')

    stream = st.sidebar.checkbox(label='Stream Output', help = 'Return partial results as they become available, instead of waiting until the computation is done.')

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
def generate_response_gpt_turbo(message):
    import openai
    prompt = f'Conversation with a chatbot\n\nHuman: {message}\nAI:'
    chat_response = openai.chat.completions.create(
        model = selected_model,
        messages = [{"role": "user",
                     "content": prompt}],
        temperature = temperature,
        stream = True
    )
    response = ""
    for part in chat_response:
        response += part.choices[0].delta.content or ""
    return response

def generate_response_davinci(message):
    import openai
    completion = openai.completions.create(
    model=selected_model,
    prompt = prompt,
    max_tokens=500
    # stream=True
    # )
    # response = ""
    # for part in completion:
    #     response += part.choices[0].text or ""
    # return response
    )

    return completion.choices[0].text

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
            if selected_model[0] == 'g':
                response = generate_response_gpt_turbo(prompt)
            elif selected_model[0] == 't':
                response = generate_response_davinci(prompt)
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