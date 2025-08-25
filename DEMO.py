import streamlit as st
from urllib.parse import urlparse, parse_qs
import re

# Hàm chuyển link Google Drive thành link ảnh trực tiếp (đã làm robust)
def gdrive_to_direct(link: str) -> str:
    if not link:
        return link
    try:
        url = urlparse(link)
    except Exception:
        return link

    # Nếu không phải link Drive hoặc đã là googleusercontent (đã trực tiếp) thì trả về nguyên
    if ("drive.google.com" not in url.netloc) or ("googleusercontent.com" in url.netloc):
        return link

    # 1) Ưu tiên lấy qua query ?id=FILE_ID (open?id=..., uc?id=..., thumbnail?id=...)
    qs = parse_qs(url.query)
    file_id = None
    if "id" in qs and qs["id"]:
        file_id = qs["id"][0]

    # 2) Nếu không có, bắt dạng /file/d/FILE_ID/... hoặc /d/FILE_ID/...
    if not file_id:
        m = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url.path)
        if not m:
            m = re.search(r"/d/([a-zA-Z0-9_-]+)", url.path)
        if m:
            file_id = m.group(1)

    # Nếu vẫn không có ID (có thể là link folder...), trả lại link gốc
    if not file_id:
        return link

    # Trả về link nhúng ảnh trực tiếp
    return f"https://drive.google.com/uc?export=view&id={file_id}"

# Danh sách sản phẩm test
products = [
    {
        "id": 1,
        "name": "Áo thun",
        "price": 120000,
        # Link Drive dạng /file/d/.../view?usp=...
        "image": "https://drive.google.com/file/d/1s6sJALOs2IxX5f9nqa4Tf8zut_U9KE3O/view?usp=drive_link",
    },
    {
        "id": 2,
        "name": "Quần jean",
        "price": 250000,
        "image": "https://via.placeholder.com/150",
    },
    {
        "id": 3,
        "name": "Áo khoác",
        "price": 350000,
        "image": "https://via.placeholder.com/150",
    },
]

st.title("🖼️ Test hiển thị ảnh Google Drive")

# Tuỳ chọn debug để xem link trước/sau khi convert
show_debug = st.checkbox("Hiện link gốc & link đã convert để debug", value=False)

for p in products:
    direct_link = gdrive_to_direct(p["image"])
    if show_debug:
        st.write(f"Link gốc: {p['image']}")
        st.write(f"Link convert: {direct_link}")
    st.image(direct_link, caption=p["name"], width=200)
    st.write(f"Giá: {p['price']:,} VND")
