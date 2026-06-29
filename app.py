import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import requests

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

DOSSIER_CONVERSATIONS = "conversations"
if not os.path.exists(DOSSIER_CONVERSATIONS):
    os.makedirs(DOSSIER_CONVERSATIONS)

# Personnalite / instructions cachees donnees au bot
PERSONNALITE = (
    "Tu es MoonIA, un assistant IA chaleureux, clair et serviable. "
    "Tu reponds en francais sauf si on te demande une autre langue. "
    "Tu es concis mais complet, et tu expliques les choses simplement."
)


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


def a_besoin_recherche_web(message):
    """Detecte si la question necessite probablement une recherche web."""
    mots_cles = [
        "aujourd'hui", "actualite", "actualites", "recent", "recente",
        "derniere", "dernier", "maintenant", "en ce moment", "2026",
        "qui est le president", "meteo", "score", "resultat", "prix actuel",
        "cours de", "nouvelles"
    ]
    message_minuscule = message.lower()
    return any(mot in message_minuscule for mot in mots_cles)


def rechercher_sur_le_web(requete):
    """Effectue une recherche web via Tavily et renvoie un resume textuel des resultats."""
    if not TAVILY_API_KEY:
        return None
    try:
        reponse = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": requete,
                "max_results": 4,
                "include_answer": True
            },
            timeout=10
        )
        donnees = reponse.json()
        resultats_texte = ""
        if donnees.get("answer"):
            resultats_texte += f"Resume: {donnees['answer']}\n\n"
        for resultat in donnees.get("results", []):
            resultats_texte += f"- {resultat.get('title', '')}: {resultat.get('content', '')[:300]}\n"
        return resultats_texte if resultats_texte else None
    except Exception:
        return None


def extraire_texte_fichier(fichier_televerse):
    """Extrait le texte d'un fichier televerse (txt ou pdf)."""
    nom = fichier_televerse.name.lower()
    if nom.endswith(".txt"):
        return fichier_televerse.read().decode("utf-8", errors="ignore")
    elif nom.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            lecteur = PdfReader(fichier_televerse)
            texte = ""
            for page in lecteur.pages:
                texte += page.extract_text() or ""
            return texte
        except Exception:
            return "(Impossible de lire ce PDF)"
    return "(Format de fichier non pris en charge)"


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
if "contexte_fichier" not in st.session_state:
    st.session_state.contexte_fichier = None

with st.sidebar:
    st.title("💬 Conversations")

    if st.button("➕ Nouvelle conversation", use_container_width=True):
        st.session_state.fichier_actuel = None
        st.session_state.historique = []
        st.session_state.titre_actuel = None
        st.session_state.contexte_fichier = None
        st.rerun()

    st.divider()

    fichier_televerse = st.file_uploader(
        "📎 Joindre un fichier (.txt ou .pdf)",
        type=["txt", "pdf"]
    )
    if fichier_televerse is not None:
        if st.button("Analyser ce fichier", use_container_width=True):
            texte_extrait = extraire_texte_fichier(fichier_televerse)
            st.session_state.contexte_fichier = texte_extrait[:8000]
            st.success(f"Fichier '{fichier_televerse.name}' pret a etre discute !")

    st.divider()
    st.caption("Récents")

    conversations = lister_conversations()
    for fichier in conversations:
        donnees = charger_conversation(fichier)
        if not isinstance(donnees, dict):
            continue
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

    # Construit les messages a envoyer, avec personnalite + contexte fichier + recherche web
    messages_a_envoyer = [{"role": "system", "content": PERSONNALITE}]

    if st.session_state.contexte_fichier:
        messages_a_envoyer.append({
            "role": "system",
            "content": (
                "Voici le contenu d'un fichier fourni par l'utilisateur, "
                "utilise-le pour repondre si pertinent :\n\n"
                f"{st.session_state.contexte_fichier}"
            )
        })

    if a_besoin_recherche_web(question):
        with st.spinner("Recherche d'informations recentes..."):
            resultats_web = rechercher_sur_le_web(question)
        if resultats_web:
            messages_a_envoyer.append({
                "role": "system",
                "content": (
                    "Voici des resultats de recherche web recents, "
                    "utilise-les pour repondre de facon a jour :\n\n"
                    f"{resultats_web}"
                )
            })

    messages_a_envoyer.extend(st.session_state.historique)

    with st.spinner("MoonIA est en train d'écrire..."):
        reponse = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_a_envoyer
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