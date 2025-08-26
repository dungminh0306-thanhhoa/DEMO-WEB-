import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import base64

st.set_page_config(layout="wide")
st.title("🛍️ Mini Shop - Grid Layout")

# Google Sheet CSV hợp lệ
sheet_url = "https://docs.google.com/spreadsheets/d/1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY/export?format=csv"
df = pd.read_csv(sheet_url)
products = df.to_dict("records")

css_and_html = """
<style>
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
  justify-items: center;
}
.product-card {
  border:1px solid #ddd; border-radius: 8px;
  padding: 10px; text-align:center;
  max-width: 180px; background: #fafafa;
}
.product-card img {
  max-width: 150px; height: auto;
  border-radius: 5px; margin-bottom: 6px;
}
</style>
<div class="product-grid">
"""

for p in products:
    img_url = p.get("image", "")
    # base64
    img_b64 = None
    try:
        resp = requests.get(img_url, timeout=5)
        img = Image.open(BytesIO(resp.content))
        img.thumbnail((150,150))
        buf = BytesIO(); img.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        img_html = f'<img src="data:image/png;base64,{img_b64}"/>'
    except:
        img_html = '<div style="width:150px;height:150px;background:#eee;"></div>'

    css_and_html += f"""
    <div class="product-card">
      {img_html}
      <b>{p.get('name','SP')}</b><br>
      Giá: {p.get('price',0):,} đ
    </div>
    """

css_and_html += "</div>"

st.markdown(css_and_html, unsafe_allow_html=True)
