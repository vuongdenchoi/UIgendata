import streamlit as st
import streamlit.components.v1 as components
import json
import os
import pandas as pd

# Cấu hình giao diện
st.set_page_config(page_title="Medical QA Viewer", layout="wide")

# Cài đặt
DATA_FOLDER = "examples/data_gen"
BATCH_SIZE = 100
SAVE_PATH = "merged_data_after_delete.json"

# --- Danh sách file .json trong thư mục ---
def list_json_files(folder):
    return sorted([f for f in os.listdir(folder) if f.endswith(".json")])

# --- Load dữ liệu từ batch file ---
def load_batch_json(file_list, start_index, batch_size):
    data = []
    end_index = min(start_index + batch_size, len(file_list))
    for filename in file_list[start_index:end_index]:
        try:
            with open(os.path.join(DATA_FOLDER, filename), "r", encoding="utf-8") as f:
                content = json.load(f)

                # Nếu là list
                if isinstance(content, list):
                    for item in content:
                        data.append({
                            "filename": filename,
                            "Question": item.get("Question", ""),
                            "Complex_CoT": item.get("Complex_CoT", ""),
                            "Response": item.get("Response", ""),
                            "Question_translated": item.get("Question_translated", {}).get("result", ""),
                            "Complex_CoT_translated": item.get("Complex_CoT_translated", {}).get("result", ""),
                            "Response_translated": item.get("Response_translated", {}).get("result", ""),
                        })
                # Nếu là object đơn
                elif isinstance(content, dict):
                    data.append({
                        "filename": filename,
                        "Question": content.get("Question", ""),
                        "Complex_CoT": content.get("Complex_CoT", ""),
                        "Response": content.get("Response", ""),
                        "Question_translated": content.get("Question_translated", {}).get("result", ""),
                        "Complex_CoT_translated": content.get("Complex_CoT_translated", {}).get("result", ""),
                        "Response_translated": content.get("Response_translated", {}).get("result", ""),
                    })

        except Exception as e:
            st.warning(f"⚠️ Lỗi khi đọc file `{filename}`: {e}")
    return data

# --- Lưu dữ liệu ra JSON ---
def save_to_json(data_list, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=2)

# --- Khởi tạo trạng thái ---
if "file_list" not in st.session_state:
    st.session_state.file_list = list_json_files(DATA_FOLDER)
    st.session_state.current_index = 0
    st.session_state.data = []

# --- Lần đầu load: lấy 100 file đầu tiên ---
if not st.session_state.data:
    st.session_state.data = load_batch_json(
        st.session_state.file_list,
        st.session_state.current_index,
        BATCH_SIZE
    )

# --- Giao diện hiển thị ---
st.title("🧠 Medical QA Viewer – Load JSON theo từng cụm 100 file")
st.markdown(f"### Tổng số dòng dữ liệu đã load: {len(st.session_state.data)}")

df = pd.DataFrame(st.session_state.data)
columns = df.columns.tolist()

# --- Header bảng ---
header_cols = st.columns(len(columns) + 1)
for i, col in enumerate(columns):
    header_cols[i].markdown(f"**{col}**")
header_cols[-1].markdown("**Xoá**")

# --- Hiển thị từng dòng và xoá ---
for idx, row in df.iterrows():
    row_cols = st.columns(len(columns) + 1)
    for i, col in enumerate(columns):
        content = str(row[col]).replace('\n', '<br>')
        row_cols[i].markdown(
            f"<div style='word-wrap: break-word; white-space: pre-wrap;'>{content}</div>",
            unsafe_allow_html=True
        )
    if row_cols[-1].button("🗑️", key=f"delete_{idx}"):
        st.session_state.data.pop(idx)
        save_to_json(st.session_state.data, SAVE_PATH)
        st.success(f"✅ Đã xoá dòng {idx+1} và lưu vào `{SAVE_PATH}`")
        st.rerun()

# --- Nút tải JSON đã chỉnh sửa ---
st.markdown("---")
if os.path.exists(SAVE_PATH):
    with open(SAVE_PATH, "rb") as f:
        st.download_button("📥 Tải JSON đã chỉnh sửa", f, file_name=SAVE_PATH, mime="application/json")

# --- Nút load thêm 100 file tiếp theo ---
next_index = st.session_state.current_index + BATCH_SIZE
if next_index < len(st.session_state.file_list):
    if st.button("➡️ Load thêm 100 file tiếp theo"):
        st.session_state.current_index = next_index
        new_data = load_batch_json(
            st.session_state.file_list,
            st.session_state.current_index,
            BATCH_SIZE
        )
        st.session_state.data.extend(new_data)

        # ✅ Auto scroll lên đầu trang
        components.html("<script>window.scrollTo({ top: 0, behavior: 'smooth' });</script>", height=0)

        st.rerun()
else:
    st.info("✅ Đã load toàn bộ file JSON trong thư mục.")
