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


def sauvegarder_conversation(nom_fichier, historique, titre):
    chemin = os.path.join(DOSSIER_CONVERSATIONS, nom_fichier)
    donnees = {"titre": titre, "messages": historique}
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)


def nouveau_nom_fichier():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"


def generer_titre(premier_message):
    try:
        reponse = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Donne un titre tres court (4 mots maximum, sans guillemets, "
                        "sans ponctuation finale) qui resume ce message : "
                        f"\"{premier_message}\""
                    )
                }
            ]
        )
        titre = reponse.choices[0].message.content.strip()
        titre = titre.replace('"', '').replace("«", "").replace("»", "")
        return titre[:40]
    except Exception:
        return premier_message[:40]


st.set_page_config(page_title="MoonIA", page_icon="💬")

st.markdown("""
<style>
.stApp {
    background-color: #1a1a1a;
    font-size: 17px;
}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}

.block-container {
    max-width: 700px;
    padding-top: 2rem;
}

h1 {
    font-size: 2rem !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] {
    background-color: #161616;
    font-size: 16px;
}

[data-testid="stChatInput"] {
    max-width: 700px;
    margin: 0 auto;
}

[data-testid="stChatInput"] textarea {
    font-size: 17px !important;
}

.user-bubble {
    background-color: #2b2b2b;
    color: #f5f5f5;
    border-radius: 14px;
    padding: 0.75rem 1.1rem;
    display: inline-block;
    max-width: 80%;
    text-align: left;
    font-size: 17px;
    line-height: 1.6;
}

.user-bubble-wrapper {
    display: flex;
    justify-content: flex-end;
    margin: 0.9rem 0;
}

.bot-wrapper {
    text-align: left;
    margin: 0.9rem 0;
}

.bot-wrapper b {
    font-size: 16px;
}

.bot-text {
    color: #e8e8e8;
    font-size: 17px;
    line-height: 1.65;
}

button {
    font-size: 15px !important;
}
</style>
""", unsafe_allow_html=True)

if "fichier_actuel" not in st.session_state:
    st.session_state.fichier_actuel = None
if "historique" not in st.session_state:
    st.session_state.historique = []
if "titre_actuel" not in st.session_state:
    st.session_state.titre_actuel = None

with st.sidebar:
    st.title("💬 Conversations")

    if st.button("➕ Nouvelle conversation", use_container_width=True):
        st.session_state.fichier_actuel = None
        st.session_state.historique = []
        st.session_state.titre_actuel = None
        st.rerun()

    st.divider()
    st.caption("Récents")

    conversations = lister_conversations()
    for fichier in conversations:
        donnees = charger_conversation(fichier)
        titre_affiche = donnees.get("titre", fichier.replace(".json", ""))
        if st.button(titre_affiche, key=fichier, use_container_width=True):
            st.session_state.fichier_actuel = fichier
            st.session_state.historique = donnees.get("messages", [])
            st.session_state.titre_actuel = titre_affiche
            st.rerun()

st.title("MoonIA")


def afficher_message_user(texte):
    st.markdown(
        f'<div class="user-bubble-wrapper"><div class="user-bubble">{texte}</div></div>',
        unsafe_allow_html=True
    )


def afficher_message_bot(texte):
    st.markdown(
        f'<div class="bot-wrapper"><b>🌙 MoonIA</b><br><span class="bot-text">{texte}</span></div>',
        unsafe_allow_html=True
    )


for message in st.session_state.historique:
    if message["role"] == "user":
        afficher_message_user(message["content"])
    else:
        afficher_message_bot(message["content"])

question = st.chat_input("Écris ton message ici...")

if question:
    premiere_fois = st.session_state.fichier_actuel is None

    if premiere_fois:
        st.session_state.fichier_actuel = nouveau_nom_fichier()

    st.session_state.historique.append({"role": "user", "content": question})
    afficher_message_user(question)

    with st.spinner("MoonIA est en train d'écrire..."):
        reponse = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.historique
        )
        reponse_bot = reponse.choices[0].message.content

    afficher_message_bot(reponse_bot)

    st.session_state.historique.append({"role": "assistant", "content": reponse_bot})

    if premiere_fois:
        st.session_state.titre_actuel = generer_titre(question)

    sauvegarder_conversation(
        st.session_state.fichier_actuel,
        st.session_state.historique,
        st.session_state.titre_actuel
    )

    if premiere_fois:
        st.rerun()
       
        