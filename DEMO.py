import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import base64

st.set_page_config(layout="wide")
st.title("🛍️ Mini Shop - Grid Layout (Fix Size)")

# Lấy dữ liệu từ Google Sheets
sheet_url = "https://docs.google.com/spreadsheets/d/1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY/export?format=csv"
df = pd.read_csv(sheet_url)
products = df.to_dict("records")

# CSS grid
html = """
<style>
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, 160px);
  gap: 20px;
  justify-content: center;
}
.product-card {
  border:1px solid #ddd;
  border-radius: 10px;
  padding: 10px;
  text-align:center;
  background: #fff;
  width: 160px;
}
.product-card img {
  width: 120px;
  height: auto;
  border-radius: 5px;
}
</style>
<div class="product-grid">
"""

# Render sản phẩm
for p in products:
    img_url = str(p.get("image", "")).strip()
    try:
        resp = requests.get(img_url, timeout=5)
        img = Image.open(BytesIO(resp.content))
        img.thumbnail((120, 120))
        buf = BytesIO(); img.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        img_html = f'<img src="data:image/png;base64,{img_b64}"/>'
    except:
        img_html = '<div style="width:120px;height:120px;background:#eee;"></div>'

    html += f"""
    <div class="product-card">
        {img_html}
        <div><b>{p.get('name','SP')}</b></div>
        <div>💰 {p.get('price','0')} đ</div>
    </div>
    """

html += "</div>"

st.html(html, height=300, scrolling=True)

