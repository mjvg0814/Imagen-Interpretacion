import os
import streamlit as st
import base64
from openai import OpenAI

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# Configuración de la página de Streamlit
st.set_page_config(page_title="Análisis de Imagen", layout="centered", initial_sidebar_state="collapsed")
st.title("Análisis de Imagen 🤖🏞️")

# Barra lateral para ingresar la clave de API
st.sidebar.header("Configuración")
ke = st.sidebar.text_input('Ingresa tu Clave de API', type='password')
os.environ['OPENAI_API_KEY'] = ke

# Recuperar la clave de API de OpenAI
api_key = os.environ['OPENAI_API_KEY']

# Inicializar el cliente de OpenAI
client = OpenAI(api_key=api_key)

# Cargador de archivos para que el usuario agregue su propia imagen
uploaded_file = st.file_uploader("📤 Carga una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Mostrar la imagen cargada
    with st.expander("Vista Previa de la Imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Toggle para mostrar detalles adicionales
show_details = st.checkbox("¿Agregar detalles sobre la imagen?", value=False)

if show_details:
    # Campo de texto para detalles adicionales sobre la imagen
    additional_details = st.text_area(
        "Agrega contexto sobre la imagen aquí:",
        disabled=not show_details
    )

# Botón para iniciar el análisis
analyze_button = st.button("Analizar la Imagen", type="primary")

# Comprobar si se ha subido una imagen, si hay una clave API disponible y si se ha presionado el botón
if uploaded_file is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        # Codificar la imagen
        base64_image = encode_image(uploaded_file)

        # Texto del prompt optimizado
        prompt_text = "Describe lo que ves en la imagen en español."

        if show_details and additional_details:
            prompt_text += f"\n\nContexto adicional proporcionado por el usuario:\n{additional_details}"

        # Crear el payload para la solicitud de completado
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ]

        # Realizar la solicitud a la API de OpenAI
        try:
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4-vision-preview", messages=messages,   
                max_tokens=1200, stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
else:
    # Advertencias para acciones requeridas del usuario
    if not uploaded_file and analyze_button:
        st.warning("Por favor, carga una imagen.")
    if not api_key:
        st.warning("Por favor, ingresa tu clave API.")
