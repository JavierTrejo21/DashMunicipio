import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("No se encontró OPENAI_API_KEY en el archivo .env")

client = OpenAI(api_key=api_key)


def preguntar_ia(pregunta):

    respuesta = client.responses.create(
        model="gpt-5",
        instructions="""
        Eres el asistente de inteligencia artificial del
        Sistema Municipal de Chapulhuacán.

        Tu función es ayudar a analizar información municipal,
        indicadores, obras, presupuesto, PMD, PBR y datos
        administrativos.

        Responde siempre en español.
        Sé claro, preciso y estructurado.
        No inventes datos que no estén disponibles.
        """,
        input=pregunta
    )

    return respuesta.output_text
