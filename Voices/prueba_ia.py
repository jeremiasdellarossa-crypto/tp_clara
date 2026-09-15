import ollama
respuesta = ollama.chat(
    model="llama3.2",
    messages=[
        {
            "role": "user",
            "content": "Hola, presentate en una oración."
        }
    ]
)
print(respuesta["message"]["content"])