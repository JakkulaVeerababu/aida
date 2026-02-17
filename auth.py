import streamlit as st
from supabase import create_client

SUPABASE_URL = "https://lrldbgepvvosnckvbniz.supabase.co"

SUPABASE_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxybGRiZ2VwdnZvc25ja3Zibml6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA5NTA3NzAsImV4cCI6MjA4NjUyNjc3MH0."
    "45edn4KGDUmMY5-gCwWlsdcCvkVd-ACMOPtM0nXoKyQ"
)

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def login_ui():
    st.title("Login")

    providers = {
        "Google": "google",
        "GitHub": "github",
        "LinkedIn": "linkedin",
        "Discord": "discord",
        "Facebook": "facebook"
    }

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


