import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests
from PIL import Image
from io import BytesIO
import base64

# ==== KẾT NỐI GOOGLE SHEETS ====
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# thay file service account JSON của bạn
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
client = gspread.authorize(creds)

# link sheet bạn đưa
SHEET_URL = "https://docs.google.com/spreadsheets/d/1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY/edit?usp=sharing"
spreadsheet = client.open_by_url(SHEET_URL)
worksheet = spreadsheet.sheet1
data = worksheet.get_all_records()

# ==== HÀM HỖ TRỢ ====
def convert_drive_link(url):
    """Chuyển link Google Drive về direct link"""
    if "drive.google.com" in url and "/d/" in url:
        file_id = url.split("/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?id={file_id}"
    return url

def load_image_base64(url):
    """Lấy ảnh từ link và chuyển thành base64"""
    try:
        url = convert_drive_link(url)
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img.thumbnail((150, 150))  # resize ảnh nhỏ lại
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        return None

# ==== GIAO DIỆN ====
st.set_page_config(layout="wide")
st.title("🛍️ Danh sách sản phẩm")

# CSS Grid layout
st.markdown(
    """
    <style>
    .product-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        justify-items: center;
    }
    .product-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 10px;
        background: #fafafa;
        text-align: center;
        max-width: 200px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    .product-card img {
        max-width: 150px;
        height: auto;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    </style>
    <div class="product-grid">
    """,
    unsafe_allow_html=True
)

# render từng sản phẩm
for p in data:
    img_b64 = load_image_base64(p.get("image", ""))
    if img_b64:
        img_html = f'<img src="data:image/png;base64,{img_b64}" />'
    else:
        img_html = '<div style="width:150px;height:150px;background:#eee;line-height:150px;">No Image</div>'

    st.markdown(
        f"""
        <div class="product-card">
            {img_html}
            <b>{p.get('name','Không tên')}</b><br>
            💰 Giá: {p.get('price','0')} VNĐ
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)
