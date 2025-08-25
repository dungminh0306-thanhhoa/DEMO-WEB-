import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import re
from urllib.parse import urlparse, parse_qs

# Hàm lấy file_id từ link Google Drive
def get_file_id(link: str) -> str:
    url = urlparse(link)
    qs = parse_qs(url.query)
    if "id" in qs and qs["id"]:
        return qs["id"][0]
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url.path)
    if m:
        return m.group(1)
    return None

# Hàm tải ảnh về từ Google Drive
def load_drive_image(link: str):
    file_id = get_file_id(link)
    if not file_id:
        st.error("❌ Không tìm thấy file_id trong link Google Drive")
        return None
    direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
    try:
        response = requests.get(direct_link)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        st.error(f"⚠️ Không tải được ảnh: {e}")
        return None

# Test với link của mày
drive_link = "https://drive.google.com/file/d/1s6sJALOs2IxX5f9nqa4Tf8zut_U9KE3O/view?usp=sharing"

st.title("🖼️ Test load ảnh Google Drive (cách 3)")

img = load_drive_image(drive_link)
if img:
    st.image(img, caption="Ảnh từ Google Drive (full size)", use_column_width=True)
