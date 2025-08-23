import streamlit as st
import pandas as pd

# ===== DỮ LIỆU SẢN PHẨM =====
products = [
    {"id": 1, "name": "Áo thun", "price": 120000, "image": "https://via.placeholder.com/150"},
    {"id": 2, "name": "Quần jean", "price": 250000, "image": "https://via.placeholder.com/150"},
    {"id": 3, "name": "Áo khoác", "price": 350000, "image": "https://via.placeholder.com/150"},
]

# ===== KHỞI TẠO SESSION STATE =====
if "cart" not in st.session_state:
    st.session_state.cart = []
if "orders" not in st.session_state:
    st.session_state.orders = []  # nơi lưu các đơn hàng

# ===== HEADER =====
st.title("🛒 Cửa hàng Online Demo")

menu = st.sidebar.radio("📌 Menu", ["Trang chủ", "Giỏ hàng", "Thanh toán", "Quản lý"])

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
        total = 0
        for item in st.session_state.cart:
            st.write(f"- {item['name']} | {item['price']:,} VND")
            total += item['price']
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
                st.success(f"✅ Cảm ơn {name}, đơn hàng của bạn đã được ghi nhận!")
                st.session_state.cart = []  # Xóa giỏ sau khi đặt
            else:
                st.error("Vui lòng nhập đầy đủ thông tin trước khi đặt hàng.")

# ===== QUẢN LÝ =====
elif menu == "Quản lý":
    st.subheader("📦 Danh sách đơn hàng")
    if not st.session_state.orders:
        st.info("Chưa có đơn hàng nào.")
    else:
        df = pd.DataFrame(st.session_state.orders)
        st.dataframe(df, use_container_width=True)

        # Nút xuất ra Excel
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Tải về danh sách đơn hàng (CSV)", data=csv, file_name="orders.csv", mime="text/csv")
