import streamlit as st
import json
import math
from datetime import datetime
import pytz
import google.generativeai as genai

# ─────────────────────────────────────────
# CONFIGURAZIONE PAGINA
# ─────────────────────────────────────────
st.set_page_config(
    page_title="🇯🇵 Giappone Spettacularis",
    page_icon="🗾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────
# FUNZIONE GEMINI (INTEGRATA)
# ─────────────────────────────────────────
def get_gemini_response(user_prompt, my_lat=None, my_lon=None):
    """
    Motore RAG per l'Assistente Giappone Spettacularis.
    Utilizza Gemini 1.5 Pro per analizzare itinerario e documenti.
    """
    # 1. Configurazione API
    try:
        genai.configure(api_key="AIzaSyBThNr3-39nQ7fufaannZvuKet4pwg1gHM")
        model = genai.GenerativeModel("gemini-1.5-pro")
    except Exception as e:
        return f"❌ Errore Configurazione API: Controlla st.secrets. {str(e)}"

    # 2. Caricamento Contesto Locale
    try:
        with open("itinerary.json", "r", encoding="utf-8") as f:
            itinerary_json = json.load(f)
        with open("itinerary_text.txt", "r", encoding="utf-8") as f:
            manual_text = f.read()
    except Exception as e:
        return f"❌ Errore caricamento file di contesto: {str(e)}"

    # 3. Gestione Tempo di Tokyo
    tz_tokyo = pytz.timezone("Asia/Tokyo")
    now_tokyo = datetime.now(tz_tokyo)
    current_date = now_tokyo.strftime("%Y-%m-%d")
    current_time = now_tokyo.strftime("%H:%M")

    # 4. Costruzione del System Instruction (RAG)
    system_instruction = f"""
    Sei l'assistente "Giappone Spettacularis", una guida esperta con lo stile di Marco Togni: pratico, diretto e "Zero Stress".
    
    DATI DI OGGI (TOKYO):
    - Data: {current_date}
    - Ora: {current_time}
    - Posizione GPS Utente: {f"{my_lat}, {my_lon}" if my_lat else "Non disponibile"}

    CONTESTO ITINERARIO (itinerary.json):
    {json.dumps(itinerary_json, indent=2)}

    GUIDA STRATEGICA E APPUNTI (itinerary_text.txt):
    {manual_text}

    REGOLE MANDATORIE PER LA RISPOSTA:
    1. IDENTIFICA IL GIORNO: Guarda in che giorno del viaggio si trova l'utente basandoti sulla data di Tokyo.
    2. RISPOSTA DIRETTA: Sii breve. No introduzioni prolisse. Stile manuale operativo.
    3. GPS & MAPS: Per ogni luogo citato, includi coordinate e link:
       Formato: "Luogo (lat, lon) -> https://www.google.com/maps/search/?api=1&query=lat,lon"
    4. CONSIGLI PRATICI: Chiudi sempre con 1 o 2 "Trucchi Insider" (es. Suica, uscite stazioni, cibo specifico).
    5. SE NON SAI: Se l'info non è nei documenti o nell'itinerario, rispondi: "Non ho dati precisi, usa Google Maps".
    6. LINGUA: Rispondi in Italiano.
    """

    try:
        response = model.generate_content([system_instruction, user_prompt])
        return response.text
    except Exception as e:
        return f"⚠️ Errore durante la generazione: {str(e)}"

# ─────────────────────────────────────────
# CSS MOBILE-FIRST (Premium Look)
# ─────────────────────────────────────────
st.markdown("""
<style>
    /* Pulsanti grandi per tocco su Android */
    div.stLinkButton a {
        display: block;
        width: 100%;
        min-height: 55px;
        font-size: 16px;
        font-weight: bold;
        text-align: center;
        padding: 12px 10px;
        border-radius: 14px;
        background-color: #e63946;
        color: white !important;
        text-decoration: none;
    }
    /* Card attrazione */
    .card {
        background-color: #1e1e2e;
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 12px;
        border-left: 5px solid #e63946;
    }
    .card h4 { margin: 0 0 4px 0; color: #ffffff; font-size: 17px; }
    .card p  { margin: 0; color: #aaaaaa; font-size: 13px; }
    /* Badge città */
    .badge {
        display: inline-block;
        background: #e63946;
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    /* Info box */
    .info-box {
        background: #2a2a3e;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        font-size: 14px;
        color: #dddddd;
    }
    /* Titolo principale */
    h1 { font-size: 24px !important; }
    
    /* Navigazione Radio stilizzata come Tab */
    div[data-testid="stRadio"] > div {
        background-color: #2a2a3e;
        padding: 6px;
        border-radius: 15px;
        display: flex;
        justify-content: space-around;
        gap: 8px;
    }
    div[data-testid="stRadio"] label {
        color: #888888;
        font-weight: bold;
        font-size: 13px;
        cursor: pointer;
        padding: 8px 10px;
    }
    div[data-testid="stRadio"] label[data-checked="true"] {
        color: white !important;
        background: #e63946;
        border-radius: 10px;
    }
    /* Nasconde il cerchio del radio widget */
    div[data-testid="stRadio"] label div:first-child { display: none; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# FUNZIONI UTILITY
# ─────────────────────────────────────────
@st.cache_data
def load_itinerary():
    with open("itinerary.json", "r", encoding="utf-8") as f:
        return json.load(f)["itinerary"]

def haversine(lat1, lon1, lat2, lon2):
    """Distanza in km tra due coordinate GPS."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def maps_url(dest_lat, dest_lon, orig_lat=None, orig_lon=None, mode="transit"):
    """Genera il Deep Link per Google Maps."""
    base = "https://www.google.com/maps/dir/?api=1"
    dest = f"&destination={dest_lat},{dest_lon}"
    origin = f"&origin={orig_lat},{orig_lon}" if orig_lat else ""
    travel = f"&travelmode={mode}"
    return base + origin + dest + travel

def get_today_tokyo():
    """Data odierna nel fuso orario di Tokyo."""
    return datetime.now(pytz.timezone("Asia/Tokyo")).strftime("%Y-%m-%d")

def get_day_plan(itinerary, date_str):
    return next((d for d in itinerary if d["date"] == date_str), None)

def city_emoji(city):
    if "Tokyo" in city:   return "🗼"
    if "Kyoto" in city:   return "⛩️"
    if "Osaka" in city:   return "🍜"
    return "📍"


# ─────────────────────────────────────────
# CARICAMENTO DATI
# ─────────────────────────────────────────
itinerary = load_itinerary()
all_dates = [d["date"] for d in itinerary]
today_tokyo = get_today_tokyo()

in_trip = today_tokyo in all_dates
default_date = today_tokyo if in_trip else all_dates[0]

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.title("🇯🇵 Giappone Spettacularis")

if in_trip:
    st.success(f"✅ Sei in Giappone! Oggi: {today_tokyo} (Tokyo Time)")
else:
    days_to_go = (datetime.strptime(all_dates[0], "%Y-%m-%d") -
                  datetime.now(pytz.timezone("Asia/Tokyo")).replace(tzinfo=None)).days
    if days_to_go > 0:
        st.info(f"✈️ Mancano **{days_to_go} giorni** alla partenza!")
    else:
        st.warning("Il viaggio è terminato. 🌸")

# ─────────────────────────────────────────
# NAVIGAZIONE (Custom Tab-like)
# ─────────────────────────────────────────
# Usiamo chiavi semplici e format_func per evitare problemi con gli emoji
# NAVIGAZIONE (Selectbox per massima compatibilità)
tab_selection = st.selectbox(
    "Navigazione:",
    options=["📍 Oggi", "🗺️ Viaggio", "🤖 Assistente"],
    index=0
)

st.markdown("---")

# ══════════════════════════════════════════
# SEZIONE 1 - OGGI
# ══════════════════════════════════════════
if tab_selection == "📍 Oggi":
    date_labels = {d["date"]: f"{d['date']}  {city_emoji(d['city_base'])}  {d['city_base']}"
                   for d in itinerary}
    selected_date = st.selectbox(
        "📅 Giorno del viaggio:",
        options=all_dates,
        index=all_dates.index(default_date),
        format_func=lambda x: date_labels[x]
    )

    plan = get_day_plan(itinerary, selected_date)

    if plan:
        st.markdown(f'<div class="badge">{city_emoji(plan["city_base"])} {plan["city_base"]}</div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">🚆 <b>Logistica:</b> {plan["logistics"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">🍜 <b>Food focus:</b> {plan["food_focus"]}</div>', unsafe_allow_html=True)

        st.markdown("### 🎯 Attrazioni")
        
        with st.expander("📡 Posizione GPS (simulata)", expanded=False):
            col1, col2 = st.columns(2)
            my_lat = col1.number_input("Lat", value=plan["activities"][0]["lat"], format="%.4f")
            my_lon = col2.number_input("Lon", value=plan["activities"][0]["lon"], format="%.4f")

            # Salviamo in session state per l'AI
            st.session_state.my_lat = my_lat
            st.session_state.my_lon = my_lon

        for act in plan["activities"]:
            dist = haversine(my_lat, my_lon, act["lat"], act["lon"])
            st.markdown(f"""
            <div class="card">
                <h4>{act['name']}</h4>
                <p>📏 {dist:.1f} km da te</p>
            </div>
            """, unsafe_allow_html=True)
            url = maps_url(act["lat"], act["lon"], my_lat, my_lon, mode="transit")
            st.link_button(f"📍 Portami a {act['name']}", url, use_container_width=True)
            st.write("")


# ══════════════════════════════════════════
# SEZIONE 2 - TUTTO IL VIAGGIO
# ══════════════════════════════════════════
elif tab_selection == "🗺️ Viaggio":
    st.markdown("### 🗓️ Itinerario completo")
    for day in itinerary:
        emoji = city_emoji(day["city_base"])
        with st.expander(f"{emoji}  {day['date']}  —  {day['city_base']}"):
            st.markdown(f"🚆 **Logistica:** {day['logistics']}")
            st.markdown(f"🍜 **Food:** {day['food_focus']}")
            st.markdown("**Attrazioni:**")
            for act in day["activities"]:
                url = maps_url(act["lat"], act["lon"])
                st.link_button(f"📍 {act['name']}", url, use_container_width=True)


# ══════════════════════════════════════════
# SEZIONE 3 - ASSISTENTE AI
# ══════════════════════════════════════════
else:
    st.markdown("### 🤖 Chiedi all'Assistente")
    st.caption("L'AI consulta i tuoi documenti in tempo reale.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant",
             "content": "Ciao! Sono la tua guida AI. Chiedimi qualsiasi cosa sull'itinerario! 🇯🇵"}
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Es: Dove mangio stasera?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.spinner("L'assistente sta pensando..."):
            # Recupera GPS se disponibile
            lat = st.session_state.get('my_lat')
            lon = st.session_state.get('my_lon')
            reply = get_gemini_response(prompt, my_lat=lat, my_lon=lon)
        
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)
