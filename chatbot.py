import ollama

historique = []

while True:
    message = input("Toi : ")

    if message == "quit":
        break

    historique.append({"role": "user", "content": message})

    reponse = ollama.chat(
        model="llama3.2",
        messages=historique
    )

    reponse_bot = reponse["message"]["content"]
    print("Bot :", reponse_bot)


   