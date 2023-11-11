import streamlit as st
import os
import time

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
        st.toast('Refreshed')
        time.sleep(0.5)

    st.subheader('Models and Parameters')

    selected_model = st.sidebar.selectbox(
        ':blue[Choose a Model]',
        ['gpt-3.5-turbo', 'gpt-3.5-turbo-1106', 'text-davinci-002'], 
        index = None, 
        key = 'selected_model', 
        placeholder='select a model', 
        help = "A set of models that improve on GPT-3 and can understand as well as generate natural language or code",
        disabled=not api_key)
    
    if api_key and not selected_model:
        st.warning("Please select a model.")

    temperature = st.sidebar.slider(':blue[Temperature]', min_value=0.0, max_value=2.0, value = 0.0, step = 0.01, help = 'Controls the randomness of the model\'s output.', disabled=not api_key)
    
    max_length = st.sidebar.slider(':blue[Maximum Length]', min_value=100, max_value=2000, value=500, step=10, help = 'Controls the maximum length of the model\'s response.', disabled=not api_key)

    # independent_completions = st.sidebar.number_input(":blue[Independent Completions]", value=1, help = 'Number of independent completions to generate from the same prompt.', disabled=not api_key)

    stream = st.sidebar.toggle(label=':blue[Stream Output]', help = '(simulation) Return partial results as they become available, instead of waiting until the computation is done.', disabled=not api_key)

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
    openai.api_key = api_key
    prompt = f'Conversation with a chatbot\n\nHuman: {message}\nAI:'
    chat_response = openai.chat.completions.create(
        model = selected_model,
        messages = [{"role": "user",
                     "content": prompt}],
        temperature = temperature,
        max_tokens=max_length,
        # n = independent_completions,
        stream = stream
    )
    if stream:
        response = ""
        for part in chat_response:
            response += part.choices[0].delta.content or ""
        return response
    else:
        return chat_response.choices[0].message.content
    

def generate_response_davinci(message):
    import openai
    openai.api_key = api_key
    completion = openai.completions.create(
        model=selected_model,
        prompt = prompt,
        max_tokens=max_length,
        stream = stream
    )
    if stream:
        response = ""
        for part in completion:
            response += part.choices[0].text or ""
        return response
    else:
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
                assistant_response = generate_response_gpt_turbo(prompt)
            elif selected_model[0] == 't':
                assistant_response = generate_response_davinci(prompt)
            placeholder = st.empty()
            full_response = ''
            if stream:
                # Simulate stream of response with milliseconds delay
                for item in assistant_response.split():
                    full_response += item + " "
                    time.sleep(0.05)
                    # Blinking cursor to simulate typing
                    placeholder.markdown(full_response + "| ")
            else:
                for item in assistant_response:
                    full_response  += item
            placeholder.markdown(full_response)

    message = {
        "role": 'assistant',
        "content": full_response
    }
    st.session_state.messages.append(message)