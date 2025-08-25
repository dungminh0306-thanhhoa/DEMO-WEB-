import streamlit as st

# Hàm chuyển link Google Drive thành link ảnh trực tiếp
def gdrive_to_direct(link):
    if "drive.google.com" in link:
        if "/file/d/" in link:  # dạng https://drive.google.com/file/d/FILE_ID/view?usp=sharing
            file_id = link.split("/file/d/")[1].split("/")[0]
            return f"https://drive.google.com/uc?export=view&id={file_id}"
        elif "id=" in link:  # dạng https://drive.google.com/open?id=FILE_ID
            file_id = link.split("id=")[1]
            return f"https://drive.google.com/uc?export=view&id={file_id}"
    return link

# Danh sách sản phẩm test
products = [
    {"id": 1, "name": "Áo thun", "price": 120000,
     "image": "https://drive.google.com/file/d/1s6sJALOs2IxX5f9nqa4Tf8zut_U9KE3O/view?usp=drive_link"},
    {"id": 2, "name": "Quần jean", "price": 250000,
     "image": "https://via.placeholder.com/150"},
    {"id": 3, "name": "Áo khoác", "price": 350000,
     "image": "https://via.placeholder.com/150"},
]

st.title("🖼️ Test hiển thị ảnh Google Drive")

for p in products:
    st.image(gdrive_to_direct(p["image"]), caption=p["name"], width=200)
    st.write(f"Giá: {p['price']:,} VND")

