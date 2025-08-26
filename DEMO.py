import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🛍️ Mini Shop - Fixed Size")

# Lấy dữ liệu từ Google Sheets
sheet_url = "https://docs.google.com/spreadsheets/d/1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY/export?format=csv"
df = pd.read_csv(sheet_url)
products = df.to_dict("records")

# CSS ép card có size nhỏ gọn
html = """
<style>
.product-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}
.product-card {
  width: 180px;          /* 👈 mỗi sản phẩm chỉ rộng 180px */
  border:1px solid #ddd;
  border-radius: 10px;
  padding: 10px;
  text-align:center;
  background: #fff;
}
.product-card img {
  max-width: 150px;      /* 👈 ảnh nhỏ gọn cố định */
  height: auto;
  object-fit: contain;
}
</style>
<div class="product-grid">
"""

for p in products:
    img_url = str(p.get("image", "")).strip()
    html += f"""
    <div class="product-card">
        <img src="{img_url}" alt="Image"/>
        <div><b>{p.get('name','SP')}</b></div>
        <div>💰 {p.get('price','0')} đ</div>
    </div>
    """

html += "</div>"

st.markdown(html, unsafe_allow_html=True)
