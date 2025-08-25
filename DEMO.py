import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import datetime

# ==============================
# Hàm xử lý ảnh Google Drive
# ==============================
def gdrive_to_direct(link, size="s600"):
    if "drive.google.com" in link:
        if "/file/d/" in link:
            file_id = link.split("/file/d/")[1].split("/")[0]
        elif "id=" in link:
            file_id = link.split("id=")[1]
        else:
            return link
        return f"https://drive.google.com/thumbnail?id={file_id}&{size}"
    return link

def load_drive_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except:
        return None
    return None

# ==============================
# Dữ liệu test
# ==============================
products = [
    {"id": 1, "name": "Áo thun", "price": 120000,
     "image": "https://drive.google.com/file/d/1s6sJALOs2IxX5f9nqa4Tf8zut_U9KE3O/view?usp=drive_link"},
    {"id": 2, "name": "Quần jean", "price": 250000,
     "image": "https://via.placeholder.com/200"},
    {"id": 3, "name": "Áo khoác", "price": 350000,
     "image": "https://via.placeholder.com/200"},
]

# ==============================
# Khởi tạo session
# ==============================
if "cart" not in st.session_state:
    st.session_state.cart = []
if "orders" not in st.session_state:
    st.session_state.orders = []   # tất cả đơn
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "new_order" not in st.session_state:
    st.session_state.new_order = False

# ==============================
# Login
# ==============================
menu = st.sidebar.radio("Menu", ["Trang chủ", "🛒 Giỏ hàng", "📦 Đơn hàng của tôi", "🔑 Đăng nhập"])

if st.session_state.is_admin:
    menu = st.sidebar.radio("Quản lý", ["📦 Quản lý đơn hàng", "Đăng xuất"])

if menu == "🔑 Đăng nhập":
    st.subheader("Đăng nhập")
    user = st.text_input("Tên đăng nhập")
    pwd = st.text_input("Mật khẩu", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "123":
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.session_state.username = "admin"
            st.success("Đăng nhập admin thành công ✅")
        elif user != "" and pwd != "":
            st.session_state.logged_in = True
            st.session_state.is_admin = False
            st.session_state.username = user
            st.success(f"Xin chào {user} 👋")
        else:
            st.error("Sai thông tin đăng nhập!")

elif menu == "Đăng xuất":
    st.session_state.logged_in = False
    st.session_state.is_admin = False
    st.session_state.username = ""
    st.sidebar.success("Đã đăng xuất!")

# ==============================
# Trang chủ (khách hàng)
# ==============================
if menu == "Trang chủ":
    st.title("🛍️ Cửa hàng online")

    # Chuẩn hóa qty
    for item in st.session_state.cart:
        if "qty" not in item:
            item["qty"] = 1

    for p in products:
        col1, col2 = st.columns([1, 2])
        with col1:
            img = load_drive_image(gdrive_to_direct(p["image"]))
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

# ==============================
# Giỏ hàng
# ==============================
elif menu == "🛒 Giỏ hàng":
    st.title("🛒 Giỏ hàng của bạn")

    if not st.session_state.cart:
        st.info("Giỏ hàng trống!")
    else:
        total = 0
        for item in st.session_state.cart:
            st.write(f"{item['name']} - {item['qty']} x {item['price']:,} VND")
            total += item["qty"] * item["price"]
        st.write(f"### Tổng cộng: {total:,} VND")

        if st.button("✅ Đặt hàng"):
            order = {
                "id": len(st.session_state.orders) + 1,
                "user": st.session_state.username if st.session_state.username else "Khách",
                "items": st.session_state.cart.copy(),
                "status": "Chờ xác nhận",
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.orders.append(order)
            st.session_state.cart = []
            st.session_state.new_order = True
            st.success("Đặt hàng thành công! 📦")

# ==============================
# Đơn hàng của tôi
# ==============================
elif menu == "📦 Đơn hàng của tôi":
    st.title("📦 Đơn hàng của tôi")
    user_orders = [o for o in st.session_state.orders if o["user"] == st.session_state.username]
    if not user_orders:
        st.info("Bạn chưa có đơn hàng nào.")
    else:
        for o in user_orders:
            st.write(f"🆔 Đơn #{o['id']} ({o['time']}) - Trạng thái: {o['status']}")
            for item in o["items"]:
                st.write(f"- {item['name']} x {item['qty']}")
            if o["status"] == "Chờ xác nhận":
                if st.button(f"❌ Hủy đơn #{o['id']}", key=f"cancel_{o['id']}"):
                    o["status"] = "Đã hủy"
                    st.warning("Đơn hàng đã được hủy.")

# ==============================
# Admin quản lý đơn hàng
# ==============================
elif menu == "📦 Quản lý đơn hàng" and st.session_state.is_admin:
    st.title("📦 Quản lý tất cả đơn hàng")

    if st.session_state.new_order:
        st.sidebar.error("🔔 Có đơn hàng mới!")
        st.session_state.new_order = False

    if not st.session_state.orders:
        st.info("Chưa có đơn hàng nào.")
    else:
        for o in st.session_state.orders:
            st.write(f"🆔 Đơn #{o['id']} - Người đặt: {o['user']} ({o['time']})")
            for item in o["items"]:
                st.write(f"- {item['name']} x {item['qty']}")
            st.write(f"**Trạng thái:** {o['status']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Xác nhận #{o['id']}", key=f"confirm_{o['id']}"):
                    o["status"] = "Đã xác nhận"
            with col2:
                if st.button(f"❌ Hủy #{o['id']}", key=f"admin_cancel_{o['id']}"):
                    o["status"] = "Đã hủy"
