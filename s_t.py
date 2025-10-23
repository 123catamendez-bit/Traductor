import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# 🌌 CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Traductor Galáctico", page_icon="🪐", layout="wide")

# 🌠 FONDO TIPO GALAXIA (CSS)
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    background-attachment: fixed;
    color: white;
}
[data-testid="stSidebar"] {
    background: rgba(10, 20, 30, 0.95);
    color: white;
}
h1, h2, h3, h4, h5 {
    color: #a8c8ff !important;
    text-shadow: 0 0 10px #4fc3f7;
}
.stButton>button {
    background: linear-gradient(90deg, #283e51, #485563);
    color: white;
    border-radius: 10px;
    border: none;
    transition: 0.3s;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #0f2027, #2c5364);
    transform: scale(1.05);
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# 🚀 TÍTULO Y DESCRIPCIÓN
st.title("🪐 Traductor Galáctico")
st.subheader("Escucho lo que deseas traducir a través del cosmos ✨")

# 🖼️ Imagen (por ahora comentada)
image = Image.open('galaxia.jpg')
st.image(image, width=300)

with st.sidebar:
    st.subheader("🌠 Panel de Traducción")
    st.write("Presiona el botón, habla lo que deseas traducir, "
             "y elige el idioma de entrada y salida según necesites.")

st.write("🎙️ Toca el botón y habla lo que quieres traducir:")

# 🎤 Botón para activar el reconocimiento de voz
stt_button = Button(label=" Escuchar  🎤", width=300, height=50)
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
        if (value != "") {
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
    debounce_time=0
)

# 🌌 PROCESAMIENTO DE AUDIO Y TRADUCCIÓN
if result:
    if "GET_TEXT" in result:
        st.write("🗣️ Texto detectado:")
        st.info(result.get("GET_TEXT"))

    try:
        os.mkdir("temp")
    except:
        pass

    st.markdown("---")
    st.subheader("🔊 Texto a Audio")

    translator = Translator()
    text = str(result.get("GET_TEXT"))

    in_lang = st.selectbox("🌍 Idioma de Entrada", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    out_lang = st.selectbox("🚀 Idioma de Salida", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    english_accent = st.selectbox("🌎 Acento del Inglés", (
        "Defecto", "Español", "Reino Unido", "Estados Unidos", "Canada", "Australia", "Irlanda", "Sudáfrica"
    ))

    lang_map = {
        "Inglés": "en", "Español": "es", "Bengali": "bn",
        "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"
    }
    tld_map = {
        "Defecto": "com", "Español": "com.mx", "Reino Unido": "co.uk",
        "Estados Unidos": "com", "Canada": "ca", "Australia": "com.au",
        "Irlanda": "ie", "Sudáfrica": "co.za"
    }

    input_language = lang_map.get(in_lang, "en")
    output_language = lang_map.get(out_lang, "en")
    tld = tld_map.get(english_accent, "com")

    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text

    display_output_text = st.checkbox("Mostrar texto traducido")

    if st.button("Convertir 🌌"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## 🔈 Tu audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown("### 💫 Texto traducido:")
            st.write(f"\"{output_text}\"")

    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Deleted ", f)

    remove_files(7)

st.markdown("---")
st.markdown("<center>🌠 Desarrollado entre las estrellas con Streamlit y Bokeh 🌠</center>", unsafe_allow_html=True)
