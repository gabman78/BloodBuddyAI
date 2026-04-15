#!/bin/bash

echo "🔄 Verifica della disponibilità di Elasticsearch..."

# Aspetta finché Elasticsearch non risponde
until curl -s http://elasticsearch:9200 >/dev/null; do
  echo "$(date) ⌛ Elasticsearch non è ancora disponibile, ritento tra pochi secondi..."
  sleep 2
done

echo "✅ Elasticsearch è pronto!"

# Verifica se l'indice esiste
if curl --silent --fail http://elasticsearch:9200/index1 >/dev/null; then
  COUNT=$(curl -s http://elasticsearch:9200/index1/_count | grep -o '"count":[0-9]*' | grep -o '[0-9]*')
else
  COUNT=0
fi

# Caricamento se necessario
if [ "$COUNT" = "0" ] || [ -z "$COUNT" ]; then
  echo "🚀 Caricamento iniziale del database da databaseHealth.json..."
  python load_data.py
else
  echo "ℹ️ L'indice 'index1' contiene già dati, nessun caricamento necessario."
fi

# Avvio dell'applicazione Streamlit
echo "🚀 Avvio di BloodBuddyAI..."
streamlit run app1.py --server.port=8501 --server.address=0.0.0.0
