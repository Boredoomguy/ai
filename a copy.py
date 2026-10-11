import streamlit as ui
from groq import Groq
import tempfile
import os
ui.title("Clanker")
client = Groq(api_key=ui.secrets["GROQ_API"])
if "messages" not in ui.session_state:
    ui.session_state.messages=[]
for message in ui.session_state.messages:
    with ui.chat_message(message['role']):
        ui.write(message['content'])
prompt = ui.chat_input()
if prompt:
    ui.session_state.messages.append({"role": "user", "content": "prompt"})
    with ui.chat_message("user"):
        ui.write(prompt)
    with ui.chat_message("assistant"):  
        with ui.spinner("Thinking..."):
            try:
                messages = [{"role": "system", "content": "You are a helpful assistant."}]
                for message in ui.session_state.messages:
                    messages.append({"role": message["role"], "content": message["content"]})
                response = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=messages,
                        max_tokens=500,
                        temperature=0.7
                    )
                answer = response.choices[0].message.content
            except Exception as e:
                answer = e
        ui.write(answer)
    ui.session_state.messages.append({"role": "assistant", "content": answer})

ui.markdown("---")        
aud = ui.audio_input("say anything")
if aud:
    with ui.spinner("transcribing..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(aud.read())
            tmp_file_path = tmp_file.name
    try:
        with open(tmp_file_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model= "whisper-large-v3",
                file=(os.path.basename(tmp_file_path), f),
                response_format="text"
            )
    finally:
        os.unlink(tmp_file_path)
    if not transcript or len(transcript.strip()) < 2:
        ui.error("not even a single breath.....")
    else:
        ui.session_state.messages.append({"role":"user", "content":transcript})
        with ui.chat_message("user"):
            ui.write(transcript)
        with ui.chat_message("assistant"):
            with ui.spinner("thinking"):
                try: 
                    messages = [{"role":"system","content":"You're a helpful assistant"}]
                    for message in ui.session_state.messages:
                        messages.append({"role": message["role"], "content":message["content"]})
                    response = client.chat.completions.create(
                            model="openai/gpt-oss-120b",
                            messages=messages,
                            max_tokens=500,
                            temperature=0.7
                        )
                    answer = response.choices[0].message.content
                except Exception as e:
                    answer = e
            ui.write(answer)
        ui.session_state.messages.append({"role": "assistant", "content": answer})