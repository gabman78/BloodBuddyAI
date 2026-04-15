# 🩸 BloodBuddyAI

> **L'assistente virtuale intelligente per comprendere le analisi del sangue.**
> Progetto realizzato per il corso di *AI System Engineering* presso l'Università degli Studi di Napoli Federico II.

<p align="center">
  <img src="BloodBuddy.png" alt="BloodBuddy Logo" width="400">
</p>

BloodBuddyAI è un'applicazione web basata su un'architettura **RAG (Retrieval-Augmented Generation)** avanzata. Permette agli utenti di caricare i propri referti ematochimici, estrarne i dati automaticamente e ricevere spiegazioni chiare, empatiche e clinicamente contestualizzate grazie alla potenza dei LLM di ultima generazione.

---

## ✨ Funzionalità Principali

* 📄 **Scansione e Parsing dei Referti (OCR):** Carica immagini (JPG, PNG) o PDF. Il sistema utilizza PaddleOCR e OpenCV per estrarre e normalizzare automaticamente i valori e le unità di misura.
* 💬 **Chat Medica Intelligente:** Poni domande sui tuoi sintomi o sui tuoi esami. Il modello risponde con un tono empatico e rassicurante, agendo come un medico di base virtuale.
* 👤 **Profilo Clinico Personalizzato:** Crea un profilo con i tuoi dati (età, peso, patologie pregresse, farmaci). L'IA userà queste informazioni per contestualizzare l'analisi.
* 🧠 **Architettura RAG a doppia via:**
    * **Retrieval Clinico:** Cerca pazienti reali simili nel database NHANES (indicizzato su Elasticsearch) per fornire un supporto statistico.
    * **Retrieval Teorico:** Recupera nozioni mediche teoriche vettorializzate tramite BioBERT (su Pinecone) per garantire accuratezza scientifica.
* 🔒 **Privacy by Design:** Nessun dato, referto o chat viene salvato in modo permanente.

---

## 🛠️ Stack Tecnologico

L'applicazione è costruita con un'architettura monolitica modulare, interamente containerizzata con Docker.

* **Frontend:** [Streamlit](https://streamlit.io/)
* **LLM & Inferenza:** [LLaMA 4 Scout](https://ai.meta.com/llama/) via [Groq API](https://groq.com/) per latenze ultra-basse.
* **Vettorializzazione Semantica:** `pritamdeka/BioBERT` (tramite HuggingFace).
* **Vector Database (Teoria):** [Pinecone](https://www.pinecone.io/)
* **Search Engine (Dati Clinici):** [Elasticsearch](https://www.elastic.co/) (Eseguito in locale via Docker).
* **OCR Pipeline:** PaddleOCR, OpenCV, PIL, pdf2image.
* **Deploy:** Docker & Docker Compose.

---

## 🚀 Installazione e Avvio Rapido

### Prerequisiti
* [Docker](https://www.docker.com/) e Docker Compose installati.
* Chiave API di **Groq** e **Pinecone**.

### Passaggi

1. **Clona il repository:**
   ```bash
   git clone [https://github.com/gabman78/BloodBuddyAI.git](https://github.com/gabman78/BloodBuddyAI.git)
   cd BloodBuddyAI
