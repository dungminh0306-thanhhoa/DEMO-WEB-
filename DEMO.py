import streamlit as st
import pandas as pd

# ===== DANH SÁCH TÀI KHOẢN (demo) =====
# role: guest | staff | admin
accounts = {
    "staff": {"password": "1111", "role": "staff"},
    "admin": {"password": "1234", "role": "admin"},
}

# ===== DỮ LIỆU SẢN PHẨM =====
products = [
    {"id": 1, "name": "Áo thun", "price": 120000, "image": "https://via.placeholder.com/150"},
    {"id": 2, "name": "Quần jean", "price": 250000, "image": "https://via.placeholder.com/150"},
    {"id": 3, "name": "Áo khoác", "price": 350000, "image": "https://via.placeholder.com/150"},
]

# ===== SESSION STATE =====
if "cart" not in st.session_state:
    st.session_state.cart = []
if "orders" not in st.session_state:
    st.session_state.orders = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = "guest"

# ===== HEADER =====
st.title("🛒 Cửa hàng Online Demo")

menu = st.sidebar.radio("📌 Menu", ["Trang chủ", "Giỏ hàng", "Thanh toán", "Đăng nhập", "Quản lý"])

# ===== TRANG CHỦ =====
if menu == "Trang chủ":
    st.subheader("Danh sách sản phẩm")
    cols = st.columns(3)

    for idx, product in enumerate(products):
        with cols[idx % 3]:
            st.image(product["image"], use_container_width=True)
            st.write(f"**{product['name']}**")
            st.write(f"💰 Giá: {product['price']:,} VND")
            if st.button(f"Thêm {product['name']} vào giỏ", key=f"add_{product['id']}"):
                st.session_state.cart.append(product)
                st.success(f"Đã thêm {product['name']} vào giỏ hàng!")

# ===== GIỎ HÀNG =====
elif menu == "Giỏ hàng":
    st.subheader("🛒 Giỏ hàng của bạn")
    if not st.session_state.cart:
        st.info("Giỏ hàng đang trống.")
    else:
        total = sum(item['price'] for item in st.session_state.cart)
        for item in st.session_state.cart:
            st.write(f"- {item['name']} | {item['price']:,} VND")
        st.write(f"### Tổng cộng: {total:,} VND")

# ===== THANH TOÁN =====
elif menu == "Thanh toán":
    st.subheader("💳 Thông tin thanh toán")
    if not st.session_state.cart:
        st.warning("Bạn chưa có sản phẩm nào trong giỏ!")
    else:
        name = st.text_input("Họ tên")
        phone = st.text_input("Số điện thoại")
        address = st.text_area("Địa chỉ giao hàng")

        if st.button("Đặt hàng"):
            if name and phone and address:
                total = sum(item['price'] for item in st.session_state.cart)
                order = {
                    "Tên khách": name,
                    "SĐT": phone,
                    "Địa chỉ": address,
                    "Sản phẩm": ", ".join([item['name'] for item in st.session_state.cart]),
                    "Tổng tiền": total
                }
                st.session_state.orders.append(order)
                st.success(f"✅ Cảm ơn {name}, đơn hàng đã được ghi nhận!")
                st.session_state.cart = []
            else:
                st.error("Vui lòng nhập đủ thông tin!")

# ===== ĐĂNG NHẬP =====
elif menu == "Đăng nhập":
    if st.session_state.logged_in:
        st.info(f"👤 Bạn đang đăng nhập với quyền: **{st.session_state.role}**")
        if st.button("🚪 Đăng xuất"):
            st.session_state.logged_in = False
            st.session_state.role = "guest"
            st.success("Đã đăng xuất!")
    else:
        st.subheader("🔐 Đăng nhập")
        username = st.text_input("Tài khoản")
        password = st.text_input("Mật khẩu", type="password")

        if st.button("Đăng nhập"):
            if username in accounts and accounts[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.role = accounts[username]["role"]
                st.success(f"✅ Đăng nhập thành công! Quyền: {st.session_state.role}")
            else:
                st.error("Sai tài khoản hoặc mật khẩu!")

# ===== QUẢN LÝ =====
elif menu == "Quản lý":
    if not st.session_state.logged_in:
        st.warning("Bạn cần đăng nhập để truy cập chức năng quản lý!")
    else:
        st.subheader("📦 Danh sách đơn hàng")
        if not st.session_state.orders:
            st.info("Chưa có đơn hàng nào.")
        else:
            df = pd.DataFrame(st.session_state.orders)
            st.dataframe(df, use_container_width=True)

            if st.session_state.role == "admin":
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Tải về danh sách đơn hàng (CSV)", data=csv,
                                   file_name="orders.csv", mime="text/csv")
            else:
                st.info("Bạn chỉ có quyền xem, không được tải xuống.")
