from groq import Groq

GROQ_API_KEY = "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"
groq_client = Groq(api_key=GROQ_API_KEY)

def preguntar_groq(pregunta):
    respuesta = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": pregunta}]
    )
    return respuesta.choices[0].message.content