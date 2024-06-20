import streamlit as st
import mysql.connector

# Datenbankverbindung herstellen
def connect_to_db():
    return mysql.connector.connect(
        user=st.secrets["user"],
        password=st.secrets["password"],
        host=st.secrets["host"],
        database=st.secrets["database"],
        port=st.secrets["port"]
    )

# Daten aus der Datenbank abrufen
def get_data(query):
    cnx = connect_to_db()
    cursor = cnx.cursor()
    cursor.execute(query)
    response = [row for row in cursor]
    cursor.close()
    cnx.close()
    return response

# Daten in die Datenbank schreiben
def push_data(query, params=None):
    cnx = connect_to_db()
    cursor = cnx.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    cnx.commit()
    cursor.close()
    cnx.close()

# Daten speichern in der Datenbank
def save_data_to_db(evaluations, additional_texts, reviewer_id, groundtruth_ids):
    for i, (evaluation, additional_text) in enumerate(zip(evaluations, additional_texts)):
        groundtruthsegment_id = groundtruth_ids[i]
        query = """
            INSERT INTO RATINGS (groundtruthsegment_id, answersegments, reviewer_id, rating)
            VALUES (%s, %s, %s, %s)
        """
        params = (groundtruthsegment_id, additional_text, reviewer_id, evaluation)
        push_data(query, params)

# Groundtruths abrufen und sortieren
def get_sorted_groundtruths(question_id):
    groundtruths = get_data(f"SELECT * FROM GROUNDTRUTHS WHERE question_id = '{str(question_id)}'")
    return sorted(groundtruths, key=lambda x: x[2])

# Antwortsegmente abrufen und sortieren
def get_sorted_answersegments(answer_id):
    answersegments = get_data(f"SELECT * FROM ANSWERSEGMENTS WHERE answer_id = '{str(answer_id)}'")
    return sorted(answersegments, key=lambda x: x[2])

# Streamlit-State initialisieren
def initialize_state():
    if 'dataset_index' not in st.session_state:
        st.session_state['dataset_index'] = 0

    if 'evaluations' not in st.session_state:
        st.session_state['evaluations'] = [
            [0 for _ in range(len(get_sorted_answersegments(qna_ids_list[0][0])))] 
            for _ in range(len(qna_ids_list))
        ]

    if 'additional_texts' not in st.session_state:
        st.session_state['additional_texts'] = [
            ["" for _ in range(len(get_sorted_answersegments(qna_ids_list[0][0])))] 
            for _ in range(len(qna_ids_list))
        ]

    # Initialisieren Sie den Schlüssel 'error_message'
    if 'error_message' not in st.session_state:
        st.session_state['error_message'] = ""

# UI-Elemente für die Navigation
def render_navigation():
    st.sidebar.title("Navigation")
    col1, col2, col3, col4 = st.sidebar.columns(4)
    with col1:
        st.button("-5", on_click=lambda: st.session_state.update(dataset_index=max(0, st.session_state['dataset_index'] - 5)), key="5_zurück")
    with col2:
        st.button("-1", on_click=lambda: st.session_state.update(dataset_index=max(0, st.session_state['dataset_index'] - 1)), key="zurück")
    with col3:
        st.button("+1", on_click=lambda: st.session_state.update(dataset_index=min(len(qna_ids_list) - 1, st.session_state['dataset_index'] + 1)), key="vor")
    with col4:
        st.button("+5", on_click=lambda: st.session_state.update(dataset_index=min(len(qna_ids_list) - 1, st.session_state['dataset_index'] + 5)), key="5_vor")

# UI-Elemente für Prüferinformationen und Anweisungen
def render_reviewer_info():
    st.sidebar.title("Daten speichern")

    # Prüfer ID validieren
    global reviewer_id
    reviewer_id = st.sidebar.text_input("Prüfer ID:", key="prüfer_id")
    allowed_ids = st.secrets["reviewer_ids"],
    if reviewer_id not in allowed_ids:
        st.session_state['error_message'] = "Ungültige Prüfer ID. Bitte wählen Sie eine gültige ID aus der Liste."
    else:
        st.session_state['error_message'] = ""

    # Senden-Button anzeigen
    st.sidebar.button("Senden", 
        on_click=lambda: save_data_to_db(
            st.session_state['evaluations'][st.session_state['dataset_index']],
            st.session_state['additional_texts'][st.session_state['dataset_index']],
            reviewer_id,
            [gt[0] for gt in get_sorted_groundtruths(qna_ids_list[st.session_state['dataset_index']][1])]
        ), 
        key="senden", 
        disabled=bool(st.session_state['error_message'])
    )
    
    st.sidebar.header("Prüfanweisungen")
    st.sidebar.markdown("Bitte bewerten Sie die Aussagen und geben Sie die Anzahl der relevanten Referenzen an.")
    st.sidebar.markdown("Die Bewertung erfolgt auf einer Skala von 0 bis 4, wobei 0 für 'nicht relevant' und 4 für 'sehr relevant' steht.")
    st.sidebar.markdown("Die Anzahl der relevanten Referenzen sollte als Zahl eingegeben werden.")

# Hauptinhalt rendern
def render_main_content():
    current_index = st.session_state['dataset_index']
    st.header(f"Datensatz {current_index + 1} von {len(qna_ids_list)}")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.header("Groundtruth")
        sorted_groundtruths = get_sorted_groundtruths(qna_ids_list[current_index][1])
        evaluation = []
        additional_texts = []
        for i, groundtruth in enumerate(sorted_groundtruths):
            sub_col1, sub_col2, sub_col3 = st.columns([3, 1, 2])
            with sub_col1:
                st.write(groundtruth[3], groundtruth[4])  # 3 = Index, 4 = Text
            with sub_col2:
                eval_value = st.selectbox(f'Bewertung', range(5), key=f"eval_{current_index}_{i}")
                evaluation.append(eval_value)
            with sub_col3:
                additional_text = st.text_input(f'Relevante Referenzen', key=f"num_{current_index}_{i}")
                additional_texts.append(additional_text)
                # Überprüfung der Texteingaben auf ungültige Zeichen
                allowed_values = [""] + [str(num) for num in range(10)] + [","]
                if not all(char in allowed_values for char in additional_text):
                    st.error("Bitte geben Sie Zahlen ein. Trennen Sie mehrere Zahlen durch Kommata ab. Leere Felder sind erlaubt.")
        st.session_state['evaluations'][current_index] = evaluation
        st.session_state['additional_texts'][current_index] = additional_texts

    with col2:
        st.header("Referenzsätze")
        sorted_answersegments = get_sorted_answersegments(qna_ids_list[current_index][0])
        for answer in sorted_answersegments:
            st.write(answer[2], answer[3])  # 2 = Index, 3 = Text
    
    # Kommentarfunktion nicht implementiert: DB Verbindung fehlt
    # st.header("Kommentare") 
    # st.text_area("Bitte geben Sie hier Ihre Kommentare ein.", height=100, key='comment')

# Setzen Sie das Layout auf "wide"
st.set_page_config(layout="wide")

# Datenabfrage
qna_ids_query = "SELECT answer_id, question_id FROM ANSWERS"
qna_ids_list = get_data(qna_ids_query)

# Initialisierung des States
initialize_state()

# Rendern der Seitenleiste
render_navigation()
render_reviewer_info()

# Rendern des Hauptinhalts
st.title("GAEP-Evaluationstool")
render_main_content()
