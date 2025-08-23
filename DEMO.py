import streamlit as st
import pandas as pd

# ===== DANH SÁCH TÀI KHOẢN =====
accounts = {
    "staff": {"password": "1111", "role": "staff"},
    "admin": {"password": "1234", "role": "admin"},
}

# ===== DỮ LIỆU SẢN PHẨM =====
products = [
    {"id": 1, "name": "Áo thun", "price": 120000, "image": https://drive.google.com/file/d/1s6sJALOs2IxX5f9nqa4Tf8zut_U9KE3O/view?usp=sharing"},
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

menu = st.sidebar.radio(
    "📌 Menu",
    ["Trang chủ", "Giỏ hàng", "Thanh toán", "Đơn hàng của tôi", "Đăng nhập", "Quản lý"]
)

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
                    "Tổng tiền": total,
                    "Trạng thái": "Chờ xác nhận"
                }
                st.session_state.orders.append(order)
                st.success(f"✅ Cảm ơn {name}, đơn hàng đã được ghi nhận!")
                st.session_state.cart = []
            else:
                st.error("Vui lòng nhập đủ thông tin!")

# ===== ĐƠN HÀNG CỦA TÔI =====
elif menu == "Đơn hàng của tôi":
    st.subheader("📜 Tra cứu đơn hàng")
    phone_lookup = st.text_input("Nhập số điện thoại của bạn")

    if phone_lookup:
        my_orders = [o for o in st.session_state.orders if o["SĐT"] == phone_lookup]
        if my_orders:
            for idx, order in enumerate(my_orders):
                st.write(f"### Đơn hàng {idx+1}")
                st.write(order)

                # Cho phép hủy nếu đơn chưa xác nhận
                if order["Trạng thái"] == "Chờ xác nhận":
                    if st.button(f"❌ Hủy đơn {idx+1}", key=f"cancel_{idx}"):
                        order["Trạng thái"] = "Đã hủy"
                        st.warning(f"Đơn hàng {idx+1} đã được hủy!")
        else:
            st.warning("Không tìm thấy đơn hàng nào với số điện thoại này!")

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
            for idx, order in enumerate(st.session_state.orders):
                st.write(f"### Đơn hàng {idx+1}")
                st.write(order)

                # Nhân viên/Admin có thể cập nhật trạng thái
                if st.session_state.role in ["staff", "admin"]:
                    new_status = st.selectbox(
                        f"Trạng thái đơn {idx+1}",
                        ["Chờ xác nhận", "Đã xác nhận", "Đang giao", "Hoàn tất", "Đã hủy"],
                        index=["Chờ xác nhận", "Đã xác nhận", "Đang giao", "Hoàn tất", "Đã hủy"].index(order["Trạng thái"]),
                        key=f"status_{idx}"
                    )
                    if new_status != order["Trạng thái"]:
                        order["Trạng thái"] = new_status
                        st.success(f"✅ Đã cập nhật trạng thái đơn {idx+1} thành {new_status}")

            # Admin có quyền tải về
            if st.session_state.role == "admin":
                df = pd.DataFrame(st.session_state.orders)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Tải về danh sách đơn hàng (CSV)", data=csv,
                                   file_name="orders.csv", mime="text/csv")


