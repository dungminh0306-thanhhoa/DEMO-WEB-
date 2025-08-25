import streamlit as st
import re
from urllib.parse import urlparse, parse_qs

def gdrive_to_direct(link: str) -> str:
    url = urlparse(link)
    qs = parse_qs(url.query)
    file_id = None

    if "id" in qs and qs["id"]:
        file_id = qs["id"][0]
    else:
        m = re.search(r"/d/([a-zA-Z0-9_-]+)", url.path)
        if m:
            file_id = m.group(1)

    if not file_id:
        return link

    # Link full size (gốc)
    return f"https://drive.google.com/uc?export=download&id={file_id}"

drive_link = "https://drive.google.com/file/d/1s6sJALOs2IxX5f9nqa4Tf8zut_U9KE3O/view?usp=sharing"

st.title("🖼️ Test 1 ảnh Google Drive (full size)")
direct_link = gdrive_to_direct(drive_link)

st.write("🔗 Link gốc:", drive_link)
st.write("➡️ Link convert:", direct_link)
st.image(direct_link, caption="Ảnh từ Google Drive (full size)", width=400)
