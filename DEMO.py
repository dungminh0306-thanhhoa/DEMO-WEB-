import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import pandas as pd
import datetime
import uuid
import copy

# ==============================
# Cấu hình trang
# ==============================
st.set_page_config(page_title="Mini Shop", page_icon="🛍️", layout="wide")

# ==============================
# Google Sheet config bạn đã cung cấp
# ==============================
SHEET_ID = "1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300)
def load_products():
    try:
        df = pd.read_csv(SHEET_URL)
    except Exception as e:
        st.error("Không đọc được Google Sheet. Hãy kiểm tra chia sẻ (Anyone with link → Viewer).")
        st.stop()

    # Đổi tên cột chuẩn cho code hiện tại
    df = df.rename(columns={
        "ID": "id",
        "NAME": "name",
        "PRICE": "price",
        "IMAGE": "image"
    })

    # Chuyển kiểu dữ liệu hợp lý
    df["id"] = df["id"].astype(str)
    df["name"] = df["name"].astype(str)
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0).astype(int)
    df["image"] = df["image"].astype(str).fillna("")

    return df.to_dict("records")

products = load_products()

# ==============================
# Helpers for images + cart
# ==============================
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
        url = gdrive_thumbnail(link, 800)
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return Image.open(BytesIO(r.content))
    except Exception:
        return None

def ensure_cart_schema():
    for it in st.session_state.cart:
        if "qty" not in it:
            it["qty"] = 1

def add_to_cart(product, qty: int = 1):
    ensure_cart_schema()
    for it in st.session_state.cart:
        if it["id"] == product["id"]:
            it["qty"] += qty
            return
    item = product.copy()
    item["qty"] = qty
    st.session_state.cart.append(item)

# ==============================
# Admin config
# ==============================
ADMIN_USER = "admin"
ADMIN_PASS = "123"

# ==============================
# Session state init
# ==============================
if "cart" not in st.session_state:
    st.session_state.cart = []
if "orders" not in st.session_state:
    st.session_state.orders = []
if "username" not in st.session_state:
    st.session_state.username = ""
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "new_order" not in st.session_state:
    st.session_state.new_order = False

# ==============================
# Sidebar: login, menu, ...
# ==============================
st.sidebar.markdown("## 👤 Tài khoản")

if not st.session_state.logged_in:
    with st.sidebar.expander("Đăng nhập / Đăng ký nhanh", expanded=True):
        user = st.text_input("Tên đăng nhập (để theo dõi đơn)", key="username_input")
        pwd = st.text_input("Mật khẩu", type="password", key="password_input")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Đăng nhập thường"):
                if user.strip():
                    st.session_state.logged_in = True
                    st.session_state.is_admin = False
                    st.session_state.username = user.strip()
                    st.success(f"Xin chào {st.session_state.username}!")
                    st.rerun()
                else:
                    st.warning("Vui lòng nhập tên đăng nhập.")
        with col2:
            if st.button("Đăng nhập Admin"):
                if user == ADMIN_USER and pwd == ADMIN_PASS:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.username = ADMIN_USER
                    st.success("Đăng nhập admin thành công.")
                    st.rerun()
                else:
                    st.error("Sai tài khoản / mật khẩu.")
