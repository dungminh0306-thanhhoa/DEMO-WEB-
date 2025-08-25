import streamlit as st
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

# Hàm convert Google Drive link -> thumbnail
def gdrive_to_thumbnail(link: str, size: int = 800) -> str:
    file_id = get_file_id(link)
    if not file_id:
        return link
    return f"https://drive.google.com/thumbnail?id={file_id}&sz=w{size}"

# Hàm xử lý ảnh chung (Drive hoặc link ngoài)
def get_image_link(link: str) -> str:
    if "drive.google.com" in link:
        return gdrive_to_thumbnail(link, size=800)
    return link

# Danh sách sản phẩm
products = [
    {
        "id": 1,
        "name": "quần sịp",
        "price": 120000,
        "image": "https://drive.google.com/file/d/1s6sJALOs2IxX5f9nqa4Tf8zut_U9KE3O/view?usp=sharing",
    },
    {
        "id": 2,
        "name": "áo thun tay dài",
        "price": 250000,
        "image": "https://drive.google.com/file/d/1lMp7IgJaxx9_9X06_HEEyW7p4UEMHiTK/view?usp=sharing",
    },
    {
        "id": 3,
        "name": "Áo khoác",
        "price": 350000,
        "image": "https://drive.google.com/file/d/18_nnT8H71no1543HuhI4piutdo_Aq5WW/view?usp=drive_sharing",
    },
]

st.title("🛍️ Danh sách sản phẩm (ảnh Google Drive = thumbnail)")

for p in products:
    img_link = get_image_link(p["image"])
    st.image(img_link, caption=p["name"], width=200)
    st.write(f"💰 Giá: {p['price']:,} VND")


