# 🩸 BloodBuddyAI

> **L'assistente virtuale intelligente per comprendere le analisi del sangue.**
> Progetto realizzato per il corso di *AI System Engineering* presso l'Università degli Studi di Napoli Federico II.

[cite_start]BloodBuddyAI è un'applicazione web basata su un'architettura **RAG (Retrieval-Augmented Generation)** avanzata[cite: 13, 14, 18]. [cite_start]Permette agli utenti di caricare i propri referti ematochimici, estrarne i dati automaticamente e ricevere spiegazioni chiare, empatiche e clinicamente contestualizzate grazie alla potenza dei LLM di ultima generazione[cite: 1, 3, 12, 13].

---

## ✨ Funzionalità Principali

* 📄 **Scansione e Parsing dei Referti (OCR):** Carica immagini (JPG, PNG) o PDF. [cite_start]Il sistema utilizza PaddleOCR e OpenCV per estrarre e normalizzare automaticamente i valori e le unità di misura[cite: 14, 17, 18, 19].
* 💬 **Chat Medica Intelligente:** Poni domande sui tuoi sintomi o sui tuoi esami. [cite_start]Il modello risponde con un tono empatico e rassicurante, agendo come un medico di base virtuale[cite: 1, 3, 12, 13, 14].
* 👤 **Profilo Clinico Personalizzato:** Crea un profilo con i tuoi dati (età, peso, patologie pregresse, farmaci). [cite_start]L'IA userà queste informazioni per contestualizzare l'analisi[cite: 3, 12, 13, 14].
* 🧠 **Architettura RAG a doppia via:**
    * [cite_start]**Retrieval Clinico:** Cerca pazienti reali simili nel dataset NHANES (indicizzato su Elasticsearch) per fornire un supporto statistico[cite: 3, 13, 14, 15, 18].
    * [cite_start]**Retrieval Teorico:** Recupera nozioni mediche teoriche vettorializzate tramite BioBERT (su Pinecone) per garantire accuratezza scientifica[cite: 3, 13, 14, 18].
* [cite_start]🔒 **Privacy by Design:** Nessun dato, referto o chat viene salvato in modo permanente per addestrare il modello[cite: 3, 4].

---

## 🛠️ Stack Tecnologico

[cite_start]L'applicazione è costruita con un'architettura monolitica modulare, interamente containerizzata con Docker[cite: 5, 13, 14, 18].

* [cite_start]**Frontend:** [Streamlit](https://streamlit.io/) [cite: 14]
* [cite_start]**LLM & Inferenza:** [LLaMA 4 Scout](https://ai.meta.com/llama/) via [Groq API](https://groq.com/) per latenze ultra-basse[cite: 13, 14, 18].
* [cite_start]**Vettorializzazione Semantica:** `pritamdeka/BioBERT` (tramite HuggingFace Sentence Transformers)[cite: 14, 18].
* [cite_start]**Vector Database (Teoria):** [Pinecone](https://www.pinecone.io/) [cite: 13, 14, 18]
* [cite_start]**Search Engine (Dati Clinici):** [Elasticsearch](https://www.elastic.co/) (Eseguito in locale via Docker)[cite: 13, 14, 18].
* [cite_start]**OCR Pipeline:** PaddleOCR, OpenCV, PIL, pdf2image[cite: 14, 18].
* [cite_start]**Deploy:** Docker & Docker Compose[cite: 14, 18].

---

## 🚀 Installazione e Avvio Rapido

[cite_start]Grazie a Docker, l'avvio del progetto in locale è estremamente rapido[cite: 5, 14, 18].

### Prerequisiti
* [cite_start][Docker](https://www.docker.com/) e Docker Compose installati sul sistema[cite: 5, 18].
* Chiave API di **Groq** (da inserire nel codice o via `.env`).
* Chiave API e Index Name di **Pinecone** configurati per il retrieval teorico.

### Passaggi

1.  **Clona il repository:**
    ```bash
    git clone [https://github.com/tuo-username/BloodBuddyAI.git](https://github.com/tuo-username/BloodBuddyAI.git)
    cd BloodBuddyAI
    ```

2.  **Prepara i dati clinici (opzionale ma consigliato):**
    Assicurati che il file `databaseHealth.json` (estratto dal dataset NHANES) sia presente nella root del progetto. [cite_start]Verrà caricato automaticamente in Elasticsearch[cite: 13, 14, 15, 18].

3.  **Avvia i container:**
    Esegui il build e avvia i servizi (Elasticsearch e l'app Streamlit):
    ```bash
    docker-compose up --build
    ```

4.  **Accedi all'app:**
    Apri il browser e vai all'indirizzo: `http://localhost:8501` [cite: 18]

---

## 📂 Struttura del Progetto

```text
BloodBuddyAI/
├── app1.py                   # Interfaccia UI principale (Streamlit) [cite: 14, 18, 20]
├── bloodbuddy_module.py      # Core RAG, Prompt Engineering e chiamate a LLaMA/Groq [cite: 14, 18]
├── ocr_pipeline.py           # Pipeline di preprocessamento visivo ed estrazione testo (PaddleOCR) [cite: 14, 18, 19]
├── load_data.py              # Script per il caricamento iniziale del database clinico su Elasticsearch
├── docker-compose.yaml       # Orchestrazione dei container (App + Elasticsearch) [cite: 5, 14, 18]
├── Dockerfile                # Configurazione dell'immagine per l'app Streamlit [cite: 5, 14, 18]
├── requirements.txt          # Dipendenze Python [cite: 14, 18]
├── user_profiles.json        # Database locale mock per i profili utente [cite: 14, 18, 20]
└── databaseHealth.json       # Dataset clinico NHANES (non incluso nel repo di base) [cite: 13, 14, 15]
