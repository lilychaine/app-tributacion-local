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
MODES = ["Secuencial", "Aleatorio", "Simulacro 20", "Repaso de errores"]

# -----------------------------
# ESTADO
# -----------------------------
DEFAULTS = {
    "setup_done": False,
    "queue": [],
    "index": 0,
    "answered": False,
    "selected": None,
    "score_ok": 0,
    "score_bad": 0,
    "current_topic": "Todos",
    "current_mode": "Secuencial",
    "wrong_questions": [],
    "show_reference": True,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


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
    elif mode == "Repaso de errores":
        items = st.session_state.wrong_questions.copy()
        # Evitar duplicados por id
        seen = set()
        deduped = []
        for q in items:
            if q["id"] not in seen and (topic == "Todos" or q["topic"] == topic):
                seen.add(q["id"])
                deduped.append(q)
        items = deduped

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


def register_wrong_question(question):
    if not any(q["id"] == question["id"] for q in st.session_state.wrong_questions):
        st.session_state.wrong_questions.append(question)


def clear_current_answer_state():
    st.session_state.answered = False
    st.session_state.selected = None


def next_question():
    st.session_state.index += 1
    clear_current_answer_state()


# -----------------------------
# INTERFAZ
# -----------------------------
st.title("Estudio Tributacion Local")
st.caption("Test interactivo basado en questions_local.json")

with st.sidebar:
    st.subheader("Marcador")
    total = st.session_state.score_ok + st.session_state.score_bad
    pct = round((st.session_state.score_ok / total) * 100, 2) if total else 0.0
    st.write(f"Aciertos: {st.session_state.score_ok}")
    st.write(f"Errores: {st.session_state.score_bad}")
    st.write(f"Porcentaje: {pct}%")
    st.write(f"Falladas acumuladas: {len(st.session_state.wrong_questions)}")
    st.checkbox("Mostrar referencia normativa", key="show_reference")

    if st.session_state.setup_done:
        st.write(f"Bloque: {st.session_state.current_topic}")
        st.write(f"Modo: {st.session_state.current_mode}")
        st.write(
            f"Pregunta: {min(st.session_state.index + 1, max(len(st.session_state.queue), 1))}/{len(st.session_state.queue)}"
        )
        progress = st.session_state.index / len(st.session_state.queue) if st.session_state.queue else 1.0
        st.progress(min(progress, 1.0))

if not st.session_state.setup_done:
    st.subheader("Configuracion inicial")
    topic = st.selectbox("Bloque", TOPICS)
    mode = st.selectbox("Modalidad", MODES)

    if mode == "Repaso de errores" and len(st.session_state.wrong_questions) == 0:
        st.info("Aun no has fallado preguntas. Primero haz un test normal para alimentar este modo.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Empezar test"):
            reset_quiz(topic, mode)
            st.rerun()
    with col2:
        if st.button("Borrar falladas acumuladas"):
            st.session_state.wrong_questions = []
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

        if total > 0:
            if pct >= 80:
                st.success("Muy buen resultado.")
            elif pct >= 60:
                st.warning("Resultado aceptable, pero conviene repasar los errores.")
            else:
                st.error("Conviene repasar el bloque antes de seguir.")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Repetir misma configuracion"):
                reset_quiz(st.session_state.current_topic, st.session_state.current_mode)
                st.rerun()
        with col2:
            if st.button("Nueva configuracion"):
                st.session_state.setup_done = False
                clear_current_answer_state()
                st.rerun()
        with col3:
            if st.button("Ir a repaso de errores"):
                st.session_state.setup_done = False
                st.session_state.current_mode = "Repaso de errores"
                st.rerun()

    else:
        st.caption(f"Bloque: {q['topic']} | ID: {q['id']}")
        st.subheader(f"Pregunta {st.session_state.index + 1}")
        st.write(q["question"])

        selected = st.radio(
            "Elige una opcion",
            ["A", "B", "C", "D"],
            format_func=lambda x: f"{x}) {q['options'][x]}",
            key=f"radio_{q['id']}_{st.session_state.index}"
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
                    register_wrong_question(q)

                st.rerun()

        with col2:
            if st.button("Cambiar configuracion"):
                st.session_state.setup_done = False
                clear_current_answer_state()
                st.rerun()

        if st.session_state.answered:
            if st.session_state.selected == q["answer"]:
                st.success(f"Correcta. Respuesta: {q['answer']}")
            else:
                st.error(f"Incorrecta. Respuesta correcta: {q['answer']}")

            st.write("Explicacion:", q["explanation"])
            if st.session_state.show_reference:
                st.write("Referencia:", q["reference"])

            if st.button("Siguiente pregunta"):
                next_question()
                st.rerun()
