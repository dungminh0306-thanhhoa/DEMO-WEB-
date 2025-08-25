import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# ---------------------------
# Hàm hỗ trợ
# ---------------------------
def load_drive_image(link):
    """Tải ảnh từ Google Drive link về và trả về đối tượng PIL.Image"""
    try:
        if "drive.google.com" in link:
            if "/file/d/" in link:
                file_id = link.split("/file/d/")[1].split("/")[0]
            elif "id=" in link:
                file_id = link.split("id=")[1]
            else:
                return None
            url = f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            return img
        else:
            response = requests.get(link)
            img = Image.open(BytesIO(response.content))
            return img
    except:
        return None


# ---------------------------
# Data mẫu
# ---------------------------
products = [
    {"id": 1, "name": "Áo thun", "price": 120000,
     "image": "https://drive.google.com/file/d/1s6sJALOs2IxX5f9nqa4Tf8zut_U9KE3O/view?usp=drive_link"},
    {"id": 2, "name": "Quần jean", "price": 250000,
     "image": "https://via.placeholder.com/150"},
    {"id": 3, "name": "Áo khoác", "price": 350000,
     "image": "https://via.placeholder.com/150"},
]

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# ---------------------------
# Session state
# ---------------------------
if "cart" not in st.session_state:
    st.session_state.cart = []
if "orders" not in st.session_state:
    st.session_state.orders = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False


# ---------------------------
# Sidebar menu
# ---------------------------
menu = st.sidebar.radio("Menu", ["Trang chủ", "Giỏ hàng", "Đơn hàng của tôi", "Admin"])

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

            qty = st.number_input(
                f"Số lượng {p['name']}",
                min_value=1,
                value=1,
                key=f"qty_home_{p['id']}"
            )

            if st.button("🛒 Thêm vào giỏ", key=f"add_{p['id']}"):
                found = False
                for item in st.session_state.cart:
                    if item["id"] == p["id"]:
                        item["qty"] += qty
                        found = True
                        break
                if not found:
                    st.session_state.cart.append({**p, "qty": qty})
                st.success(f"Đã thêm {qty} {p['name']} vào giỏ hàng!")

# ---------------------------
# Giỏ hàng
# ---------------------------
elif menu == "Giỏ hàng":
    st.title("🛒 Giỏ hàng của bạn")

    if not st.session_state.cart:
        st.info("Giỏ hàng đang trống.")
    else:
        total = 0
        for item in st.session_state.cart:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{item['name']}** - {item['price']:,} VND")
            with col2:
                new_qty = st.number_input("Số lượng", min_value=1,
                                          value=item["qty"], key=f"cart_qty_{item['id']}")
                item["qty"] = new_qty
            with col3:
                if st.button("❌ Xóa", key=f"remove_{item['id']}"):
                    st.session_state.cart.remove(item)
                    st.rerun()
            total += item["qty"] * item["price"]

        st.write(f"### Tổng cộng: {total:,} VND")

        if st.button("✅ Đặt hàng"):
            st.session_state.orders.append({
                "items": st.session_state.cart.copy(),
                "status": "Chờ xác nhận"
            })
            st.session_state.cart.clear()
            st.success("Đặt hàng thành công!")

# ---------------------------
# Đơn hàng của tôi
# ---------------------------
elif menu == "Đơn hàng của tôi":
    st.title("📦 Đơn hàng đã đặt")

    if not st.session_state.orders:
        st.info("Bạn chưa có đơn hàng nào.")
    else:
        for i, order in enumerate(st.session_state.orders):
            st.write(f"### Đơn hàng #{i+1} - Trạng thái: {order['status']}")
            for item in order["items"]:
                st.write(f"- {item['name']} x {item['qty']} = {item['qty']*item['price']:,} VND")

            if order["status"] == "Chờ xác nhận":
                if st.button("❌ Hủy đơn này", key=f"cancel_{i}"):
                    st.session_state.orders.pop(i)
                    st.success("Đã hủy đơn hàng.")
                    st.rerun()

# ---------------------------
# Admin
# ---------------------------
elif menu == "Admin":
    if not st.session_state.logged_in or not st.session_state.is_admin:
        st.subheader("🔐 Đăng nhập Admin")
        user = st.text_input("Tên đăng nhập")
        pw = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            if user == ADMIN_USER and pw == ADMIN_PASS:
                st.session_state.logged_in = True
                st.session_state.is_admin = True
                st.success("Đăng nhập thành công!")
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu")
    else:
        st.title("📊 Quản lý đơn hàng")
        if not st.session_state.orders:
            st.info("Chưa có đơn hàng nào.")
        else:
            for i, order in enumerate(st.session_state.orders):
                st.write(f"### Đơn hàng #{i+1} - Trạng thái: {order['status']}")
                for item in order["items"]:
                    st.write(f"- {item['name']} x {item['qty']} = {item['qty']*item['price']:,} VND")

                if order["status"] == "Chờ xác nhận":
                    if st.button("✅ Xác nhận đơn", key=f"confirm_{i}"):
                        order["status"] = "Đã xác nhận"
                        st.success(f"Đơn hàng #{i+1} đã được xác nhận!")
                        st.rerun()

        if st.button("🚪 Đăng xuất"):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.success("Đã đăng xuất.")
            st.rerun()
