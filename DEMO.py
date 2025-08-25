import streamlit as st
import re
from urllib.parse import urlparse, parse_qs
import uuid

# -----------------------
# HÀM XỬ LÝ GOOGLE DRIVE
# -----------------------
def get_file_id(link: str) -> str:
    url = urlparse(link)
    qs = parse_qs(url.query)
    if "id" in qs and qs["id"]:
        return qs["id"][0]
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url.path)
    if m:
        return m.group(1)
    return None

def gdrive_to_thumbnail(link: str, size: int = 800) -> str:
    file_id = get_file_id(link)
    if not file_id:
        return link
    return f"https://drive.google.com/thumbnail?id={file_id}&sz=w{size}"

def get_image_link(link: str) -> str:
    if "drive.google.com" in link:
        return gdrive_to_thumbnail(link, size=800)
    return link

# -----------------------
# DỮ LIỆU SẢN PHẨM
# -----------------------
products = [
    {"id": 1, "name": "Áo thun", "price": 120000,
     "image": "https://drive.google.com/file/d/1s6sJALOs2IxX5f9nqa4Tf8zut_U9KE3O/view?usp=sharing"},
    {"id": 2, "name": "Quần jean", "price": 250000,
     "image": "https://via.placeholder.com/200"},
    {"id": 3, "name": "Áo khoác", "price": 350000,
     "image": "https://via.placeholder.com/200"},
]

# -----------------------
# SESSION STATE
# -----------------------
if "cart" not in st.session_state:
    st.session_state.cart = []
if "orders" not in st.session_state:
    st.session_state.orders = []
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# -----------------------
# GIAO DIỆN ĐĂNG NHẬP
# -----------------------
menu = st.sidebar.radio("Menu", ["Trang chủ", "Giỏ hàng", "Đơn hàng của tôi", "Admin"])

# -----------------------
# TRANG CHỦ: KHÁCH HÀNG XEM SẢN PHẨM
# -----------------------
if menu == "Trang chủ":
    st.title("🛍️ Danh sách sản phẩm")

    for p in products:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(get_image_link(p["image"]), width=150)
        with col2:
            st.subheader(p["name"])
            st.write(f"💰 Giá: {p['price']:,} VND")
            if st.button(f"🛒 Thêm vào giỏ", key=f"add_{p['id']}"):
                st.session_state.cart.append(p)

# -----------------------
# GIỎ HÀNG
# -----------------------
elif menu == "Giỏ hàng":
    st.title("🛒 Giỏ hàng của bạn")

    if st.session_state.cart:
        total = 0
        for i, item in enumerate(st.session_state.cart):
            st.write(f"{i+1}. {item['name']} - {item['price']:,} VND")
            total += item["price"]

        st.write(f"**Tổng cộng: {total:,} VND**")
        if st.button("✅ Đặt hàng"):
            order_id = str(uuid.uuid4())[:8]
            st.session_state.orders.append({
                "id": order_id,
                "items": list(st.session_state.cart),
                "status": "Chưa xác nhận"
            })
            st.session_state.cart = []
            st.success(f"Đặt hàng thành công! Mã đơn: {order_id}")
    else:
        st.info("Giỏ hàng đang trống.")

# -----------------------
# KHÁCH HÀNG XEM ĐƠN HÀNG
# -----------------------
elif menu == "Đơn hàng của tôi":
    st.title("📦 Đơn hàng của tôi")

    if st.session_state.orders:
        for order in st.session_state.orders:
            st.subheader(f"Đơn {order['id']}")
            for it in order["items"]:
                st.write(f"- {it['name']} - {it['price']:,} VND")
            st.write(f"📝 Trạng thái: **{order['status']}**")

            if order["status"] == "Chưa xác nhận":
                if st.button(f"❌ Hủy đơn {order['id']}", key=f"cancel_{order['id']}"):
                    st.session_state.orders.remove(order)
                    st.warning(f"Đơn {order['id']} đã bị hủy.")
    else:
        st.info("Bạn chưa có đơn hàng nào.")

# -----------------------
# ADMIN
# -----------------------
elif menu == "Admin":
    if not st.session_state.is_admin:
        st.subheader("🔑 Đăng nhập Admin")
        pwd = st.text_input("Nhập mật khẩu:", type="password")
        if st.button("Đăng nhập"):
            if pwd == "admin123":  # đổi mật khẩu ở đây
                st.session_state.is_admin = True
                st.success("Đăng nhập thành công!")
            else:
                st.error("Sai mật khẩu!")
    else:
        st.title("📋 Quản lý đơn hàng")

        if st.session_state.orders:
            for order in st.session_state.orders:
                st.subheader(f"Đơn {order['id']}")
                for it in order["items"]:
                    st.write(f"- {it['name']} - {it['price']:,} VND")
                st.write(f"📝 Trạng thái: **{order['status']}**")

                if order["status"] == "Chưa xác nhận":
                    if st.button(f"✅ Xác nhận {order['id']}", key=f"confirm_{order['id']}"):
                        order["status"] = "Đã xác nhận"
                        st.success(f"Đơn {order['id']} đã được xác nhận.")
                    if st.button(f"❌ Hủy {order['id']}", key=f"reject_{order['id']}"):
                        st.session_state.orders.remove(order)
                        st.error(f"Đơn {order['id']} đã bị hủy.")
        else:
            st.info("Chưa có đơn hàng nào.")
