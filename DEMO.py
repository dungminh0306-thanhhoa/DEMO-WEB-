import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Shop Online", layout="wide")

# ======= HÀM CHUYỂN LINK GOOGLE DRIVE THÀNH LINK THUMBNAIL =======
def gdrive_thumbnail(link: str, width: int = 400) -> str:
    if "drive.google.com" not in link:
        return link
    file_id = None
    if "/file/d/" in link:
        file_id = link.split("/file/d/")[1].split("/")[0]
    elif "id=" in link:
        file_id = link.split("id=")[1].split("&")[0]
    return f"https://drive.google.com/thumbnail?id={file_id}&sz=w{width}" if file_id else link

# ======= HÀM LOAD ẢNH VỚI KÍCH THƯỚC CỐ ĐỊNH =======
def load_image(link: str, height: int = 200):
    try:
        if not link:
            return None
        resp = requests.get(gdrive_thumbnail(link, 400), timeout=8)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))
        # resize theo chiều cao cố định
        w, h = img.size
        new_w = int((height / h) * w)
        img = img.resize((new_w, height))
        return img
    except Exception:
        return None

# ======= LOAD DATA TỪ GOOGLE SHEET =======
sheet_url = "https://docs.google.com/spreadsheets/d/1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY/gviz/tq?tqx=out:csv&sheet=Sheet1"

@st.cache_data(ttl=300)
def load_products():
    df = pd.read_csv(sheet_url)
    return df.to_dict("records")

products = load_products()

# ======= HIỂN THỊ SẢN PHẨM =======
st.title("🛍️ Cửa Hàng Online")

cols = st.columns(4)  # 4 sản phẩm mỗi hàng
for i, p in enumerate(products):
    with cols[i % 4]:
        st.markdown(
            """
            <div style="border:1px solid #ddd; border-radius:10px; padding:10px; text-align:center; margin-bottom:15px; background:#fafafa;">
            """,
            unsafe_allow_html=True
        )
        
        img = load_image(p.get("image", ""), height=200)
        if img:
            st.image(img, caption="", use_container_width=False)

        st.markdown(f"**{p.get('name', 'Không tên')}**")
        st.write(f"💰 Giá: {p.get('price', '0')} VNĐ")

        st.markdown("</div>", unsafe_allow_html=True)
