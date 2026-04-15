import json
from elasticsearch import Elasticsearch                                                         # type: ignore                      
from elasticsearch.exceptions import BadRequestError                                            # type: ignore
import traceback

es = Elasticsearch("http://elasticsearch:9200")
index_name = "index1"

# Mapping dinamico
mappings = {
    "mappings": {
        "dynamic": True,
        "properties": {} 
    }
}

# Elimina indice se già presente
try:
    if es.indices.exists(index=index_name):
        print(f"🗑️ L'indice '{index_name}' esiste già. Lo elimino...")
        es.indices.delete(index=index_name)
except Exception as e:
    print("❌ Errore eliminando l'indice:", str(e))
    exit()

# Crea nuovo indice
try:
    print(f"🚧 Creo l'indice '{index_name}'...")
    es.indices.create(index=index_name, body=mappings)
    print(f"✅ Indice '{index_name}' creato con successo.")
except BadRequestError as e:
    print("❌ Errore 400 nella creazione dell'indice:")
    traceback.print_exc()
    print("Dettagli:", e.meta.body if hasattr(e, 'meta') else str(e))
    exit()

# Caricamento del file JSON
try:
    with open("databaseHealth.json", "r") as f:
        dati = json.load(f)
    print(f"📂 Caricati {len(dati)} record dal file JSON.")
except Exception as e:
    print(f"❌ Errore nel parsing del JSON: {e}")
    exit()

# Inserimento documenti
success = 0
for patient_id, patient_data in dati.items():
    try:
        es.index(index=index_name, id=patient_id, document=patient_data)
        success += 1
    except Exception as e:
        print(f"❌ Errore inserendo paziente {patient_id}: {e}")

print(f"✅ Inseriti {success} pazienti su {len(dati)}.")
