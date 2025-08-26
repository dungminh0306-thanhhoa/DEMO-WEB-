import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🛍️ Mini Shop - Fixed Image Size")

# Lấy dữ liệu từ Google Sheets
sheet_url = "https://docs.google.com/spreadsheets/d/1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY/export?format=csv"
df = pd.read_csv(sheet_url)
products = df.to_dict("records")

# CSS grid layout
html = """
<style>
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
  justify-content: center;
}
.product-card {
  border:1px solid #ddd;
  border-radius: 10px;
  padding: 10px;
  text-align:center;
  background: #fff;
}
.product-card img {
  width: 150px;   /* 👈 ảnh luôn cố định 150px */
  height: auto;
  object-fit: contain;
}
</style>
<div class="product-grid">
"""

# Render sản phẩm
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
