import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- APP CONFIG ---
st.set_page_config(page_title="D&D Mini Catalog", layout="wide")

# --- CONNECT TO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)
df['owned'] = df['owned'].astype(bool)

st.title("⚔️ Miniatures Catalog")

# --- ALPHABETICAL DROPDOWN SEARCH ---
# Creates an alphabetical list for the dropdown
inventory_list = sorted(df['name'].tolist())
selected_creature = st.selectbox(
    "🔍 Search or Select from Inventory:", 
    options=[""] + inventory_list, 
    placeholder="Choose a creature..."
)

st.divider()

# --- FILTERING LOGIC ---
display_df = df.sort_values(by='name')

# If a user selects from the dropdown, show ONLY that creature
if selected_creature:
    display_df = display_df[display_df['name'] == selected_creature]

# --- THE LIST VIEW ---
for index, row in display_df.iterrows():
    with st.container(border=True):
        # Layout: Checkbox | Name | Qty | Stats
        col_check, col_name, col_qty, col_stats = st.columns([1, 5, 1, 1])
        
        with col_check:
            # The Toggle Button
            if not row['owned']:
                if st.button("✅", key=f"check_{row['id']}", use_container_width=True, help="Mark Owned"):
                    df.at[index, 'owned'] = True
                    conn.update(data=df)
                    st.rerun()
            else:
                if st.button("🔄", key=f"undo_{row['id']}", use_container_width=True, help="Unmark"):
                    df.at[index, 'owned'] = False
                    conn.update(data=df)
                    st.rerun()
        
        with col_name:
            # Highlight name if owned
            if row['owned']:
                st.markdown(f"**{row['name']}** (Inventory)")
            else:
                st.markdown(f"**{row['name']}**")
                
            if pd.notna(row['notes']) and row['notes'] != "":
                st.caption(f"*{row['notes']}*")
        
        with col_qty:
            st.write(f"Qty: {row['qty_target']}")
            
        with col_stats:
            # STATS BUTTON
            formatted_name = row['name'].lower().replace(" ", "-")
            stats_url = f"https://open5e.com/monsters/{formatted_name}"
            st.link_button("📊", stats_url, use_container_width=True)
