import streamlit as st
import json
import math
from datetime import datetime
import pytz
import google.generativeai as genai
import geocoder  # AGGIORNATO: Geocodifica reale via IP
import os        # AGGIORNATO: Per gestione percorsi assoluti

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
# CSS CUSTOM (Mobile-First & No-Flash - AGGIORNATO)
# ─────────────────────────────────────────
st.markdown("""
<style>
    * { transition: none !important; } /* AGGIORNATO: No flash effect */
    div.stLinkButton a {
        display: block; width: 100%; min-height: 50px;
        font-size: 15px; font-weight: bold; text-align: center;
        padding: 10px; border-radius: 12px;
        background-color: #e63946; color: white !important;
        text-decoration: none;
    }
    .card {
        background-color: #1e1e2e; border-radius: 12px;
        padding: 15px; margin-bottom: 10px; border-left: 5px solid #e63946;
    }
    .card h4 { margin: 0 0 5px 0; color: white; font-size: 16px; }
    .card p { margin: 0; color: #aaa; font-size: 13px; }
    .badge { display: inline-block; background: #e63946; color: white; padding: 2px 10px; border-radius: 10px; font-size: 12px; margin-bottom: 10px; }
    .klm-badge { background: #1d3557; color: #f1faee; border: 1px solid #457b9d; } /* AGGIORNATO: Badge KLM style */
    .info-box { background: #2a2a3e; border-radius: 10px; padding: 10px; margin-bottom: 10px; font-size: 13px; color: #ddd; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# GPS REALE CON CACHE (AGGIORNATO)
# ─────────────────────────────────────────
@st.cache_data(ttl=600)
def get_user_gps():
    try:
        g = geocoder.ip('me')
        if g.ok:
            return g.latlng[0], g.latlng[1]
    except:
        pass
    return 35.6895, 139.6917  # Fallback: Tokyo Shinjuku

# ─────────────────────────────────────────
# FUNZIONE GEMINI (RAG Multi-File - AGGIORNATO)
# ─────────────────────────────────────────
@st.cache_data(ttl=300)
def get_gemini_response(user_prompt, my_lat=None, my_lon=None):
    try:
        # AGGIORNATO: API Key sicura via st.secrets
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # AGGIORNATO: Caricamento 3 file con percorsi assoluti robusti
        base_path = os.path.dirname(__file__)
        
        with open(os.path.join(base_path, "itinerary.json"), "r", encoding="utf-8") as f: 
            itinerary_json = json.load(f)
        with open(os.path.join(base_path, "itinerary_text.txt"), "r", encoding="utf-8") as f: 
            base_text = f.read()
        with open(os.path.join(base_path, "klm_compendio.txt"), "r", encoding="utf-8") as f: 
            klm_text = f.read()

        tz_tokyo = pytz.timezone("Asia/Tokyo")
        now_tokyo = datetime.now(tz_tokyo)
        
        system_instruction = f"""
        Sei l'assistente "Giappone Spettacularis", esperto Senior RAG in stile Marco Togni.
        Data Tokyo: {now_tokyo.strftime('%Y-%m-%d %H:%M')}
        Posizione GPS Utente: {f"{my_lat}, {my_lon}" if my_lat else "Ignota"}

        CONTESTO COMPLETO:
        1. Itinerario: {json.dumps(itinerary_json)}
        2. Guida Base: {base_text}
        3. KLM Compendio: {klm_text[:4000]} # Truncated for token optimization

        NUOVE REVISE REGOLE:
        - Cita SEMPRE la fonte: "Da KLM compendio:", "Da itinerario:", o "Da guida base:".
        - Per domande su VOLI, TRENI, TRASPORTI e LOGISTICA: DA' PRIORITÀ ASSOLUTA a klm_compendio.txt.
        - Includi SEMPRE coordinate GPS e Link Maps per i luoghi citati: https://www.google.com/maps/search/?api=1&query=lat,lon
        - Sii pratico, diretto e perentorio (Stile manuale operativo).
        """
        response = model.generate_content([system_instruction, user_prompt])
        return response.text
    except Exception as e:
        return f"⚠️ Errore AI: {str(e)}"

# ─────────────────────────────────────────
# UTILS & CARICAMENTO DATI
# ─────────────────────────────────────────
@st.cache_data
def load_itinerary():
    base_path = os.path.dirname(__file__)
    with open(os.path.join(base_path, "itinerary.json"), "r", encoding="utf-8") as f:
        return json.load(f)["itinerary"]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

itinerary = load_itinerary()
all_dates = [d["date"] for d in itinerary]
today_tokyo = datetime.now(pytz.timezone("Asia/Tokyo")).strftime("%Y-%m-%d")
default_date = today_tokyo if today_tokyo in all_dates else all_dates[0]

# AGGIORNATO: GPS Reale in Sidebar/Background
lat, lon = get_user_gps()
st.sidebar.metric("🗺️ GPS (IP)", f"{lat:.4f}, {lon:.4f}") # AGGIORNATO: Metric sidebar

# ─────────────────────────────────────────
# LAYOUT & NAVIGAZIONE
# ─────────────────────────────────────────
st.title("🇯🇵 Giappone Spettacularis")

tab_selection = st.selectbox(
    "Navigazione:",
    options=["📍 Oggi", "🗺️ Viaggio", "🤖 Assistente"],
    index=0,
    key="main_nav" # AGGIORNATO: Key univoca
)
st.markdown("---")

# SEZIONE 1 - OGGI
if tab_selection == "📍 Oggi":
    date_labels = {d["date"]: f"{d['date']} {d['city_base']}" for d in itinerary}
    selected_date = st.selectbox("Seleziona Giorno:", all_dates, 
                                 index=all_dates.index(default_date), 
                                 format_func=lambda x: date_labels[x],
                                 key="date_sel") # AGGIORNATO: Key univoca
    
    plan = next((d for d in itinerary if d["date"] == selected_date), None)
    if plan:
        st.markdown(f'<div class="badge">{plan["city_base"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">🚆 <b>Logistica:</b> {plan["logistics"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">🍜 <b>Food:</b> {plan["food_focus"]}</div>', unsafe_allow_html=True)
        
        with st.expander("📡 Posizione GPS"):
            c1, c2 = st.columns(2)
            u_lat = c1.number_input("Lat", value=lat, format="%.4f", key="gps_lat")
            u_lon = c2.number_input("Lon", value=lon, format="%.4f", key="gps_lon")
            st.session_state.my_lat, st.session_state.my_lon = u_lat, u_lon

        st.markdown("### 🎯 Attrazioni")
        for act in plan["activities"]:
            d = haversine(st.session_state.get('my_lat', lat), st.session_state.get('my_lon', lon), act["lat"], act["lon"])
            st.markdown(f'<div class="card"><h4>{act["name"]}</h4><p>📏 {d:.1f} km da te</p></div>', unsafe_allow_html=True)
            u = f"https://www.google.com/maps/dir/?api=1&destination={act['lat']},{act['lon']}&travelmode=transit"
            st.link_button(f"📍 Vai a {act['name']}", u, use_container_width=True)

# SEZIONE 2 - TUTTO IL VIAGGIO
elif tab_selection == "🗺️ Viaggio":
    st.markdown("### 🗓️ Itinerario Completo")
    for d in itinerary:
        with st.expander(f"🗓️ {d['date']} - {d['city_base']}", expanded=True):
            st.write(f"🚆 {d['logistics']}")
            for act in d["activities"]:
                st.caption(f"📍 {act['name']}")

# SEZIONE 3 - ASSISTENTE AI (AGGIORNATO)
else:
    st.markdown("### 🤖 Assistente AI")
    st.markdown('<div class="badge klm-badge">KLM ✅ Compendio Caricato</div>', unsafe_allow_html=True) # AGGIORNATO: KLM Badge
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Ciao! Come posso aiutarti oggi? 🇯🇵"}]

    for m in st.session_state.messages:
        curr_role = m["role"]
        with st.chat_message(curr_role):
            st.write(m["content"])

    if prompt := st.chat_input("Es: Come funzionano gli autobus a Kyoto?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.spinner("Consultando Guide & Compendio..."):
            res = get_gemini_response(prompt, st.session_state.get('my_lat', lat), st.session_state.get('my_lon', lon))
            st.session_state.messages.append({"role": "assistant", "content": res})
            with st.chat_message("assistant"):
                st.write(res)
