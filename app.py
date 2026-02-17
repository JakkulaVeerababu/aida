import streamlit as st
import pandas as pd
import numpy as np
import json
import xmltodict
import os
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from sklearn.ensemble import IsolationForest
from gradio_client import Client
from PIL import Image
import streamlit as st
from auth import require_login, logout_ui

st.set_page_config(
    page_title="AI Universal Data Analysis System",
    layout="wide"
)

require_login()

st.sidebar.title("Account")
logout_ui()

st.title("AI Universal Data Analysis System")
st.write("You are logged in. Full access enabled.")


# ================= OPENROUTER CONFIG =================
# Load API keys from environment variables to avoid embedding secrets in source.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "PUT_YOUR_OPENROUTER_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")

# ================= STACKNET CONFIG =================
STACKNET_API_KEY = "PUT_YOUR_STACKNET_KEY_HERE"
stacknet_client = Client("stacknet/stacknet-1-1-preview-demo")

# ================= HUGGING FACE CONFIG =================
# Use environment variable for Hugging Face API key
HF_API_KEY = os.getenv("HF_API_KEY", None)
HF_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "stabilityai/stable-diffusion-2-1")

# ================= OPENROUTER CALL =================
def ask_openrouter(prompt):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=60
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI Error: {e}"

# ================= STACKNET IMAGE =================
def generate_image_stacknet(prompt):
    try:
        result = stacknet_client.predict(
            prompt=prompt,
            format_type="image",
            api_key=STACKNET_API_KEY,
            api_name="/generate_image"
        )
        if result and isinstance(result, list) and result[0]:
            return result[0].get("path")
        return None
    except:
        return None

# ================= HUGGING FACE IMAGE (FIXED) =================
def generate_image_huggingface(prompt):
    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}",
            headers={
                "Authorization": f"Bearer {HF_API_KEY}",
                "Content-Type": "application/json"
            },
            json={"inputs": prompt},
            timeout=180
        )

        # Hugging Face often returns JSON while loading model
        if not response.headers.get("content-type", "").startswith("image"):
            return None

        image_path = "hf_generated_image.png"
        with open(image_path, "wb") as f:
            f.write(response.content)

        return image_path

    except:
        return None

# ================= PAGE CONFIG =================
st.set_page_config(page_title="AI Universal Data Analysis System", layout="wide")
st.title("AI Universal Data Analysis System")
st.write("Upload data, chat with AI, analyze datasets, and generate AI images.")

# ================= FILE LOADER =================
def load_data(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file)
    elif ext == ".json":
        return pd.json_normalize(json.load(file))
    elif ext == ".xml":
        return pd.json_normalize(xmltodict.parse(file.read()))
    else:
        raise ValueError("Unsupported file format")

# ================= MYSQL LOADER =================
def load_data_from_mysql():
    # Build the connection string from environment variables to avoid storing passwords in code
    mysql_user = os.getenv("MYSQL_USER", "root")
    mysql_password = os.getenv("MYSQL_PASSWORD", "")
    mysql_host = os.getenv("MYSQL_HOST", "localhost")
    mysql_db = os.getenv("MYSQL_DB", "ai_data_db")
    conn_str = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"
    engine = create_engine(conn_str)
    return pd.read_sql("SELECT * FROM expenses", engine)

# ================= CLEAN DATA =================
def clean_data(df):
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    return df.drop_duplicates()

# ================= SIDEBAR =================
st.sidebar.header("Controls")
mode = st.sidebar.radio(
    "Choose mode",
    ["General AI Chat", "Data Analysis", "AI Media Generator"]
)

# ================= GENERAL AI CHAT =================
if mode == "General AI Chat":
    st.subheader("General AI Chat")
    user_input = st.text_input("Ask anything")

    if user_input:
        answer = ask_openrouter(user_input)
        st.write(answer)

# ================= DATA ANALYSIS =================
if mode == "Data Analysis":
    source = st.sidebar.radio(
        "Data source",
        ["Upload File", "Load from MySQL"]
    )

    uploaded_file = None
    if source == "Upload File":
        uploaded_file = st.sidebar.file_uploader(
            "Upload CSV / Excel / JSON / XML",
            type=["csv", "xlsx", "xls", "json", "xml"]
        )

    if source == "Load from MySQL" or uploaded_file:
        try:
            if source == "Load from MySQL":
                df = load_data_from_mysql()
            else:
                df = clean_data(load_data(uploaded_file))

            st.subheader("Data Preview")
            st.dataframe(df.head())

            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

            st.subheader("Histogram")
            if numeric_cols:
                col = st.selectbox("Select numeric column", numeric_cols)
                fig, ax = plt.subplots()
                sns.histplot(df[col], kde=True, ax=ax)
                st.pyplot(fig)

            st.subheader("Anomaly Detection")
            if numeric_cols and st.button("Detect Anomalies"):
                iso = IsolationForest(contamination=0.05, random_state=42)
                df["Anomaly"] = iso.fit_predict(df[numeric_cols])
                anomalies = df[df["Anomaly"] == -1]
                st.write("Anomalies found:", len(anomalies))
                st.dataframe(anomalies)

            st.subheader("AI Analyst")
            question = st.text_input("Ask anything about this data")

            if question:
                prompt = f"""
Columns:
{list(df.columns)}

Statistics:
{df.describe(include='all').fillna('').to_string()}

Sample data:
{df.head(10).to_string()}

Question:
{question}
"""
                answer = ask_openrouter(prompt)
                st.write(answer)

        except Exception as e:
            st.error("Error processing data")
            st.exception(e)

# ================= AI MEDIA GENERATOR =================
if mode == "AI Media Generator":
    st.subheader("AI Image Generator")
    prompt = st.text_input("Describe the image you want")

    if st.button("Generate Image"):
        if prompt.strip():
            with st.spinner("Generating image..."):
                image_path = generate_image_stacknet(prompt)

                if image_path is None:
                    st.info("Primary engine failed. Trying fallback.")
                    image_path = generate_image_huggingface(prompt)

            if image_path:
                image = Image.open(image_path)
                st.image(image, use_column_width=True)

                with open(image_path, "rb") as f:
                    st.download_button(
                        "Download Image",
                        f,
                        file_name="generated_image.png"
                    )
            else:
                st.error("Image generation failed from all providers")
        else:
            st.warning("Enter a prompt")
