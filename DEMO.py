import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import datetime, uuid, copy

st.set_page_config(page_title="Mini Shop", page_icon="🛍️", layout="wide")

# Google Sheet của bạn
SHEET_ID = "1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# Đọc dữ liệu từ Google Sheet (không có header -> tự gán)
@st.cache_data(ttl=300)
def load_products():
    try:
        df = pd.read_csv(SHEET_URL, header=None, names=["id","name","price","image"])
    except Exception:
        st.error("❌ Không thể đọc Google Sheet. Kiểm tra quyền chia sẻ.")
        st.stop()

    # Làm sạch dữ liệu
    df["id"] = df["id"].astype(str).str.strip()
    df["name"] = df["name"].astype(str).str.strip()
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0).astype(int)
    df["image"] = df["image"].astype(str).fillna("").str.strip()

    return df.to_dict("records")

products = load_products()

# --- Hỗ trợ ảnh Google Drive ---
def gdrive_thumbnail(link: str, width: int = 800) -> str:
    if "drive.google.com" not in link:
        return link
    file_id = None
    if "/file/d/" in link:
        file_id = link.split("/file/d/")[1].split("/")[0]
    elif "id=" in link:
        file_id = link.split("id=")[1].split("&")[0]
    return f"https://drive.google.com/thumbnail?id={file_id}&sz=w{width}" if file_id else link

def load_image(link: str):
    try:
        if not link:
            return None
        resp = requests.get(gdrive_thumbnail(link, 800), timeout=8)
        resp.raise_for_status()
        return Image.open(BytesIO(resp.content))
    except Exception:
        return None

# --- Quản lý giỏ hàng và đơn hàng ---
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "orders" not in st.session_state:
    st.session_state.orders = []

def add_to_cart(product):
    pid = product["id"]
    if pid in st.session_state.cart:
        st.session_state.cart[pid]["qty"] += 1
    else:
        st.session_state.cart[pid] = copy.deepcopy(product)
        st.session_state.cart[pid]["qty"] = 1

def clear_cart():
    st.session_state.cart = {}

# --- Giao diện ---
st.title("🛒 Mini Shop")

menu = st.sidebar.radio("📌 Menu", ["Sản phẩm", "Giỏ hàng", "Đơn hàng"])

if menu == "Sản phẩm":
    cols = st.columns(3)
    for idx, p in enumerate(products):
        with cols[idx % 3]:
            st.subheader(p["name"])
            img = load_image(p["image"])
            if img:
                st.image(img, use_container_width=True)
            st.write(f"💲 Giá: {p['price']:,} đ")
            if st.button(f"🛒 Thêm {p['id']}", key=f"add_{p['id']}"):
                add_to_cart(p)
                st.success(f"✅ Đã thêm {p['name']} vào giỏ")

elif menu == "Giỏ hàng":
    st.header("🛍️ Giỏ hàng")
    if not st.session_state.cart:
        st.info("Giỏ hàng trống.")
    else:
        total = 0
        for pid, item in st.session_state.cart.items():
            st.write(f"**{item['name']}** x{item['qty']} — {item['price']:,} đ")
            total += item["price"] * item["qty"]
        st.write(f"### Tổng cộng: {total:,} đ")

        if st.button("🧾 Thanh toán"):
            order_id = str(uuid.uuid4())[:8]
            order = {
                "id": order_id,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "items": copy.deepcopy(st.session_state.cart),
                "total": total
            }
            st.session_state.orders.append(order)
            clear_cart()
            st.success(f"🎉 Thanh toán thành công! Mã đơn: {order_id}")

elif menu == "Đơn hàng":
    st.header("📜 Lịch sử đơn hàng")
    if not st.session_state.orders:
        st.info("Chưa có đơn hàng nào.")
    else:
        for order in st.session_state.orders:
            st.write(f"### Đơn {order['id']} ({order['time']}) — {order['total']:,} đ")
            for pid, item in order["items"].items():
                st.write(f"- {item['name']} x{item['qty']} — {item['price']:,} đ")
