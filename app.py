import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DOSSIER_CONVERSATIONS = "conversations"
if not os.path.exists(DOSSIER_CONVERSATIONS):
    os.makedirs(DOSSIER_CONVERSATIONS)


def lister_conversations():
    fichiers = [f for f in os.listdir(DOSSIER_CONVERSATIONS) if f.endswith(".json")]
    fichiers.sort(reverse=True)
    return fichiers


def charger_conversation(nom_fichier):
    chemin = os.path.join(DOSSIER_CONVERSATIONS, nom_fichier)
    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)


def sauvegarder_conversation(nom_fichier, historique):
    chemin = os.path.join(DOSSIER_CONVERSATIONS, nom_fichier)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)


def nouveau_nom_fichier():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"


st.set_page_config(page_title="MoonIA", page_icon="💬")
st.markdown("""
<style>
/* Fond général */
.stApp {
    background-color: #1a1a1a;
}

/* Police plus douce */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}

/* Supprime les bulles de chat */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 1.2rem 0 !important;
    max-width: 700px;
    margin: 0 auto;
}

/* Largeur du contenu central, comme Claude */
.block-container {
    max-width: 700px;
    padding-top: 2rem;
}

/* Titre plus discret */
h1 {
    font-size: 1.8rem !important;
    font-weight: 600 !important;
}

/* Barre latérale plus sobre */
[data-testid="stSidebar"] {
    background-color: #161616;
}

/* Zone de saisie en bas */
[data-testid="stChatInput"] {
    max-width: 700px;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("💬 Conversations")

    if st.button("➕ Nouvelle conversation", use_container_width=True):
        st.session_state.fichier_actuel = nouveau_nom_fichier()
        st.session_state.historique = []
        st.rerun()

    st.divider()

    conversations = lister_conversations()
    for fichier in conversations:
        nom_affiche = fichier.replace(".json", "")
        if st.button(nom_affiche, key=fichier, use_container_width=True):
            st.session_state.fichier_actuel = fichier
            st.session_state.historique = charger_conversation(fichier)
            st.rerun()

st.title("MoonIA")

for message in st.session_state.historique:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Écris ton message ici...")

if question:
    if st.session_state.fichier_actuel is None:
        st.session_state.fichier_actuel = nouveau_nom_fichier()

    st.session_state.historique.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Réflexion..."):
            reponse = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.historique
            )
            reponse_bot = reponse.choices[0].message.content
        st.markdown(reponse_bot)

    st.session_state.historique.append({"role": "assistant", "content": reponse_bot})

    sauvegarder_conversation(st.session_state.fichier_actuel, st.session_state.historique)st.markdown
    st.markdown("""
<style>
.stApp {
    background-color: #1a1a1a;
}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}

[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 1.2rem 0 !important;
    max-width: 700px;
    margin: 0 auto;
}

.block-container {
    max-width: 700px;
    padding-top: 2rem;
}

h1 {
    font-size: 1.8rem !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] {
    background-color: #161616;
}

[data-testid="stChatInput"] {
    max-width: 700px;
    margin: 0 auto;
}

[data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)