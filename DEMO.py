import streamlit as st

# =========================
# Hàm tiện ích
# =========================
def gdrive_to_direct(link):
    """Chuyển link Google Drive thành link ảnh trực tiếp"""
    if "drive.google.com" in link and "/file/d/" in link:
        file_id = link.split("/file/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    return link

# =========================
# Dữ liệu mẫu
# =========================
products = [
    {"id": 1, "name": "Áo thun", "price": 120000,
     "image": "https://drive.google.com/file/d/1s6sJALOs2IxX5f9nqa4Tf8zut_U9KE3O/view?usp=sharing"},
    {"id": 2, "name": "Quần jean", "price": 250000,
     "image": "https://via.placeholder.com/150"},
    {"id": 3, "name": "Áo khoác", "price": 350000,
     "image": "https://via.placeholder.com/150"},
]

# =========================
# State lưu trữ
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = {}

if "orders" not in st.session_state:
    st.session_state.orders = []

if "user" not in st.session_state:
    st.session_state.user = "guest"  # guest hoặc admin

# =========================
# Giao diện
# =========================
st.title("🛒 Cửa hàng Online")

menu = st.sidebar.radio("Chức năng", ["Mua sắm", "Giỏ hàng", "Đơn hàng của tôi", "Quản lý"])

# =========================
# MUA SẮM
# =========================
if menu == "Mua sắm":
    st.header("Sản phẩm")
    for p in products:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(gdrive_to_direct(p["image"]), width=150)
        with col2:
            st.write(f"**{p['name']}** - {p['price']:,} VND")
            qty = st.number_input(f"Số lượng {p['name']}", min_value=1, value=1, key=f"qty_{p['id']}")
            if st.button(f"🛍️ Thêm {p['name']} vào giỏ", key=f"add_{p['id']}"):
                if p["id"] in st.session_state.cart:
                    st.session_state.cart[p["id"]]["qty"] += qty
                else:
                    st.session_state.cart[p["id"]] = {"product": p, "qty": qty}
                st.success(f"Đã thêm {qty} {p['name']} vào giỏ hàng!")

# =========================
# GIỎ HÀNG
# =========================
elif menu == "Giỏ hàng":
    st.header("🛒 Giỏ hàng")
    if not st.session_state.cart:
        st.info("Giỏ hàng trống.")
    else:
        total = 0
        for pid, item in st.session_state.cart.items():
            p = item["product"]
            qty = st.number_input(f"{p['name']}", min_value=1, value=item["qty"], key=f"cart_qty_{pid}")
            st.session_state.cart[pid]["qty"] = qty
            st.write(f"Giá: {p['price']:,} VND | Thành tiền: {p['price'] * qty:,} VND")
            total += p["price"] * qty

        st.write(f"### Tổng cộng: {total:,} VND")

        if st.button("✅ Đặt hàng"):
            st.session_state.orders.append({
                "items": st.session_state.cart.copy(),
                "status": "Chờ xác nhận"
            })
            st.session_state.cart.clear()
            st.success("Đã đặt hàng thành công!")

# =========================
# ĐƠN HÀNG KHÁCH
# =========================
elif menu == "Đơn hàng của tôi":
    st.header("📦 Đơn hàng của tôi")
    if not st.session_state.orders:
        st.info("Bạn chưa có đơn hàng nào.")
    else:
        for i, order in enumerate(st.session_state.orders):
            st.write(f"### Đơn hàng #{i+1} - Trạng thái: {order['status']}")
            for pid, item in order["items"].items():
                p = item["product"]
                st.write(f"- {p['name']} x {item['qty']} ({p['price']:,} VND)")

            if order["status"] == "Chờ xác nhận":
                if st.button(f"❌ Huỷ đơn #{i+1}", key=f"cancel_{i}"):
                    st.session_state.orders[i]["status"] = "Đã huỷ"
                    st.warning(f"Bạn đã huỷ đơn #{i+1}")

# =========================
# QUẢN LÝ
# =========================
elif menu == "Quản lý":
    st.header("👨‍💼 Quản lý cửa hàng")

    if st.session_state.user != "admin":
        with st.form("login_form"):
            username = st.text_input("Tài khoản")
            password = st.text_input("Mật khẩu", type="password")
            login_btn = st.form_submit_button("Đăng nhập")
            if login_btn:
                if username == "admin" and password == "123":
                    st.session_state.user = "admin"
                    st.success("Đăng nhập thành công!")
                else:
                    st.error("Sai tài khoản hoặc mật khẩu.")
    else:
        st.success("Bạn đang đăng nhập với quyền quản lý.")
        if not st.session_state.orders:
            st.info("Chưa có đơn hàng nào.")
        else:
            for i, order in enumerate(st.session_state.orders):
                st.write(f"### Đơn hàng #{i+1} - Trạng thái: {order['status']}")
                for pid, item in order["items"].items():
                    p = item["product"]
                    st.write(f"- {p['name']} x {item['qty']} ({p['price']:,} VND)")

                if order["status"] == "Chờ xác nhận":
                    if st.button(f"✅ Xác nhận đơn #{i+1}", key=f"confirm_{i}"):
                        st.session_state.orders[i]["status"] = "Đã xác nhận"
                        st.success(f"Đơn #{i+1} đã được xác nhận")
                    if st.button(f"❌ Từ chối đơn #{i+1}", key=f"reject_{i}"):
                        st.session_state.orders[i]["status"] = "Bị từ chối"
                        st.warning(f"Đơn #{i+1} đã bị từ chối")
