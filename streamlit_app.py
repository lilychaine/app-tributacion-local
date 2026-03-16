import json
import random
import streamlit as st

st.set_page_config(page_title="Estudio Tributacion Local", layout="centered")

# -----------------------------
# CARGA DE PREGUNTAS
# -----------------------------
with open("questions_local.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

TOPICS = ["Todos"] + sorted(list({q["topic"] for q in QUESTIONS}))
MODES = ["Secuencial", "Aleatorio", "Simulacro 20"]

# -----------------------------
# ESTADO
# -----------------------------
if "setup_done" not in st.session_state:
    st.session_state.setup_done = False
if "queue" not in st.session_state:
    st.session_state.queue = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "answered" not in st.session_state:
    st.session_state.answered = False
if "selected" not in st.session_state:
    st.session_state.selected = None
if "score_ok" not in st.session_state:
    st.session_state.score_ok = 0
if "score_bad" not in st.session_state:
    st.session_state.score_bad = 0
if "current_topic" not in st.session_state:
    st.session_state.current_topic = "Todos"
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "Secuencial"

# -----------------------------
# FUNCIONES
# -----------------------------
def build_queue(topic: str, mode: str):
    items = [q for q in QUESTIONS if topic == "Todos" or q["topic"] == topic]

    if mode == "Secuencial":
        items = sorted(items, key=lambda x: x["id"])
    elif mode == "Aleatorio":
        random.shuffle(items)
    elif mode == "Simulacro 20":
        random.shuffle(items)
        items = items[:20]

    return items


def reset_quiz(topic: str, mode: str):
    st.session_state.current_topic = topic
    st.session_state.current_mode = mode
    st.session_state.queue = build_queue(topic, mode)
    st.session_state.index = 0
    st.session_state.answered = False
    st.session_state.selected = None
    st.session_state.score_ok = 0
    st.session_state.score_bad = 0
    st.session_state.setup_done = True


def current_question():
    if 0 <= st.session_state.index < len(st.session_state.queue):
        return st.session_state.queue[st.session_state.index]
    return None

# -----------------------------
# INTERFAZ
# -----------------------------
st.title("Estudio Tributacion Local")

with st.sidebar:
    st.subheader("Marcador")
    total = st.session_state.score_ok + st.session_state.score_bad
    pct = round((st.session_state.score_ok / total) * 100, 2) if total else 0.0
    st.write(f"Aciertos: {st.session_state.score_ok}")
    st.write(f"Errores: {st.session_state.score_bad}")
    st.write(f"Porcentaje: {pct}%")

    if st.session_state.setup_done:
        st.write(f"Bloque: {st.session_state.current_topic}")
        st.write(f"Modo: {st.session_state.current_mode}")
        st.write(
            f"Pregunta: {min(st.session_state.index + 1, max(len(st.session_state.queue), 1))}/{len(st.session_state.queue)}"
        )

if not st.session_state.setup_done:
    st.subheader("Configuracion inicial")

    topic = st.selectbox("Bloque", TOPICS)
    mode = st.selectbox("Modalidad", MODES)

    if st.button("Empezar test"):
        reset_quiz(topic, mode)
        st.rerun()

else:
    q = current_question()

    if q is None:
        st.subheader("Test finalizado")
        total = st.session_state.score_ok + st.session_state.score_bad
        pct = round((st.session_state.score_ok / total) * 100, 2) if total else 0.0

        st.write(f"Aciertos: {st.session_state.score_ok}")
        st.write(f"Errores: {st.session_state.score_bad}")
        st.write(f"Porcentaje: {pct}%")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Repetir misma configuracion"):
                reset_quiz(st.session_state.current_topic, st.session_state.current_mode)
                st.rerun()

        with col2:
            if st.button("Nueva configuracion"):
                st.session_state.setup_done = False
                st.rerun()

    else:
        st.caption(f"Bloque: {q['topic']} | ID: {q['id']}")
        st.subheader(f"Pregunta {st.session_state.index + 1}")
        st.write(q["question"])

        selected = st.radio(
            "Elige una opcion",
            ["A", "B", "C", "D"],
            format_func=lambda x: f"{x}) {q['options'][x]}",
            key=f"radio_{q['id']}"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Responder") and not st.session_state.answered:
                st.session_state.selected = selected
                st.session_state.answered = True

                if selected == q["answer"]:
                    st.session_state.score_ok += 1
                else:
                    st.session_state.score_bad += 1

                st.rerun()

        with col2:
            if st.button("Cambiar configuracion"):
                st.session_state.setup_done = False
                st.rerun()

        if st.session_state.answered:
            if st.session_state.selected == q["answer"]:
                st.success(f"Correcta. Respuesta: {q['answer']}")
            else:
                st.error(f"Incorrecta. Respuesta correcta: {q['answer']}")

            st.write("Explicacion:", q["explanation"])
            st.write("Referencia:", q["reference"])

            if st.button("Siguiente pregunta"):
                st.session_state.index += 1
                st.session_state.answered = False
                st.session_state.selected = None
                st.rerun()