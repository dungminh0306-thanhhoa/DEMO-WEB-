import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.title("🔎 Test gspread + Google Sheet")

# Scope cần thiết
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Lấy credentials từ secrets
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPE)
client = gspread.authorize(creds)

# Google Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY/edit?usp=sharing"

try:
    sheet = client.open_by_url(SHEET_URL).sheet1
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    st.success("✅ Đọc Google Sheet thành công!")
    st.dataframe(df.head(100))  # hiện 5 dòng đầu
except Exception as e:
    st.error(f"❌ Lỗi khi đọc Google Sheet: {e}")

