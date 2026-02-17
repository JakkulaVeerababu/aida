import os
import streamlit as st
from supabase import create_client

# Load Supabase configuration from environment variables to avoid embedding secrets
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

if SUPABASE_URL and SUPABASE_ANON_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
else:
    supabase = None

def login_ui():
    st.title("Login")

    providers = {
        "Google": "google",
        "GitHub": "github",
        "LinkedIn": "linkedin",
        "Discord": "discord",
        "Facebook": "facebook"
    }

    if not SUPABASE_URL:
        st.warning("SUPABASE_URL is not configured. Login links are disabled.")
        return

    for name, provider in providers.items():
        auth_url = f"{SUPABASE_URL}/auth/v1/authorize?provider={provider}"
        st.markdown(f"[Login with {name}]({auth_url})")

    st.info("After login, click Continue.")

def require_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_ui()

        if st.button("Continue"):
            st.session_state.logged_in = True
            st.rerun()


        st.stop()

def logout_ui():
    if st.sidebar.button("Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


