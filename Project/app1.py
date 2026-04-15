import os
os.environ["STREAMLIT_WATCH_FILE_SYSTEM"] = "false"

import streamlit as st
import base64
import json
import hashlib
from io import BytesIO

from PIL import Image, ImageEnhance
from markdown import markdown
from pdf2image import convert_from_bytes                                                                        # type: ignore
from streamlit_cropper import st_cropper                                                                        # type: ignore                                       
from streamlit_extras.switch_page_button import switch_page                                                     # type: ignore
from elasticsearch import Elasticsearch                                                                         # type: ignore

st.set_page_config(page_title="BloodBuddyAI", layout="centered")

from bloodbuddy_module import *
from ocr_pipeline import *



def navigate(page):
    st.session_state.page = page

def show_home_button():
    
    # Custom CSS SOLO per questo bottone
    st.markdown("""
        <style>
            .home-button > button {
                position: fixed;
                top: 30px;
                left: 30px;
                background-color: #DF7C65;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                text-align: center;
                z-index: 9999;
                transition: background-color 0.3s ease;
            }
            .home-button > button:hover {
                background-color: #a11f1f;
                cursor: pointer;
            }
        </style>
    """, unsafe_allow_html=True)

    # Questo div serve per "contenere" il bottone e applicare la classe home-button
    with st.container():
        st.markdown('<div class="home-button">', unsafe_allow_html=True)
        home_clicked = st.button("🔙 Torna alla Home", key="home_button")
        st.markdown('</div>', unsafe_allow_html=True)

    if home_clicked:
        navigate("Home")
        st.rerun()


st.markdown("""
<style>
div.stButton > button {
    background-color: #DF7C65;
    color: white;
    padding: 15px 30px;
    border-radius: 10px;
    font-weight: bold;
    font-size: 18px;
    text-align: center;
    cursor: pointer;
    transition: background-color 0.3s ease;
    border: none;
    display: inline-block;
    margin: 0 auto 20px auto;
}

div.stButton > button:hover {
    background-color: #a11f1f;
}
</style>
""", unsafe_allow_html=True)



if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "ocr_output" not in st.session_state:
    st.session_state.ocr_output = ""


# Funzione per convertire immagine in base64 (per il logo)
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        b64_data = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{b64_data}"

logo_base64 = get_base64_image("BloodBuddy.png")


if "page" not in st.session_state or st.session_state.page not in ["Home", "OCR", "Chat", "Profilo"]:
    st.session_state.page = "Home"


# Navbar elegante
st.markdown("""
    <style>
        .navbar {
            background-color: #f8f9fa;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 40px;
            position: sticky;
            top: 0;
            z-index: 999;
        }
        .navbar a {
            margin: 0 20px;
            text-decoration: none;
            font-weight: bold;
            color: #d62828;
            font-size: 18px;
        }
        .navbar a:hover {
            color: #000;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------- HOME -----------------
if st.session_state.page == "Home":

    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

            .subtitle {{
                font-family: 'Montserrat', sans-serif;
                font-size: 80px;
                color: #555;
                margin-top: 10px;
            }}

            .welcome {{
                font-family: 'Montserrat', sans-serif;
                font-size: 18px;
                font-weight: 600;
                color: #c23636;
                text-align: center;
                margin-top: 40px;
                margin-bottom: 15px;
            }}


            .description {{
                font-family: 'Montserrat', sans-serif;
                font-size: 22px;
                color: #666;
                margin-bottom: 40px;
                text-align: center;

            }}
        </style>

        <div style="text-align: center; padding: 80px 20px;">
            <img src="{logo_base64}" width="300">
            <h1 style='color: #d62828; font-size: 72px; font-family: Montserrat, sans-serif;'>BloodBuddyAI</h1>
            <p class="subtitle">Il tuo assistente medico personale per comprendere le analisi del sangue</p>
        </div>
    """, unsafe_allow_html=True)

    # ✅ Messaggio di bentornato o di login
    if "logged_user" in st.session_state:
        profiles = {}
        if os.path.exists("user_profiles.json"):
            with open("user_profiles.json", "r") as f:
                profiles = json.load(f)

        username = st.session_state.logged_user
        user_profile = profiles.get(username, {}).get("profile", {})
        nome = user_profile.get("Nome", username)

        st.markdown(f"""
            <div class="welcome">
                👋 Bentornato <b>{username}</b>!
            </div>
            <div class="description">
                Sono felice di rivederti . Seleziona un'opzione qui sotto per continuare.
            </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
            <div class="welcome">
                🚀 Effettua il login o registrati per un'esperienza migliore e personalizzata!
            </div>
            <div class="description">
                Seleziona una delle modalità qui sotto per iniziare:
            </div>
        """, unsafe_allow_html=True)


    col1, col2 = st.columns(2)

    with col1:
        if st.button("📤 Carica le tue analisi", use_container_width=True):
            navigate("OCR")
            st.rerun()
           
    with col2:
        if st.button("💬 Chat", use_container_width=True):
            navigate("Chat")
            st.rerun()
            
    # -----------Bottone per passare al profilo--------
    col1, col2, col3 = st.columns([6, 3, 6])

    with col1:
            st.markdown("""
                <style>
            div[data-testid="stButton"] > button {
                background-color: #DF7C65;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                transition: background-color 0.3s ease;
                width: 350px;
                display: block;
                margin: 0 auto; /* QUESTO centra il bottone */
                
            }
            div[data-testid="stButton"] > button:hover {
                background-color: #a11f1f;
                cursor: pointer;
            }
            </style>
        """, unsafe_allow_html=True)

    if st.button("👤 Profilo Utente"):
            st.session_state.page = "Profilo"
            st.rerun()