else:
    st.sidebar.write(f"**Đang đăng nhập:** {st.session_state.username}")
    if st.sidebar.button("🚪 Đăng xuất"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.session_state.username = ""
        st.success("Đã đăng xuất.")
        st.rerun()

if st.session_state.is_admin and st.session_state.new_order:
    st.sidebar.error("🔔 Có đơn hàng mới")

menu = st.sidebar.radio(
    "Menu", 
    ["🏬 Trang chủ", "🛒 Giỏ hàng", "📦 Đơn của tôi"] + (["📋 Quản lý đơn"] if st.session_state.is_admin else [])
)

# ==============================
# Page: Trang chủ
# ==============================
if menu == "🏬 Trang chủ":
    st.title("🛍️ Mini Shop")

    ensure_cart_schema()
    cols = st.columns(2)
    for idx, p in enumerate(products):
        with cols[idx % 2]:
            img = load_image(p["image"])
            if img:
                st.image(img, caption=p["name"], use_column_width=True)
            else:
                fallback = gdrive_thumbnail(p["image"]) or "https://via.placeholder.com/600x800?text=No+Image"
                st.image(fallback, caption=p["name"], use_column_width=True)

            st.markdown(f"**{p['name']}**")
            st.write(f"💰 {p['price']:,} VND")

            qty = st.number_input(f"Số lượng ({p['name']})", min_value=1, value=1, key=f"home_qty_{p['id']}")
            if st.button("🛒 Thêm vào giỏ", key=f"add_{p['id']}"):
                add_to_cart(p, qty)
                st.success(f"Đã thêm {qty} x {p['name']} vào giỏ!")

# ==============================
# Page: Giỏ hàng
# ==============================
elif menu == "🛒 Giỏ hàng":
    st.title("🛒 Giỏ hàng của bạn")
    ensure_cart_schema()
    if not st.session_state.cart:
        st.info("Giỏ hàng đang trống.")
    else:
        total = 0
        remove_idx = []
        for i, item in enumerate(st.session_state.cart):
            c1, c2, c3, c4 = st.columns([4,2,2,1])
            with c1:
                st.write(f"**{item['name']}**")
                st.caption(f"Đơn giá: {item['price']:,} VND")
            with c2:
                new_q = st.number_input("Số lượng", min_value=1, value=item["qty"], key=f"cart_qty_{i}")
                item["qty"] = new_q
            with c3:
                st.write(f"Thành tiền: {item['price']*item['qty']:,} VND")
            with c4:
                if st.button("❌", key=f"rm_{i}"):
                    remove_idx.append(i)
            total += item["price"] * item["qty"]
        for idx in sorted(remove_idx, reverse=True):
            st.session_state.cart.pop(idx)
            st.experimental_rerun()
        st.subheader(f"✅ Tổng: {total:,} VND")
        if st.button("📦 Đặt hàng"):
            buyer = st.session_state.username or "Khách"
            order = {
                "id": str(uuid.uuid4())[:8],
                "user": buyer,
                "items": copy.deepcopy(st.session_state.cart),
                "status": "Chờ xác nhận",
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.orders.append(order)
            st.session_state.cart.clear()
            st.session_state.new_order = True
            st.success(f"Đặt hàng thành công! Mã: {order['id']}")
            st.rerun()

# ==============================
# Page: Đơn của tôi
# ==============================
elif menu == "📦 Đơn của tôi":
    st.title("📦 Đơn của tôi")
    user = st.session_state.username or "Khách"
    my = [o for o in st.session_state.orders if o["user"] == user]
    if not my:
        st.info("Bạn chưa có đơn.")
    else:
        for o in my:
            with st.expander(f"Đơn {o['id']} • {o['time']} • {o['status']}"):
                total = 0
                for it in o["items"]:
                    st.write(f"- {it['name']} x{it['qty']} = {(it['price']*it['qty']):,} VND")
                    total += it['price']*it['qty']
                st.write(f"**Tổng: {total:,} VND**")
                if o["status"] == "Chờ xác nhận":
                    if st.button(f"Hủy đơn {o['id']}", key=f"cancel_{o['id']}"):
                        o["status"] = "Đã hủy"
                        st.warning("Đã hủy.")
                        st.rerun()

# ==============================
# Page: Quản lý đơn (Admin)
# ==============================
elif menu == "📋 Quản lý đơn":
    if not st.session_state.is_admin:
        st.error("Bạn không có quyền.")
    else:
        st.title("Quản lý đơn")
        if st.session_state.new_order:
            st.info("Có đơn mới!")
            st.session_state.new_order = False
        if not st.session_state.orders:
            st.info("Chưa có đơn.")
        else:
            fs = st.multiselect
