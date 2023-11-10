import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import g4f

prompt = ""


def main():
    global prompt

    st.title("💬 Chatbot бот от Михалыча")
    st.caption("🚀 Чат бот готов к вашим запросам")

    recognition = st.toggle('Выкл/Вкл записи микрофона')

    stt_button = Button(label="Запись с микрофона", width=100, disabled=False, button_type="primary")
    stt_button.js_on_event("button_click", CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
    
        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if ( value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        }
        recognition.start();
        """))

    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0)

    if result:
        if "GET_TEXT" in result:
            #st.write(result.get("GET_TEXT"))
            if recognition:
                prompt = result.get("GET_TEXT")
                print(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.write(prompt)
            






    # Хранить сгенерированные LLM ответы
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "Привет! Я искусственный интеллект, созданный для помощи в различных задачах. Я могу отвечать на вопросы, предоставлять информацию, помогать в поиске решений, переводить тексты на разные языки, создавать напоминания и многое другое. Если у тебя есть какие-либо конкретные вопросы или задачи, я постараюсь помочь!"}]


    # Отображение или удаление сообщений чата
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])








    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Generating..."):
                print("Prompt: ", prompt)
                #st.chat_message("assistant").write("Generating...")
                response = g4f.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": f"{prompt}"}],
            )
                print("Response: ", response)

                placeholder = st.empty()
                full_response = ''
                for item in response:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)


    # User-provided prompt
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)


if __name__ == '__main__':
    main()