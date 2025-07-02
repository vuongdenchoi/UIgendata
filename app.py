import streamlit as st
import json
import os
import pandas as pd

# Cấu hình trang rộng
st.set_page_config(page_title="Medical QA Viewer", layout="wide")

# Đường dẫn và giới hạn
DATA_FOLDER = "examples/data_gen"
BATCH_SIZE = 100
SAVE_PATH = "merged_data_after_delete.json"

# --- Load danh sách file .json trong thư mục ---
def list_json_files(folder):
    return sorted([f for f in os.listdir(folder) if f.endswith(".json")])

# --- Load batch dữ liệu từ file ---
def load_batch_json(file_list, start_index, batch_size):
    data = []
    end_index = min(start_index + batch_size, len(file_list))
    for filename in file_list[start_index:end_index]:
        try:
            with open(os.path.join(DATA_FOLDER, filename), "r", encoding="utf-8") as f:
                content = json.load(f)
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

# --- Lưu JSON ---
def save_to_json(data_list, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=2)

# --- KHỞI TẠO SESSION STATE ---
if "file_list" not in st.session_state:
    st.session_state.file_list = list_json_files(DATA_FOLDER)
    st.session_state.current_index = 0
    st.session_state.data = []

# --- LOAD DỮ LIỆU NẾU CHƯA CÓ ---
if not st.session_state.data:
    st.session_state.data = load_batch_json(
        st.session_state.file_list,
        st.session_state.current_index,
        BATCH_SIZE
    )

# --- TẠO DATAFRAME ---
df = pd.DataFrame(st.session_state.data)

# --- GIAO DIỆN ---
st.title("🧠 Medical QA Viewer - Phân trang từng 100 file")
st.markdown(f"### Tổng số dòng dữ liệu: {len(df)}")

columns = df.columns.tolist()

# --- HIỂN THỊ HEADER ---
header_cols = st.columns(len(columns) + 1)
for i, col in enumerate(columns):
    header_cols[i].markdown(f"**{col}**")
header_cols[-1].markdown("**Xoá**")

# --- HIỂN THỊ DÒNG VÀ NÚT XOÁ ---
for idx, row in df.iterrows():
    row_cols = st.columns(len(columns) + 1)
    for i, col in enumerate(columns):
        row_cols[i].markdown(
            f"<div style='word-wrap: break-word; white-space: pre-wrap;'>{str(row[col]).replace(chr(10), '<br>')}</div>",
            unsafe_allow_html=True
        )
    if row_cols[-1].button("🗑️", key=f"delete_{idx}"):
        st.session_state.data.pop(idx)
        save_to_json(st.session_state.data, SAVE_PATH)
        st.success(f"✅ Đã xoá dòng {idx+1} và lưu vào `{SAVE_PATH}`")
        st.rerun()

# --- NÚT TẢI FILE ---
st.markdown("---")
if os.path.exists(SAVE_PATH):
    with open(SAVE_PATH, "rb") as f:
        st.download_button("📥 Tải dữ liệu đã chỉnh sửa", f, file_name=SAVE_PATH, mime="application/json")

# --- NÚT LOAD TIẾP 100 FILE TIẾP THEO ---
next_index = st.session_state.current_index + BATCH_SIZE
if next_index < len(st.session_state.file_list):
    if st.button("➡️ Load thêm 100 file tiếp theo"):
        st.session_state.current_index = next_index
        st.session_state.data = load_batch_json(
            st.session_state.file_list,
            st.session_state.current_index,
            BATCH_SIZE
        )
        st.rerun()
else:
    st.info("✅ Đã load toàn bộ dữ liệu trong thư mục.")
