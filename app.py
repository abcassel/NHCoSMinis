import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- APP CONFIG ---
st.set_page_config(page_title="D&D Mini Catalog", layout="wide")

# --- CONNECT TO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# Data Cleaning
df['qty_owned'] = pd.to_numeric(df['qty_owned'], errors='coerce').fillna(0).astype(int)
df['qty_target'] = pd.to_numeric(df['qty_target'], errors='coerce').fillna(1).astype(int)
df['owned'] = df['qty_owned'] >= df['qty_target']

# --- GLOBAL PROGRESS CALCULATION ---
total_needed = df['qty_target'].sum()
total_owned = df['qty_owned'].sum()
progress_percent = int((total_owned / total_needed) * 100) if total_needed > 0 else 0

st.title("⚔️ Barovia Miniatures Collection")

# Display Global Progress
st.write(f"### Overall Collection Progress: {progress_percent}%")
st.progress(total_owned / total_needed)
st.caption(f"You have collected {total_owned} out of {total_needed} total miniatures.")

st.divider()

# --- ALPHABETICAL DROPDOWN SEARCH ---
inventory_list = sorted(df['name'].tolist())
selected_creature = st.selectbox(
    "🔍 Search or Select from Inventory:", 
    options=[""] + inventory_list, 
    placeholder="Choose a creature..."
)

# --- FILTERING ---
display_df = df.sort_values(by='name')
if selected_creature:
    display_df = display_df[display_df['name'] == selected_creature]

# --- THE LIST VIEW ---
for index, row in display_df.iterrows():
    is_complete = row['qty_owned'] >= row['qty_target']
    
    with st.container(border=True):
        col_check, col_name, col_ratio, col_stats = st.columns([1, 4, 2, 1])
        
        with col_check:
            # ✅ Button: Increments count
            if not is_complete:
                if st.button("✅", key=f"add_{row['id']}", use_container_width=True):
                    df.at[index, 'qty_owned'] += 1
                    conn.update(data=df)
                    st.rerun()
            else:
                # 🔄 Button: Resets to 0
                if st.button("🔄", key=f"reset_{row['id']}", use_container_width=True):
                    df.at[index, 'qty_owned'] = 0
                    conn.update(data=df)
                    st.rerun()
        
        with col_name:
            # Name reflects completion
            display_name = f"**{row['name']}**" + (" ✅" if is_complete else "")
            st.markdown(display_name)
            if pd.notna(row['notes']) and row['notes'] != "":
                st.caption(f"*{row['notes']}*")
        
        with col_ratio:
            # Show the "Still Needed" Ratio
            st.write(f"**{row['qty_owned']} / {row['qty_target']}**")
            # Individual item progress
            item_prog = min(row['qty_owned'] / row['qty_target'], 1.0)
            st.progress(item_prog)
            
        with col_stats:
            # 📊 Stats Link
            formatted_name = row['name'].lower().replace(" ", "-")
            stats_url = f"https://open5e.com/monsters/{formatted_name}"
            st.link_button("📊", stats_url, use_container_width=True)
