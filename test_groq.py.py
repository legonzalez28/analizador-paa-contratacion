import socket
# Fuerza IPv4
socket.has_ipv6 = False
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
print("KEY:", os.getenv("GROQ_API_KEY")[:10] + "...") # Solo primeros 10 chars

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
r = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Di hola en JSON"}],
    response_format={"type": "json_object"}
)
print(r.choices[0].message.content)