import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.title("✅ Test gspread trên Cloud")

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPE)
client = gspread.authorize(creds)

st.success("🎉 Import gspread thành công!")
