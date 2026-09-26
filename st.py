import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Input Ingredients Produk", layout="centered", page_icon="🧪")

st.title("🧪 Tool Input Ingredients Produk")
st.write("Pilih Product ID untuk melihat detail produk, lalu paste ingredients-nya di bawah.")

# ==============================================================================
# 1. LOAD DATA MASTER PRODUK (122 PRODUK KOSONG)
# ==============================================================================
@st.cache_data
def load_queue_data():
    try:
        # Membaca file queue 122 produk kosong
        df = pd.read_csv("products_ingredients_under_13_queu.csv")
        # Pastikan kolom string rapi
        df["product_id"] = df["product_id"].astype(str).str.strip()
        df["soco_brand"] = df["soco_brand"].fillna("").astype(str)
        df["soco_product_name"] = df["soco_product_name"].fillna("").astype(str)
        return df
    except Exception as e:
        st.error(f"Gagal membaca file 'products_ingredients_under_13_queu.csv': {e}")
        return pd.DataFrame()

df_queue = load_queue_data()

if df_queue.empty:
    st.warning("File queue produk kosong atau tidak ditemukan. Pastikan 'products_ingredients_under_13_queu.csv' berada di folder yang sama.")
    st.stop()

# Buat daftar opsi untuk Dropdown: "P000283 - Brand Name - Product Name"
df_queue["display_option"] = df_queue["product_id"] + " | " + df_queue["soco_brand"] + " - " + df_queue["soco_product_name"]
options_list = df_queue["display_option"].tolist()

# ==============================================================================
# 2. PILIHAN PRODUCT ID (SEARCHABLE DROPDOWN)
# ==============================================================================
st.subheader("1. Pilih Produk")

selected_option = st.selectbox(
    "Ketik atau pilih Product ID di sini:",
    options=options_list,
    index=0,
    help="Ketik ID atau nama produk untuk mencari secara cepat"
)

# Ekstrak data produk yang dipilih
selected_row = df_queue[df_queue["display_option"] == selected_option].iloc[0]
selected_pid = selected_row["product_id"]
selected_brand = selected_row["soco_brand"]
selected_pname = selected_row["soco_product_name"]
full_product_title = f"{selected_brand} {selected_pname}".strip()

# Tampilkan Box Info Detail Produk
st.info(f"""
📌 **Detail Produk yang Dipilih:**
* **Product ID:** `{selected_pid}`
* **Brand:** {selected_brand}
* **Nama Produk:** **{selected_pname}**
""")

# Tombol bantu untuk Copy Nama Produk / Search langsung
st.caption("💡 *Gunakan nama lengkap di bawah ini untuk mencari ingredients di Google/Incidecoder:*")
st.code(full_product_title, language="text")

st.divider()

# ==============================================================================
# 3. INPUT TEKS INGREDIENTS
# ==============================================================================
st.subheader("2. Input Ingredients")

raw_text = st.text_area(
    f"Paste Teks Ingredients untuk {selected_pid} di sini:",
    height=220,
    placeholder="Contoh:\nAqua (Water), Cyclopentasiloxane, Titanium Dioxide...\n\natau format berbaris (newline)."
)

def clean_ingredient(text):
    # Hapus teks di dalam kurung beserta kurungnya
    cleaned = re.sub(r"\s*\([^)]*\)", "", text)
    # Hapus karakter invisible/zero-width space
    cleaned = re.sub(r"[\u200B-\u200D\uFEFF]", "", cleaned)
    # Rapikan spasi berlebih
    return re.sub(r"\s+", " ", cleaned).strip()

# Store session state untuk menyimpan data koleksi sementara
if "data_list" not in st.session_state:
    st.session_state.data_list = []

if st.button("➕ Simpan Produk Ini", type="primary"):
    if not raw_text.strip():
        st.error("Teks Ingredients tidak boleh kosong!")
    else:
        # Deteksi otomatis: pisahkan berdasarkan koma atau enter
        if "," in raw_text:
            items = raw_text.strip().split(",")
        else:
            items = raw_text.strip().split("\n")
            
        order = 1
        added_count = 0
        for item in items:
            cleaned = clean_ingredient(item)
            if cleaned:
                st.session_state.data_list.append({
                    "product_id": selected_pid,
                    "ingredient_order": order,
                    "ingredient_name": cleaned
                })
                order += 1
                added_count += 1
                
        st.success(f"✅ Berhasil menyimpan {added_count} ingredients untuk {selected_pid} ({selected_brand})!")

# ==============================================================================
# 4. TABEL HASIL & DOWNLOAD
# ==============================================================================
if st.session_state.data_list:
    st.divider()
    st.subheader("📋 Data yang Sudah Kamu Input")
    
    df_result = pd.DataFrame(st.session_state.data_list)
    
    # Tampilkan tabel ringkasan
    st.dataframe(df_result, use_container_width=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Tombol download file CSV
        csv_data = df_result.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 Download Hasil (.CSV)",
            data=csv_data,
            file_name=f"hasil_ingredients_{len(df_result['product_id'].unique())}_produk.csv",
            mime="text/csv"
        )
        
    with col2:
        if st.button("🗑️ Reset / Hapus Semua"):
            st.session_state.data_list = []
            st.rerun()
