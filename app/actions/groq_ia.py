import os
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def preguntar_groq(pregunta: str) -> str:
    """Consulta al modelo Llama en Groq de forma rápida."""
    global groq_client
    if not groq_client:
        current_key = os.getenv("GROQ_API_KEY", "")
        if current_key:
            groq_client = Groq(api_key=current_key)
        else:
            return "Clave GROQ_API_KEY no configurada en las variables de entorno."
    try:
        respuesta = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": pregunta}]
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error en consulta a Groq: {str(e)}"