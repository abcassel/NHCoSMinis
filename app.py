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

# --- SEARCH ---
search_query = st.text_input("🔍 Search creatures...", placeholder="Search...")

# --- FILTERING ---
display_df = df.sort_values(by='name')
if search_query:
    display_df = display_df[display_df['name'].str.contains(search_query, case=False)]

st.divider()

# --- THE LIST VIEW ---
for index, row in display_df.iterrows():
    status_emoji = "🟢" if row['owned'] else "🔴"
    
    with st.container(border=True):
        # Using a very compact column ratio
        col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{status_emoji} {row['name']}**")
            if pd.notna(row['notes']) and row['notes'] != "":
                st.caption(f"*{row['notes']}*")
        
        with col2:
            st.write(f"Qty: {row['qty_target']}")
            
        with col3:
            # STATS BUTTON
            formatted_name = row['name'].lower().replace(" ", "-")
            stats_url = f"https://open5e.com/monsters/{formatted_name}"
            st.link_button("📊", stats_url, use_container_width=True, help="View Stats")
            
        with col4:
            # THE TOGGLE BUTTON (Green Check vs Undo)
            if not row['owned']:
                if st.button("✅", key=f"btn_{row['id']}", use_container_width=True, help="Mark as Owned"):
                    df.at[index, 'owned'] = True
                    conn.update(data=df)
                    st.rerun()
            else:
                if st.button("🔄", key=f"btn_{row['id']}", use_container_width=True, help="Mark as Missing"):
                    df.at[index, 'owned'] = False
                    conn.update(data=df)
                    st.rerun()
