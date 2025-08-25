import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import uuid

# ---------------------------
# Hàm tải ảnh từ Google Drive
# ---------------------------
def load_drive_image(url):
    if "drive.google.com" in url:
        if "/file/d/" in url:
            file_id = url.split("/file/d/")[1].split("/")[0]
        elif "id=" in url:
            file_id = url.split("id=")[1]
        else:
            return None
        direct_url = f"https://drive.google.com/uc?export=view&id={file_id}"
        try:
            response = requests.get(direct_url)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
        except:
            return None
    return None

# ---------------------------
# Dữ liệu mẫu
# ---------------------------
products = [
    {"id": 1, "name": "Áo thun", "price": 120000,
     "image": "https://via.placeholder.com/300"},
    {"id": 2, "name": "Quần jean", "price": 250000,
     "image": "https://via.placeholder.com/300"},
    {"id": 3, "name": "Áo khoác", "price": 350000,
     "image": "https://via.placeholder.com/300"},
]

# ---------------------------
# Session state
# ---------------------------
if "cart" not in st.session_state:
    st.session_state.cart = []
if "orders" not in st.session_state:
    st.session_state.orders = []
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# ---------------------------
# Menu
# ---------------------------
menu = st.sidebar.radio("📌 Menu", ["Trang chủ", "Giỏ hàng", "Đơn hàng của tôi", "Admin"])

# ---------------------------
# Trang chủ
# ---------------------------
if menu == "Trang chủ":
    st.title("🛍️ Cửa hàng online")

    for p in products:
        col1, col2 = st.columns([1, 2])
        with col1:
            img = load_drive_image(p["image"])
            if img:
                st.image(img, caption=p["name"], width=200)
            else:
                st.image(p["image"], caption=p["name"], width=200)
        with col2:
            st.subheader(p["name"])
            st.write(f"💰 Giá: {p['price']:,} VND")
            if st.button("🛒 Thêm vào giỏ", key=f"add_{p['id']}"):
                found = False
                for item in st.session_state.cart:
                    if item["id"] == p["id"]:
                        item["qty"] += 1
                        found = True
                        break
                if not found:
                    st.session_state.cart.append({**p, "qty": 1})
                st.success(f"Đã thêm {p['name']} vào giỏ hàng!")

# ---------------------------
# Giỏ hàng
# ---------------------------
elif menu == "Giỏ hàng":
    st.title("🛒 Giỏ hàng của bạn")

    if st.session_state.cart:
        total = 0
        new_cart = []

        for i, item in enumerate(st.session_state.cart):
            cols = st.columns([3, 1, 1])
            with cols[0]:
                st.write(f"{i+1}. {item['name']} - {item['price']:,} VND")
            with cols[1]:
                qty = st.number_input("Số lượng", min_value=1, value=item["qty"], key=f"qty_{i}")
                item["qty"] = qty
            with cols[2]:
                if st.button("❌ Xóa", key=f"remove_{i}"):
                    continue
            new_cart.append(item)
            total += item["price"] * item["qty"]

        st.session_state.cart = new_cart
        st.write(f"**Tổng cộng: {total:,} VND**")

        if st.button("✅ Xác nhận đặt hàng"):
            order_id = str(uuid.uuid4())[:8]
            st.session_state.orders.append({
                "id": order_id,
                "items": list(st.session_state.cart),
                "total": total,
                "status": "Chưa xác nhận"
            })
            st.session_state.cart = []
            st.success(f"Đặt hàng thành công! Mã đơn: {order_id}")
    else:
        st.info("Giỏ hàng đang trống.")

# ---------------------------
# Đơn hàng của tôi
# ---------------------------
elif menu == "Đơn hàng của tôi":
    st.title("📦 Đơn hàng của tôi")

    if st.session_state.orders:
        for order in st.session_state.orders:
            st.subheader(f"Đơn {order['id']}")
            for it in order["items"]:
                st.write(f"- {it['name']} - {it['price']:,} VND x {it['qty']}")
            st.write(f"💰 Tổng: {order['total']:,} VND")
            st.write(f"📝 Trạng thái: **{order['status']}**")

            if order["status"] == "Chưa xác nhận":
                if st.button(f"❌ Hủy đơn {order['id']}", key=f"cancel_{order['id']}"):
                    st.session_state.orders.remove(order)
                    st.warning(f"Đã hủy đơn {order['id']}")
                    st.experimental_rerun()
    else:
        st.info("Bạn chưa có đơn hàng nào.")

# ---------------------------
# Admin
# ---------------------------
elif menu == "Admin":
    st.title("🔑 Quản lý Admin")

    if not st.session_state.is_admin:
        pwd = st.text_input("Nhập mật khẩu admin:", type="password")
        if st.button("Đăng nhập"):
            if pwd == "admin123":  # đổi mật khẩu ở đây
                st.session_state.is_admin = True
                st.success("Đăng nhập thành công!")
            else:
                st.error("Sai mật khẩu.")
    else:
        st.success("Bạn đã đăng nhập với quyền admin ✅")

        if st.session_state.orders:
            for order in st.session_state.orders:
                st.subheader(f"Đơn {order['id']}")
                for it in order["items"]:
                    st.write(f"- {it['name']} - {it['price']:,} VND x {it['qty']}")
                st.write(f"💰 Tổng: {order['total']:,} VND")
                st.write(f"📝 Trạng thái: **{order['status']}**")

                if order["status"] == "Chưa xác nhận":
                    if st.button(f"✅ Xác nhận đơn {order['id']}", key=f"approve_{order['id']}"):
                        order["status"] = "Đã xác nhận"
                        st.success(f"Đơn {order['id']} đã được xác nhận!")
                        st.experimental_rerun()
        else:
            st.info("Chưa có đơn hàng nào.")

