import streamlit as st
import pandas as pd
import requests
import json

# --- CẤU HÌNH ---
# Thay thế bằng Bot Token và Channel ID của bạn
token = "OTk1MjI3NzY3MTc4MjcyODc5.GBnFqf.igeJl8idY5jn0sSXRGMzWCyfD9BTYbaAu5K2AQ"  # DÁN TOKEN CỦA BẠN VÀO ĐÂY
CHANNEL_ID = "1429570178017923183" # DÁN CHANNEL ID BẠN MUỐN GỬI TIN NHẮN
TASK_FILE = "tasks.xlsx"
# --- KẾT THÚC CẤU HÌNH ---

def send_discord_message(message):
    """Hàm gửi tin nhắn tới kênh Discord bằng Token."""
    url = "https://discord.com/api/v9/science"
    
    # Header cho user token (KHÔNG có "Bot ")
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    payload = json.dumps({
        "content": message
    })
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Báo lỗi nếu mã trạng thái không phải 2xx
        return True, "Gửi thành công!"
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gửi: {e}")
        return False, str(e)

# --- Giao diện Web App ---

st.set_page_config(layout="wide", page_title="Annotation Task Review")

st.title("📝 Công Cụ Review Task cho Annotator")

# Tải danh sách task từ file Excel
try:
    df = pd.read_excel(TASK_FILE)
except FileNotFoundError:
    st.error(f"Không tìm thấy file `{TASK_FILE}`. Vui lòng tạo file và đặt cùng thư mục với app.py.")
    st.stop()

# Sử dụng session_state để lưu vị trí task hiện tại
if 'current_task_index' not in st.session_state:
    st.session_state.current_task_index = 0

# Hàm để chuyển sang task tiếp theo
def next_task():
    if st.session_state.current_task_index < len(df) - 1:
        st.session_state.current_task_index += 1
    else:
        st.session_state.current_task_index = 0 # Quay lại từ đầu nếu hết task

# Lấy task hiện tại
index = st.session_state.current_task_index
if index < len(df):
    current_task = df.loc[index, 'task_content']

    st.header(f"Task #{index + 1}/{len(df)}")
    st.info("Hãy xem và thực hành với nội dung task dưới đây.")
    
    # Hiển thị phần "practice" (nội dung task)
    st.code(current_task, language='text')
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ Task đã tốt")
        if st.button("Gửi Task Gốc vào Discord", key="good_task"):
            success, message = send_discord_message(current_task)
            if success:
                st.success(f"Đã gửi thành công task #{index + 1} vào Discord.")
                next_task()
                st.rerun() # Tải lại trang để hiển thị task mới
            else:
                st.error(f"Gửi thất bại: {message}")

    with col2:
        st.subheader("❌ Task cần sửa")
        edited_task = st.text_area("Sửa lại nội dung task tại đây:", value=current_task, height=1000)
        if st.button("Gửi Task Đã Sửa vào Discord", key="bad_task"):
            success, message = send_discord_message(edited_task)
            if success:
                st.success(f"Đã gửi thành công task #{index + 1} (đã sửa) vào Discord.")
                # Ghi chú: Bạn có thể thêm logic để lưu lại task đã sửa vào file Excel
                next_task()
                st.rerun()
            else:
                st.error(f"Gửi thất bại: {message}")
else:

    st.warning("Đã hết task trong file Excel!")
