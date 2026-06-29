import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Dossier où on sauvegarde les conversations
DOSSIER_CONVERSATIONS = "conversations"
if not os.path.exists(DOSSIER_CONVERSATIONS):
    os.makedirs(DOSSIER_CONVERSATIONS)


def lister_conversations():
    """Renvoie la liste des fichiers de conversation triés du plus récent au plus ancien."""
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


# Configuration de la page
st.set_page_config(page_title="Mon ChatBot", page_icon="💬")

# Initialisation de la session
if "fichier_actuel" not in st.session_state:
    st.session_state.fichier_actuel = None
if "historique" not in st.session_state:
    st.session_state.historique = []

# --- BARRE LATERALE ---
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

# --- ZONE PRINCIPALE DE CHAT ---
st.title("Mon ChatBot")

# Affiche tous les messages de l'historique
for message in st.session_state.historique:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie en bas de l'écran
question = st.chat_input("Écris ton message ici...")

if question:
    # Si c'est la première fois qu'on écrit dans cette conversation, on crée le fichier
    if st.session_state.fichier_actuel is None:
        st.session_state.fichier_actuel = nouveau_nom_fichier()

    # Ajoute le message de l'utilisateur à l'historique et l'affiche
    st.session_state.historique.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Demande la réponse à Groq et l'affiche
    with st.chat_message("assistant"):
        with st.spinner("Réflexion..."):
            reponse = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.historique
            )
            reponse_bot = reponse.choices[0].message.content
        st.markdown(reponse_bot)

    # Ajoute la réponse à l'historique
    st.session_state.historique.append({"role": "assistant", "content": reponse_bot})

    # Sauvegarde la conversation sur le disque
    sauvegarder_conversation(st.session_state.fichier_actuel, st.session_state.historique)
  
 st.set_page_config(page_title="MoonIA", page_icon="💬")

st.title("MoonIA")