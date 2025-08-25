import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# ==========================
# HÀM HỖ TRỢ GOOGLE DRIVE
# ==========================
def gdrive_to_direct(link, mode="thumbnail"):
    if "drive.google.com" in link:
        if "/file/d/" in link:
            file_id = link.split("/file/d/")[1].split("/")[0]
        elif "id=" in link:
            file_id = link.split("id=")[1]
        else:
            return link
        if mode == "thumbnail":
            return f"https://drive.google.com/thumbnail?id={file_id}"
        else:
            return f"https://drive.google.com/uc?id={file_id}"
    return link

def load_drive_image(link):
    try:
        url = gdrive_to_direct(link, mode="thumbnail")
        response = requests.get(url)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except:
        return None
    return None

# ==========================
# DỮ LIỆU SẢN PHẨM
# ==========================
products = [
    {"id": 1, "name": "Áo thun", "price": 120000,
     "image": "https://drive.google.com/file/d/1s6sJALOs2IxX5f9nqa4Tf8zut_U9KE3O/view?usp=drive_link"},
    {"id": 2, "name": "Quần jean", "price": 250000,
     "image": "https://via.placeholder.com/150"},
    {"id": 3, "name": "Áo khoác", "price": 350000,
     "image": "https://via.placeholder.com/150"},
]

# ==========================
# SESSION STATE
# ==========================
if "cart" not in st.session_state:
    st.session_state.cart = []
if "orders" not in st.session_state:
    st.session_state.orders = []
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ==========================
# MENU
# ==========================
menu = st.sidebar.radio("Menu", ["Trang chủ", "🛒 Giỏ hàng", "📦 Đơn hàng của tôi", "🔑 Admin"])

# ==========================
# TRANG CHỦ
# ==========================
if menu == "Trang chủ":
    st.title("🛍️ Cửa hàng online")

    # Đảm bảo giỏ hàng có qty
    for item in st.session_state.cart:
        if "qty" not in item:
            item["qty"] = 1

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
                    new_item = p.copy()
                    new_item["qty"] = qty
                    st.session_state.cart.append(new_item)
                st.success(f"Đã thêm {qty} {p['name']} vào giỏ hàng!")

# ==========================
# GIỎ HÀNG
# ==========================
elif menu == "🛒 Giỏ hàng":
    st.title("🛒 Giỏ hàng của bạn")

    if not st.session_state.cart:
        st.info("Giỏ hàng trống!")
    else:
        total = 0
        for i, item in enumerate(st.session_state.cart):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(item["name"])
            with col2:
                new_qty = st.number_input("Số lượng", min_value=1, value=item["qty"], key=f"cart_qty_{i}")
                st.session_state.cart[i]["qty"] = new_qty
                st.write(f"💰 {item['price']:,} VND")
            with col3:
                if st.button("❌ Xóa", key=f"del_{i}"):
                    st.session_state.cart.pop(i)
                    st.experimental_rerun()

            total += item["price"] * item["qty"]

        st.subheader(f"✅ Tổng: {total:,} VND")

        if st.button("📦 Xác nhận đặt hàng"):
            st.session_state.orders.append({
                "items": st.session_state.cart.copy(),
                "status": "Chờ xác nhận"
            })
            st.session_state.cart.clear()
            st.success("Đơn hàng đã được tạo thành công!")

# ==========================
# ĐƠN HÀNG CỦA KHÁCH
# ==========================
elif menu == "📦 Đơn hàng của tôi":
    st.title("📦 Đơn hàng đã đặt")

    if not st.session_state.orders:
        st.info("Bạn chưa có đơn hàng nào.")
    else:
        for i, order in enumerate(st.session_state.orders):
            st.write(f"### Đơn hàng {i+1} - Trạng thái: **{order['status']}**")
            for item in order["items"]:
                st.write(f"- {item['name']} x {item['qty']} = {item['price']*item['qty']:,} VND")

            if order["status"] == "Chờ xác nhận":
                if st.button("❌ Hủy đơn", key=f"cancel_{i}"):
                    st.session_state.orders.pop(i)
                    st.success("Đã hủy đơn hàng này.")
                    st.experimental_rerun()

# ==========================
# ADMIN
# ==========================
elif menu == "🔑 Admin":
    st.title("👨‍💼 Quản lý đơn hàng")

    if not st.session_state.admin_logged_in:
        user = st.text_input("Tài khoản")
        pwd = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            if user == "admin" and pwd == "123":
                st.session_state.admin_logged_in = True
                st.success("Đăng nhập thành công!")
            else:
                st.error("Sai tài khoản hoặc mật khẩu!")
    else:
        st.success("Bạn đã đăng nhập với quyền Admin.")

        if not st.session_state.orders:
            st.info("Chưa có đơn hàng nào.")
        else:
            for i, order in enumerate(st.session_state.orders):
                st.write(f"### Đơn hàng {i+1} - Trạng thái: **{order['status']}**")
                for item in order["items"]:
                    st.write(f"- {item['name']} x {item['qty']} = {item['price']*item['qty']:,} VND")

                if order["status"] == "Chờ xác nhận":
                    if st.button("✅ Xác nhận", key=f"confirm_{i}"):
                        st.session_state.orders[i]["status"] = "Đã xác nhận"
                        st.success(f"Đơn hàng {i+1} đã được xác nhận!")