# ---------------- OCR -----------------
if st.session_state.page == "OCR":
    show_home_button()
    st.header("📤 Carica e analizza il referto")

    uploaded_files = st.file_uploader("Carica immagini o PDF (JPG, PNG, PDF)", accept_multiple_files=True)

    allowed_exts = [".jpg", ".jpeg", ".png", ".pdf", ".JPG", ".JPEG", ".PNG", ".PDF"]
    valid_files = []
    invalid_files = []

    if uploaded_files:
        for f in uploaded_files:
            ext = os.path.splitext(f.name)[1].lower()
            if ext in allowed_exts:
                valid_files.append(f)
            else:
                invalid_files.append(f.name)

        if invalid_files:
            st.error(f"❌ I seguenti file non sono supportati: {', '.join(invalid_files)}.\n\nPer favore carica solo file JPG, PNG o PDF.")
            st.stop()

    if valid_files:
        cropped_images = []

        for uploaded_file in valid_files:

            # Controlla se è PDF
            if uploaded_file.type == "application/pdf":
                pages = convert_from_bytes(uploaded_file.read(), dpi=300)

                for page_num, page in enumerate(pages):
                    st.markdown(f"<h3 style='text-align: center;'>📄 Pagina {page_num + 1} del PDF</h3>", unsafe_allow_html=True)

                    remove_key = f"remove_pdf_{uploaded_file.name}_{page_num}"
                    col1, col2 = st.columns([6, 2])

                    with col1:
                        cropped_img = st_cropper(
                            page,
                            realtime_update=True,
                            box_color='#d62828',
                            aspect_ratio=None,
                            key=f"cropper_pdf_{uploaded_file.name}_{page_num}"
                        )
                        st.markdown("<h3 style='text-align: center;'>✂️ Anteprima immagine ritagliata</h3>", unsafe_allow_html=True)
                        st.image(cropped_img, caption=f"✂️ Anteprima immagine ritagliata - Pagina {page_num + 1}", use_container_width=True)

                    with col2:
                        remove = st.checkbox("❌ Rimuovi questa immagine", key=remove_key)
                        if remove:
                            st.warning(f"⚠️ L'immagine **{uploaded_file.name}** è stata rimossa e non verrà analizzata.")



                    if not st.session_state.get(remove_key, False):
                        buffer = BytesIO()
                        cropped_img.save(buffer, format="JPEG")
                        buffer.seek(0)
                        cropped_images.append(buffer)

            else:
                        img = Image.open(uploaded_file)

                        st.markdown("<h3 style='text-align: center;'>📐 Ritaglia manualmente l'immagine prima dell'upload</h3>", unsafe_allow_html=True)

                        remove_key = f"remove_img_{uploaded_file.name}"
                        col1, col2 = st.columns([6, 2])

                        with col1:
                            cropped_img = st_cropper(
                                img,
                                realtime_update=True,
                                box_color='#d62828',
                                aspect_ratio=None,
                                key=f"cropper_img_{uploaded_file.name}"
                            )
                            st.markdown("<h3 style='text-align: center;'>✂️ Anteprima immagine ritagliata</h3>", unsafe_allow_html=True)
                            st.image(cropped_img, caption=f"✂️ Anteprima immagine ritagliata - {uploaded_file.name}", use_container_width=True)

                        with col2:
                            remove = st.checkbox("❌ Rimuovi questa immagine", key=remove_key)
                            if remove:
                                st.warning(f"⚠️ L'immagine **{uploaded_file.name}** è stata rimossa e non verrà analizzata.")


                        if not st.session_state.get(remove_key, False):
                            buffer = BytesIO()
                            cropped_img.convert("RGB").save(buffer, format="JPEG")
                            buffer.seek(0)
                            cropped_images.append(buffer)




        # Conferma per inviare tutte le immagini a BloodBuddy
        if st.button("✅ Conferma e invia tutte le immagini a BloodBuddy"):

            all_ocr_texts = ""

            for idx, cropped_buffer in enumerate(cropped_images):
                with st.spinner(f"📦 Preparazione immagine {idx + 1} per OCR..."):
                    
                    cropped_img = Image.open(cropped_buffer)
                    enhanced_img = enhance_image_for_ocr_pil(cropped_img)

                    buffer_enhanced = BytesIO()
                    enhanced_img.save(buffer_enhanced, format="JPEG")
                    buffer_enhanced.seek(0)

                with st.spinner(f"🔎 Esecuzione OCR immagine {idx + 1}..."):
                    ocr_raw = perform_ocr(buffer_enhanced)

                    # 👇 DEBUG IN TERMINALE
                    print("\n=== OCR RAW ===")
                    print(ocr_raw)
                    print("=== END OCR ===\n")


                with st.spinner("🧹 Normalizzazione risultati..."):
                    ocr_clean = normalize_output_units(ocr_raw)

                all_ocr_texts += f"--- Referto {idx + 1} ---\n{ocr_clean}\n\n"


            st.session_state.ocr_output = all_ocr_texts

            

            
            st.success("✅ Referto caricato correttamente!")

            navigate("Chat")
            st.rerun()


