import streamlit as st
import base64
from PIL import Image
import requests
from io import BytesIO
import time

# ===== Hàm xử lý ảnh Google Drive =====
def gdrive_to_direct(link):
    if "drive.google.com" in link:
        if "/file/d/" in link:
            file_id = link.split("/file/d/")[1].split("/")[0]
            return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
        elif "id=" in link:
            file_id = link.split("id=")[1]
            return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
    return link

def load_drive_image(link):
    try:
        url = gdrive_to_direct(link)
        response = requests.get(url)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except:
        return None
    return None

# ===== Dữ liệu sản phẩm mẫu =====
products = [
    {"id": 1, "name": "Áo thun", "price": 120000,
     "image": "https://drive.google.com/file/d/1s6sJALOs2IxX5f9nqa4Tf8zut_U9KE3O/view?usp=drive_link"},
    {"id": 2, "name": "Quần jean", "price": 250000,
     "image": "https://via.placeholder.com/200"},
    {"id": 3, "name": "Áo khoác", "price": 350000,
     "image": "https://via.placeholder.com/200"},
]

# ===== Session state =====
if "cart" not in st.session_state:
    st.session_state.cart = []
if "orders" not in st.session_state:
    st.session_state.orders = []
if "user_role" not in st.session_state:
    st.session_state.user_role = "guest"  # guest / customer / admin

# ===== CSS Hiệu ứng =====
st.markdown("""
<style>
    .product-card {
        background: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    .stButton>button {
        border-radius: 10px;
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #43e97b, #38f9d7);
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# ===== Menu =====
menu = st.sidebar.radio("Menu", ["Trang chủ", "Giỏ hàng", "Đơn hàng của tôi", "Admin", "Đăng nhập"])

# ===== Đăng nhập =====
if menu == "Đăng nhập":
    st.title("🔐 Đăng nhập")
    role = st.radio("Chọn vai trò:", ["Khách hàng", "Admin"])
    if st.button("Đăng nhập"):
        if role == "Khách hàng":
            st.session_state.user_role = "customer"
            st.success("Đăng nhập với vai trò Khách hàng 🎉")
            st.balloons()
        else:
            st.session_state.user_role = "admin"
            st.success("Đăng nhập với vai trò Admin 👑")
            st.snow()

# ===== Trang chủ =====
elif menu == "Trang chủ":
    st.title("🛍️ Cửa hàng online")

    for p in products:
        col1, col2 = st.columns([1, 2])
        with col1:
            img = load_drive_image(p["image"])
            if img:
                st.image(img, caption=p["name"], use_container_width=True)
            else:
                st.image(p["image"], caption=p["name"], use_container_width=True)

        with col2:
            st.markdown(f"<div class='product-card'>", unsafe_allow_html=True)
            st.subheader(p["name"])
            st.write(f"💰 Giá: {p['price']:,} VND")

            qty = st.number_input(f"Số lượng {p['name']}", min_value=1, value=1, key=f"qty_{p['id']}")

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
                st.balloons()
            st.markdown("</div>", unsafe_allow_html=True)

# ===== Giỏ hàng =====
elif menu == "Giỏ hàng":
    st.title("🛒 Giỏ hàng của bạn")

    if not st.session_state.cart:
        st.info("Giỏ hàng trống.")
    else:
        total = 0
        for i, item in enumerate(st.session_state.cart):
            st.write(f"**{item['name']}** - {item['qty']} x {item['price']:,} VND")
            total += item["qty"] * item["price"]
            if st.button(f"❌ Xóa {item['name']}", key=f"remove_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
        st.write(f"### Tổng cộng: {total:,} VND")

        if st.button("✅ Đặt hàng"):
            st.session_state.orders.append({"items": st.session_state.cart.copy(), "status": "Chờ xác nhận"})
            st.session_state.cart.clear()
            st.success("Đơn hàng đã được đặt thành công 🎉")
            st.balloons()

# ===== Đơn hàng của tôi =====
elif menu == "Đơn hàng của tôi":
    st.title("📦 Đơn hàng của tôi")
    if st.session_state.user_role != "customer":
        st.warning("Vui lòng đăng nhập với vai trò khách hàng.")
    else:
        if not st.session_state.orders:
            st.info("Bạn chưa có đơn hàng nào.")
        else:
            for i, order in enumerate(st.session_state.orders):
                st.write(f"### Đơn {i+1} - Trạng thái: {order['status']}")
                for item in order["items"]:
                    st.write(f"- {item['name']} x {item['qty']}")
                if order["status"] == "Chờ xác nhận":
                    if st.button(f"❌ Hủy đơn {i+1}", key=f"cancel_{i}"):
                        st.session_state.orders.pop(i)
                        st.warning("Đơn hàng đã bị hủy.")
                        st.rerun()

# ===== Admin =====
elif menu == "Admin":
    st.title("👑 Quản lý đơn hàng")
    if st.session_state.user_role != "admin":
        st.warning("Bạn cần đăng nhập với vai trò Admin.")
    else:
        if not st.session_state.orders:
            st.info("Chưa có đơn hàng nào.")
        else:
            for i, order in enumerate(st.session_state.orders):
                st.write(f"### Đơn {i+1} - Trạng thái: {order['status']}")
                for item in order["items"]:
                    st.write(f"- {item['name']} x {item['qty']}")
                if order["status"] == "Chờ xác nhận":
                    if st.button(f"✅ Xác nhận đơn {i+1}", key=f"confirm_{i}"):
                        order["status"] = "Đã xác nhận"
                        st.success(f"Đơn {i+1} đã được xác nhận ✅")
