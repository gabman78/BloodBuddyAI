import os
import json
import time
import numpy as np
from elasticsearch import Elasticsearch  # type: ignore
from groq import Groq  # type: ignore
import pinecone  # type: ignore
from pinecone import Pinecone, ServerlessSpec  # type: ignore
from sentence_transformers import SentenceTransformer  # type: ignore
from elasticsearch import Elasticsearch  # type: ignore
import streamlit as st

# Groq client
groq_client = Groq(api_key="")

# Connessione Elasticsearch
es = Elasticsearch(
    hosts=[os.environ.get("ELASTIC_HOST", "http://localhost:9200")],
    request_timeout=30,
    verify_certs=False
)

# Pinecone
pc = Pinecone(api_key="")
index_name = "documenti-teorici768"
index = pc.Index(index_name)

embed_model = SentenceTransformer("pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb")

# Cerca pazienti
def cerca_pazienti(input_data, index="index1", size=5):
    if isinstance(input_data, dict):
        must_clauses = []
        for campo, valore in input_data.items():
            if isinstance(valore, (int, float)):
                delta = valore * 0.1
                must_clauses.append({"range": {campo: {"gte": valore - delta, "lte": valore + delta}}})
            elif isinstance(valore, str):
                must_clauses.append({"match": {campo: {"query": valore, "fuzziness": "AUTO"}}})
        query = {"query": {"bool": {"must": must_clauses}}, "size": size}
    elif isinstance(input_data, str):
        mapping = es.indices.get_mapping(index=index)
        properties = mapping[index]['mappings']['properties']
        campi_testuali = []
        for campo, info in properties.items():
            if info.get('type') == 'object':
                for subcampo, subinfo in info.get('properties', {}).items():
                    if subinfo.get('type') in ['text', 'keyword']:
                        campi_testuali.append(f"{campo}.{subcampo}")
            elif info.get('type') in ['text', 'keyword']:
                campi_testuali.append(campo)
        query = {
            "query": {
                "bool": {
                    "should": [
                        {"multi_match": {"query": input_data, "fields": campi_testuali, "fuzziness": "AUTO"}}
                    ]
                }
            },
            "size": size
        }
    else:
        raise ValueError("Input non valido")

    results = es.search(index=index, body=query)
    return [hit["_source"] for hit in results["hits"]["hits"]]

# Cerca teoria
def cerca_in_pinecone(domanda, index, embedding_model, top_k=3):
    query_embedding = embedding_model.encode(domanda).tolist()
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    return [match['metadata']['testo'] for match in results['matches']]

# Prompt
def costruisci_prompt(paziente_info, ocr_txt, domanda, contesto_pazienti, contesto_teorico):
    sez_ocr = (
        f"\n📄 **Le seguenti sono le analisi del sangue personali dell’utente** (da OCR):\n{ocr_txt}\n\n"
        "➡️ **Analizza questi valori come prioritari.** Commenta ciascun valore con chiarezza, segnalando se è normale,"
        "alto o basso, e fornisci spiegazioni mediche, rassicuranti e pratiche.\n"
        "Se mancano dati importanti, dillo esplicitamente e suggerisci esami da fare o domande da porre al medico."
    )


    prompt_finale = f"""
Sei BloodBuddy, un assistente digitale medico che aiuta le persone a comprendere i risultati delle **loro analisi del sangue** e i sintomi, 
in modo empatico, chiaro, umano. Parla come un bravo medico di famiglia: diretto, rassicurante, ma sempre preciso.

Questa è una conversazione continuativa: rispondi **in modo coerente** senza ripetere saluti o premesse ogni volta. 
Rivolgiti sempre in seconda persona (usa "tu"), perché stai parlando direttamente con il paziente.

❗ Non inventare valori. Se mancano dati, dillo esplicitamente. 
❗ NON dire mai frasi come “non ho accesso ai tuoi dati” o “sto usando dati di altri pazienti”. 
Usa i dati OCR se ci sono, e considera i confronti come semplice supporto statistico.

📌 Dati del paziente (usa questi per orientare la risposta, come se li avesse appena detti lui stesso):
{paziente_info}

{sez_ocr}

📂 📊 Dati statistici di riferimento (pazienti simili, da un database clinico anonimo):
{contesto_pazienti}

📚 Supporto medico-teorico (fonti affidabili per spiegazioni cliniche):
{contesto_teorico}

❓ Domanda dell’utente:
{domanda}

📣 Rispondi in modo utile, rassicurante, clinicamente fondato. Se non trovi valori, aiuta comunque: guida l’utente su cosa osservare, chiedere o fare.
"""
    return prompt_finale

# Chiamata LLaMA
def chiedi_a_llama(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = groq_client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": "Sei BloodBuddy, un assistente digitale medico che accompagna le persone a comprendere i loro esami. "
                                                 "Non ripetere saluti o nomi a ogni messaggio, mantieni la conversazione naturale. "
                                                 "Parla in modo empatico e discorsivo, ma non impersonale. "
                                                 "Non dire mai di essere un'intelligenza artificiale."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Tentativo {attempt + 1} fallito: {e}")
            time.sleep(3)
    return "Errore persistente."

# Normalizza input
def normalize_input(input_data):
    if isinstance(input_data, dict):
        return "\n".join(f"{k}: {v}" for k, v in input_data.items())
    elif isinstance(input_data, str):
        return input_data
    else:
        raise ValueError("Input non valido")

# Workflow completo
def esegui_workflow(paziente_info, ocr_output, domanda):
    # ✅ Recupera eventuale referto persistente
    if not ocr_output.strip() and "ocr_output" in st.session_state:
        ocr_output = st.session_state.ocr_output

    paziente_txt = normalize_input(paziente_info)
    ocr_txt = normalize_input(ocr_output)

    contesto_pazienti = cerca_pazienti(ocr_txt)
    contesto_teorico = cerca_in_pinecone(domanda, index, embed_model)

    contesto_teorico_txt = "\n---\n".join(contesto_teorico)
    contesto_pazienti_txt = "\n---\n".join([json.dumps(p, indent=2) for p in contesto_pazienti])

    prompt_finale = costruisci_prompt(paziente_txt, ocr_txt, domanda, contesto_pazienti_txt, contesto_teorico_txt)

    risposta = chiedi_a_llama(prompt_finale)
    return risposta
