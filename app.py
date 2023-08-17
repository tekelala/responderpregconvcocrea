import streamlit as st
import requests
import json

with open("convocatoria.txt", "r") as file:
    context = file.read()

def send_message(prompts):
    api_url = "https://api.anthropic.com/v1/complete"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": st.secrets["API_KEY"]
    }

    conversation = "\n\n".join([f'{item["role"]}: {item["content"]}' for item in prompts]) + "\n\nAssistant:"


    body = {
        "prompt": conversation,
        "model": "claude-2.0",
        "max_tokens_to_sample": 100000,
        "temperature": 0,
        "stop_sequences": ["\n\nHuman:"]
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(body))
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        st.error(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        st.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        st.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        st.error(f"Something went wrong: {err}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

    result = response.json()
    return result['completion'].strip()

st.title("Preguntale a la convocatoria CoCrea")
st.write("¡No te quedes con la duda!")

if "prompts" not in st.session_state:
    st.session_state.prompts = []

if "new_message" not in st.session_state:
    st.session_state.new_message = False

for prompt in st.session_state.prompts:
    if prompt['role'] == "Human":
        with st.chat_message("Human", avatar="🧑‍💻"):
            st.write(prompt['content'])
    else: # role == "Assistant"
        with st.chat_message(name="CoCreaBot", avatar="🤖"):
            st.write(prompt['content'])

if not st.session_state.new_message:
    pregunta = st.chat_input("¿Cuál es tu duda?") 
    if user_message: 
        user_message = f'''Role: You are an AI assistant trained in the formulation of creative and cultural economy projects using the logical framework methodology. Give your answers in Spanish and do not say which task you are doing.
                    Do the following tasks: 
                    Task 1: Read and understand the rules of the CoCrea call. Here are the rules {context}.
                    Task 2: Answer the following question {pregunta} based in the rules of the call, if you do not know the anwer to the question say so'''
        st.session_state.new_message = True
        st.session_state.prompts.append({"role": "Human", "content": user_message })
        with st.spinner(text='Writing...'):
            response_from_claude = send_message(st.session_state.prompts)
            st.session_state.prompts.append({"role": "Assistant", "content": response_from_claude})
            st.session_state.new_message = False
            st.experimental_rerun()


if st.button('Restart'):
    st.session_state.prompts = []
    st.session_state.new_message = False
    st.experimental_rerun()