# ---------------- CHAT -----------------
if st.session_state.page == "Chat":
    show_home_button()
    st.markdown("<h3 style='text-align: center;'>🤖 BloodBuddy Chat Assistant</h3>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 📦 Carica dati del paziente una sola volta
    if "logged_user" in st.session_state:
        import json
        profiles = {}
        if os.path.exists("user_profiles.json"):
            with open("user_profiles.json", "r") as f:
                profiles = json.load(f)

        username = st.session_state.logged_user
        user_profile = profiles.get(username, {}).get("profile", {})

        paziente_info = {
            "Nome": user_profile.get("Nome", "N/D"),
            "Età": user_profile.get("Età", "N/D"),
            "Sesso": user_profile.get("Sesso", "N/D"),
            "Peso (kg)": user_profile.get("Peso (kg)", "N/D"),
            "Altezza (cm)": user_profile.get("Altezza (cm)", "N/D"),
            "Pressione sanguigna": "N/D",
            "Condizioni note": user_profile.get("Condizioni note", "N/D"),
            "Farmaci attuali": user_profile.get("Farmaci attuali", "N/D"),
            "Sintomi attuali": user_profile.get("Sintomi attuali", "N/D")
        }
    else:
        paziente_info = {
            "Nome": "Utente Anonimo",
            "Età": "N/D",
            "Sesso": "N/D",
            "Peso (kg)": "N/D",
            "Altezza (cm)": "N/D",
            "Pressione sanguigna": "N/D",
            "Condizioni note": "N/D",
            "Farmaci attuali": "N/D",
            "Sintomi attuali": "N/D"
        }

    # 📜 Container con scroll per la chat
    chat_container = st.container()

    with chat_container:
        st.markdown(
            """
            <style>
                .chat-messages {
                    max-height: 500px;
                    overflow-y: auto;
                    padding-right: 10px;
                }
            </style>
            <div class="chat-messages">
            """,
            unsafe_allow_html=True,
        )

        for ruolo, messaggio in st.session_state.chat_history:
            bubble_color = "#d0ebff" if ruolo == "Tu:" else "#f1f0f0"
            avatar = "" if ruolo == "Tu:" else f"<img src='{logo_base64}' width='30' style='margin-right: 10px; border-radius: 50%;'>"
            
            if ruolo == "Utente":
                st.markdown(f"<div style='background-color: {bubble_color}; padding: 10px; border-radius: 10px; margin-bottom: 10px;'><b>{ruolo}</b>:</div>", unsafe_allow_html=True)
                st.write(messaggio)
            else:
                st.markdown(
                    f"""
                    <div style='display: flex; align-items: flex-start; margin-bottom: 10px;'>
                        {avatar}
                        <div style='background-color: {bubble_color}; padding: 10px; border-radius: 10px; max-width: 80%;'>
                            <b>{ruolo}</b>: {messaggio}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("</div>", unsafe_allow_html=True)

    # ------------------ Bottone per analisi OCR ------------------
    if st.session_state.ocr_output:

        st.markdown("""
            <style>
            div.stForm {
                text-align: center; /* Questo centra tutto dentro al form */
            }

            div.stForm button {
                background-color: #DF7C65;
                color: white;
                padding: 15px 30px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 18px;
                text-align: center;
                cursor: pointer;
                transition: background-color 0.3s ease;
                border: none;
                display: inline-block;
                margin-bottom: 20px;
            }

            div.stForm button:hover {
                background-color: #a11f1f;
            }
            </style>
            """, unsafe_allow_html=True)
        
#######################################################################
        with st.expander("📄 Visualizza referto OCR scansionato"):
            st.text_area(
                label="Testo OCR",
                value=st.session_state.ocr_output,
                height=300,
                disabled=True
            )
#########################################################################




        # Crea il bottone usando form + submit button per avere azione
        with st.form("referto_completo_form"):
            submitted = st.form_submit_button("🧠 Chiedi un referto completo delle tue analisi", type="primary")

            if submitted:
                auto_question = "Per favore analizza in modo dettagliato il referto caricato. " \
                "Voglio che tu commenti ogni valore con un elenco puntato, indicando se è normale, alto o basso rispetto ai parametri di riferimento. " \
                "Segnala eventuali anomalie e fornisci spiegazioni chiare e rassicuranti per ogni valore, " \
                "con una spiegazione finale su possibili diagnosi e dei consigli."

                with st.spinner("Elaborazione..."):
                    ocr_data = st.session_state.get("ocr_output", "")
                    if not ocr_data.strip():
                        st.warning("⚠️ Non hai caricato nessun referto. Torna alla sezione OCR e carica un documento.")
                        risposta = "Non ho trovato nessun referto da analizzare. Per favore carica un'analisi nella sezione OCR."
                    else:
                        risposta = esegui_workflow(paziente_info, ocr_data, auto_question)


                with st.chat_message("assistant"):
                    st.markdown(f"<div style='display: flex; align-items: flex-start;'><img src='{logo_base64}' width='40' style='margin-right: 10px; border-radius: 50%;'><div style='background-color: #f1f0f0; padding: 10px; border-radius: 10px;'>{risposta}</div></div>", unsafe_allow_html=True)

                st.session_state.chat_history.append(("BloodBuddy", risposta))

        # ---- DOMANDE SPECIFICHE ----
        st.markdown("<h3 style='text-align: center;'>📜 Effettua domande più specifiche qui:</h3>", unsafe_allow_html=True)

    # ------------------ Input normale ------------------
    user_input = st.chat_input("Scrivi qui la tua domanda...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

            with st.spinner("Elaborazione..."):
                ocr_data = st.session_state.get("ocr_output", "")
                risposta = esegui_workflow(paziente_info, ocr_data, user_input)


        with st.chat_message("assistant"):
            st.markdown(f"<div style='display: flex; align-items: flex-start;'><img src='{logo_base64}' width='40' style='margin-right: 10px; border-radius: 50%;'><div style='background-color: #f1f0f0; padding: 10px; border-radius: 10px;'>{risposta}</div></div>", unsafe_allow_html=True)

        st.session_state.chat_history.append(("Utente", user_input))
        st.session_state.chat_history.append(("BloodBuddy", risposta))


# Aggiungi sfondo
def set_background(png_file):
    with open(png_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("sfondo.png")

##------------------ PROFILO -----------------
if st.session_state.page == "Profilo":
    show_home_button()
    st.header("Profilo Utente")

    PROFILE_FILE = "user_profiles.json"

    def load_profiles():
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_profiles(profiles):
        with open(PROFILE_FILE, "w") as f:
            json.dump(profiles, f, indent=2)

    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    profiles = load_profiles()

    # LOGIN o REGISTRAZIONE
    if "logged_user" not in st.session_state:
        menu = ["Login", "Registrati"]
        choice = st.selectbox("Scegli un'opzione", menu)

        st.write("")  # Spazio
        if st.session_state.get("registration_success"):
            st.success("✅ Account creato con successo! Ora effettua il login.")
            st.session_state.registration_success = False  # Reset dopo il messaggio
            choice = "Login"  # Forza l'apertura della sezione login


        if choice == "Login":
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")

                st.write("")
                st.write("")

                st.markdown("<br><br><br>", unsafe_allow_html=True)  # 👈 QUESTO SPINGE IN BASSO IL BOTTONE

                # Bottone login centrato
                col1, col2, col3 = st.columns([5, 2, 8])
                with col2:

                    st.markdown("""
                        <style>
                        div[data-testid="stButton"] > button {
                            background-color: #DF7C65;
                            color: white;
                            padding: 12px 24px;
                            border-radius: 8px;
                            font-weight: bold;
                            transition: background-color 0.3s ease;
                            width: 200px;
                            display: block;
                            margin: 0 auto;

       
                        }
                        div[data-testid="stButton"] > button:hover {
                            background-color: #a11f1f;
                            cursor: pointer;
                        }
                        </style>
                    """, unsafe_allow_html=True)

                    if st.button("🔐 Login", use_container_width=True):
                        if username in profiles and profiles[username]["password"] == hash_password(password):
                            st.session_state.logged_user = username
                            st.success(f"Benvenuto {username}!")
                            st.rerun()
                        else:
                            st.error("Username o password errati.")

        elif choice == "Registrati":
            new_username = st.text_input("Scegli un username", key="register_username")
            new_password = st.text_input("Scegli una password", type="password", key="register_password")

            st.write("")
            st.write("")

            col1, col2, col3 = st.columns([3, 2, 3])

            with col2:
                st.markdown("""
                    <style>
                    div[data-testid="stButton"] > button {
                        background-color: #DF7C65;
                        color: white;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-weight: bold;
                        transition: background-color 0.3s ease;
                        margin-top: 40px;
                    }
                    div[data-testid="stButton"] > button:hover {
                        background-color: #a11f1f;
                        cursor: pointer;
                    }
                    </style>
                """, unsafe_allow_html=True)

                if st.button("✅ Crea Account", use_container_width=True):
                    if not new_username or not new_password:
                        st.warning("Inserisci sia username che password.")
                    elif new_username in profiles:
                        st.warning("Username già registrato.")
                    else:
                        profiles[new_username] = {
                            "password": hash_password(new_password),
                            "profile": {
                                "Nome": "",
                                "Età": 0,
                                "Sesso": "",
                                "Peso (kg)": 0.0,
                                "Altezza (cm)": 0.0,
                                "Condizioni note": "",
                                "Farmaci attuali": "",
                                "Sintomi attuali": ""
                            }
                        }
                        save_profiles(profiles)
                        st.session_state.registration_success = True  # <-- SALVI IN SESSIONE
                        st.rerun()

 


        # PROFILO PERSONALE
    if "logged_user" in st.session_state:
            username = st.session_state.logged_user
            user_data = profiles[username]["profile"]

            st.subheader(f"👤  {username}")
            if st.button("🚪 Logout", use_container_width=True):
                del st.session_state.logged_user
                st.success("Sei stato disconnesso.")
                st.session_state.page = "Home"
                st.rerun()
                
            if "edit_profile" not in st.session_state:
                st.session_state.edit_profile = False

            if not st.session_state.edit_profile:
                for key, value in user_data.items():
                    st.markdown(f"**{key}:** {value if value != '' else 'N/D'}")

                st.write("")

                if st.button("✏️ Modifica info personali", use_container_width=True):
                    st.session_state.edit_profile = True
                    st.rerun()
            else:
                nome = st.text_input("Nome completo", user_data["Nome"])
                eta = st.number_input("Età", value=user_data["Età"], step=1)
                sesso = st.selectbox("Sesso", ["Maschio", "Femmina"], index=["Maschio", "Femmina"].index(user_data["Sesso"]) if user_data["Sesso"] in ["Maschio", "Femmina"] else 0)
                peso = st.number_input("Peso (kg)", value=user_data["Peso (kg)"])
                altezza = st.number_input("Altezza (cm)", value=user_data["Altezza (cm)"])
                condizioni = st.text_area("Condizioni note", user_data["Condizioni note"])
                farmaci = st.text_area("Farmaci attuali", user_data["Farmaci attuali"])
                sintomi = st.text_area("Sintomi attuali", user_data["Sintomi attuali"])

                st.write("")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Salva modifiche", use_container_width=True):
                        profiles[username]["profile"] = {
                            "Nome": nome,
                            "Età": eta,
                            "Sesso": sesso,
                            "Peso (kg)": peso,
                            "Altezza (cm)": altezza,
                            "Condizioni note": condizioni,
                            "Farmaci attuali": farmaci,
                            "Sintomi attuali": sintomi
                        }
                        save_profiles(profiles)
                        st.success("Profilo aggiornato!")
                        st.session_state.edit_profile = False
                        st.rerun()

                with col2:
                    if st.button("❌ Annulla", use_container_width=True):
                        st.session_state.edit_profile = False
                        st.rerun()
