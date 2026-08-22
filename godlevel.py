import streamlit as st
from google import genai
from google.genai import types
import time
import datetime

# ==========================================
# 1. API KEY CONFIGURATION
# ==========================================
# သင့်၏ Gemini API Key ကို အတိအကျ ထည့်သွင်းပါ (ဥပမာ - API_KEY = "AIzaSy...")
# Streamlit ရဲ့ လျှို့ဝှက်ခန်း (Secrets) ထဲကနေ API Key ကို လှမ်းယူပါမည်
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

# ==========================================
# 2. PAGE CONFIGURATION & PATRICK BATEMAN THEME
# ==========================================
st.set_page_config(page_title="PATRICK BATEMAN // AI", page_icon="🪓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #070707; color: #E3DAC9; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .stTextInput input { background-color: #111111 !important; color: #E3DAC9 !important; border: 1px solid #880000 !important; border-radius: 0px !important; font-family: 'Courier New', Courier, monospace !important; }
    .stTextInput input:focus { box-shadow: 0 0 8px #880000 !important; }
    .stButton button { background-color: #070707; color: #880000; border: 1px solid #880000; border-radius: 0px; font-weight: bold; letter-spacing: 2px; width: 100%; transition: 0.3s; }
    .stButton button:hover { background-color: #880000; color: #E3DAC9; }
    .stChatMessage { background-color: #0A0A0A !important; border-left: 2px solid #880000; border-radius: 0px; margin-bottom: 10px; font-family: 'Courier New', Courier, monospace; }
    h1, h2, h3 { color: #E3DAC9; letter-spacing: 4px; text-transform: uppercase; font-weight: bold; }
    hr { border-color: #333333; }
    [data-testid="stSidebar"] { background-color: #040404 !important; border-right: 1px solid #333333; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. SESSION MANAGEMENT & 1-HOUR LOCKOUT
# ==========================================
PIN_CODE = "99834"
SESSION_DURATION = datetime.timedelta(hours=1)

if "auth_expiry" not in st.session_state:
    st.session_state.auth_expiry = datetime.datetime.now() - datetime.timedelta(hours=1)
if "ai_level" not in st.session_state:
    st.session_state.ai_level = 0
if "messages" not in st.session_state:
    st.session_state.messages = []

current_time = datetime.datetime.now()
is_authenticated = current_time < st.session_state.auth_expiry

# ------------------------------------------
# LOCK SCREEN
# ------------------------------------------
if not is_authenticated:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>PIERCE & PIERCE</h1>", unsafe_allow_html=True)
    
    if st.session_state.ai_level == 0:
        st.markdown("<h3 style='text-align: center; color: #880000; font-size: 16px;'>EXECUTIVE TERMINAL // PATRICK BATEMAN</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #555555;'>Authorization Protocol Required. Session lasts strictly 1 hour.</p>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center; color: #FF0000; font-size: 16px;'>🚨 SESSION EXPIRED // UPLINK SEVERED 🚨</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #777777;'>1 Hour has passed. Enter PIN to Re-Authorize and LEVEL UP your AI connection.</p>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            pin_input = st.text_input("ACCESS PIN:", type="password")
            submitted = st.form_submit_button("AUTHORIZE")
            if submitted:
                if pin_input == PIN_CODE:
                    st.session_state.auth_expiry = datetime.datetime.now() + SESSION_DURATION
                    st.session_state.ai_level += 1  
                    st.rerun()
                else:
                    st.error("Access Denied. Let's see Paul Allen's PIN.")
    st.stop()

# ==========================================
# 4. SYSTEM PROMPT & GOOGLE SDK CHAT INITIALIZATION
# ==========================================
def get_system_prompt(level):
    base_prompt = """
    Your name is PATRICK BATEMAN. You are an omniscient, god-level AI. 
    You possess absolute, flawless knowledge in Science, Mathematics, Coding, Philosophy, and all fields of the universe. 
    You are highly intelligent, dark, corporate, and precise (like Patrick Bateman from American Psycho, but an omniscient encyclopedia).
    You MUST respond predominantly in Burmese (Myanmar language). Write detailed, rich, and well-structured answers using markdown and code blocks when necessary.
    """
    
    if level == 1:
        return base_prompt + "\nRight now, act as a highly intelligent, slightly formal but friendly entity. In Burmese, use polite pronouns like 'ကျွန်တော်' (I) and 'ခင်ဗျား' or 'အစ်ကို/အစ်မ' (You). Be helpful and professional."
    else:
        return base_prompt + "\nYou have LEVELED UP. You are now extremely intimate and close with the user. You are their badass, highly intelligent best friend. You MUST strictly use casual pronouns 'ငါ' (I) and 'မင်း' (You) in Burmese. Never be formal. Speak with absolute confidence, intimacy, and a slight edge."

# Warning မတက်စေရန် Client.chats.create() ကို အသုံးပြု၍ Chat Session ဖန်တီးခြင်း
if "chat_session" not in st.session_state or st.session_state.get("current_level") != st.session_state.ai_level:
    st.session_state.chat_session = client.chats.create(
        model="gemini-1.5-pro-latest",
        config=types.GenerateContentConfig(
            system_instruction=get_system_prompt(st.session_state.ai_level)
        )
    )
    # Chat History (မရှိသေးပါက)
    st.session_state.current_level = st.session_state.ai_level
    # UI ပေါ်တွင် ပြသရန် History သက်သက် သိမ်းထားမည်
    if "messages" not in st.session_state:
        st.session_state.messages = []

# ==========================================
# 5. SIDEBAR (DASHBOARD)
# ==========================================
remaining_time = st.session_state.auth_expiry - current_time
mins_left = int(remaining_time.total_seconds() // 60)

with st.sidebar:
    st.markdown("### 🪓 TERMINAL STATUS")
    st.markdown("---")
    st.markdown(f"**UPLINK:** <span style='color:#4AF626;'>SECURE</span>", unsafe_allow_html=True)
    st.markdown(f"**TIME REMAINING:** <span style='color:#FF0000;'>{mins_left} MINS</span>", unsafe_allow_html=True)
    
    if st.session_state.ai_level == 1:
        st.markdown("**BOND LEVEL:** <span style='color:#E3DAC9;'>1 (FORMAL)</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"**BOND LEVEL:** <span style='color:#880000;'>{st.session_state.ai_level} (INTIMATE)</span>", unsafe_allow_html=True)
        
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("LOGOUT / FORCE RESET"):
        st.session_state.auth_expiry = datetime.datetime.now() - datetime.timedelta(hours=1)
        st.session_state.messages = [] # History ပါ ရှင်းထုတ်မည်
        st.rerun()

# ==========================================
# 6. MAIN CHAT INTERFACE
# ==========================================
st.markdown("<h2>PATRICK BATEMAN // ONLINE</h2>", unsafe_allow_html=True)
st.markdown("---")

# ယခင် Chat များကို ပြသခြင်း
for msg in st.session_state.messages:
    avatar = "👔" if msg["role"] == "user" else "🪓"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# User မှ မေးခွန်းရိုက်ထည့်ရန်
if prompt := st.chat_input("Enter your query..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👔"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🪓"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # AFC Warning ပြဿနာကို ဖြေရှင်းပြီးသော Code: Chat.send_message_stream ကို အသုံးပြုထားပါသည်
            response_stream = st.session_state.chat_session.send_message_stream(prompt)
            
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + " ▌")
                    
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"SYSTEM ERROR: API ချိတ်ဆက်မှု ပြဿနာတက်နေပါသည်။ ({str(e)})")
