import streamlit as st
import pandas as pd
import json
import datetime

# Setzen Sie das Layout auf "wide"
st.set_page_config(layout="wide")

# Beispiel-Daten für die Sätze und die Referenzsätze
data_statements = [
    {
        "dataset": 1,
        "statements": [
            "Körperliche Aktivität soll regelmäßig erfragt werden.",
            "Körperliche Aktivität soll an individuelle Voraussetzungen angepasst werden.",
            "Patient*innen mit COPD, die zu selbstständiger sportlicher Aktivität nicht in der Lage sind, sollte Rehabilitationssport (z. B. Lungensport) empfohlen und verordnet werden."
        ]
    },
    {
        "dataset": 2,
        "statements": [
            "COPD Patient*innen soll eine individuell angepasste Trainingstherapie mit dem Ziel der möglichst eigenständigen Weiterführung angeboten werden.",
            "Zielsetzung der Trainingstherapie ist dabei die Kräftigung und Aktivierung geschwächter Muskulatur."
        ]
    }
]

data_references = [
    {
        "dataset": 1,
        "references": [
            "Allen Patient*innen mit COPD sollen Selbsthilfetechniken bei Atemnot vermittelt werden, einschließlich Schulungen, Lungensport, physiotherapeutischen oder rehabilitativen Interventionen.",
            "Atemphysiotherapie kann als Teil eines physiotherapeutischen Gesamtkonzeptes in Betracht gezogen werden, besonders dann, wenn körperliches Training nicht ausreichend möglich ist.",
            "Alle Patient*innen sollen über den Nutzen von körperlicher Aktivität und körperlichem Training informiert werden.",
            "Es wird empfohlen individuell angepasstes, angeleitetes körperliches Training zu empfehlen.",
            "Patient*innen, die kein körperliches Training außerhalb ihrer Wohnung durchführen können, soll eine individuell angepasste, supervidierte und motivierende häusliche Trainingstherapie angeboten werden."
        ]
    },
    {
        "dataset": 2,
        "references": [
            "Die aktuellen Leitlinien spezifizieren kein direktes Heimübungsprogramm für COPD-Patienten.",
            "Stattdessen wird empfohlen, dass Patienten mit COPD, die nicht außerhalb ihrer Wohnung trainieren können, eine individuell angepasste, supervidierte und motivierende häusliche Trainingstherapie angeboten werden soll.",
            "Diese Therapie zielt darauf ab, die Patienten zu befähigen, das Training möglichst eigenständig fortzuführen."
        ]
    }
]

# Funktion zur Speicherung der Daten als JSON
def save_data(evaluation, additional_numbers, reviewer_id, dataset_index):
    data = {
        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Dataset Index": dataset_index,
        "Statements": data_statements[dataset_index]["statements"],
        "Evaluation": evaluation,
        "Additional Numbers": additional_numbers,
        "Reviewer ID": reviewer_id,
        "Comment": comment
    }
    filename =f"response_{reviewer_id}_{dataset_index}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)

# Funktion zum Löschen der eingegebenen Daten
def clear_data():
    for i in range(len(data_statements[st.session_state['dataset_index']]["statements"])):
        st.session_state[f"eval_{st.session_state['dataset_index']}_{i}"] = 0
        st.session_state[f"num_{st.session_state['dataset_index']}_{i}"] = ""

# Initialisierung des States
if 'dataset_index' not in st.session_state:
    st.session_state['dataset_index'] = 0

if 'evaluations' not in st.session_state:
    st.session_state['evaluations'] = [[0 for _ in range(len(ds["statements"]))] for ds in data_statements]

if 'additional_numbers' not in st.session_state:
    st.session_state['additional_numbers'] = [["" for _ in range(len(ds["statements"]))] for ds in data_statements]

# Titel in der Seitenleiste
st.sidebar.title("Navigation")

# Navigation in der Seitenleiste
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    st.button("Zurück", on_click=lambda: st.session_state.update(dataset_index=max(0, st.session_state['dataset_index'] - 1)), key="zurück")
with col2:
    st.button("Vor", on_click=lambda: st.session_state.update(dataset_index=min(len(data_statements) - 1, st.session_state['dataset_index'] + 1)), key="vor")
with col3:
    st.button("Löschen", on_click=clear_data, key="löschen")

# Senden-Button in der Seitenleiste
st.sidebar.button("Senden", on_click=lambda: save_data(evaluation, additional_numbers, reviewer_id, st.session_state['dataset_index']), key="senden")

# Zwischenüberschrift in der Seitenleiste
st.sidebar.header("Püferinformationen")

# Dropdown für Prüfer ID
reviewer_id = st.sidebar.selectbox("Prüfer ID:", ["ID1", "ID2", "ID3", "ID4", "ID5"], key="prüfer_id")

# Zwischnenüberschrift in der Seitenleiste
st.sidebar.header("Prüfanweisungen")

# Erklärungstext in der Seitenleiste
st.sidebar.markdown("Bitte bewerten Sie die Aussagen und geben Sie die Anzahl der relevanten Referenzen an.")
st.sidebar.markdown("Die Bewertung erfolgt auf einer Skala von 0 bis 4, wobei 0 für 'nicht relevant' und 4 für 'sehr relevant' steht.")
st.sidebar.markdown("Die Anzahl der relevanten Referenzen sollte als Zahl eingegeben werden.")

# Anzeige des Hauptinhalts

# Überschrift im Hauptbereich
st.title("GAEP-Evaluationstool")

# Laden der Daten
current_index = st.session_state['dataset_index']
st.header(f"Datensatz {current_index + 1} von {len(data_statements)}")


# Hauptinhalt in zwei Spalten aufteilen: links für die Sätze und rechts für die Referenzsätze
col1, col2 = st.columns([1, 1])

with col1:
    # Datensatz-Anzeige
    st.header("Groundtruth-Sätze")

    # Anzeige der Sätze und Dropdowns in Spalten
    current_dataset = data_statements[current_index]

    evaluation = []
    additional_numbers = []
    for i, statement in enumerate(current_dataset["statements"]):
        sub_col1, sub_col2, sub_col3 = st.columns([3, 1, 2])
        with sub_col1:
            st.write(statement)
        with sub_col2:
            eval_value = st.selectbox(f'Bewertung', range(5), key=f"eval_{current_index}_{i}")
            evaluation.append(eval_value)
        with sub_col3:
            additional_number = st.text_input(f'Relevante Referenezen', key=f"num_{current_index}_{i}")
            additional_numbers.append(additional_number)

with col2:
    # Referenzsätze
    st.header("Referenzsätze")
    current_references = data_references[current_index]["references"]
    for ref in current_references:
        st.write(ref)

# Kommentarfeld im Hauptbereich
st.header("Kommentare")
comment = st.text_area("Bitte geben Sie hier Ihre Kommentare ein.", height=100)
