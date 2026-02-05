import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- APP CONFIG ---
st.set_page_config(page_title="D&D Mini & Stat Tracker", layout="wide")

# --- CONNECT TO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# Ensure 'owned' is boolean for the toggle logic
df['owned'] = df['owned'].astype(bool)

st.title("⚔️ Barovia Inventory & Bestiary")

# --- SEARCH BAR ---
search_query = st.text_input("🔍 Search creatures...", placeholder="Type name here (e.g. Bat, Strahd, Knight)")

# --- FILTERING ---
display_df = df.sort_values(by='name')
if search_query:
    display_df = display_df[display_df['name'].str.contains(search_query, case=False)]

st.divider()

# --- THE LIST VIEW ---
for index, row in display_df.iterrows():
    # Define status visual
    status_emoji = "🟢" if row['owned'] else "🔴"
    
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.markdown(f"### {status_emoji} {row['name']}")
            st.caption(f"**Category:** {row['category']} | **ID:** {row['id']}")
            if pd.notna(row['notes']) and row['notes'] != "":
                st.info(f"📍 {row['notes']}")
        
        with col2:
            # DYNAMIC STAT BUTTON
            # Formats name for URL: "Dire Wolf" -> "dire-wolf"
            formatted_name = row['name'].lower().replace(" ", "-")
            
            # We'll use Open5e as the primary source as it's very reliable for SRD monsters
            stats_url = f"https://open5e.com/monsters/{formatted_name}"
            
            st.write(f"**Target Qty:** {row['qty_target']}")
            st.link_button("📜 View Stat Block", stats_url, use_container_width=True)
            
        with col3:
            # THE TOGGLE BUTTON
            button_label = "Got it!" if not row['owned'] else "Mark Missing"
            if st.button(button_label, key=f"btn_{row['id']}", use_container_width=True):
                df.at[index, 'owned'] = not row['owned']
                conn.update(data=df)
                st.rerun()

# --- FOOTER ---
st.divider()
needed_count = len(df[df['owned'] == False])
st.write(f"💡 **Quick Tip:** You still need to find **{needed_count}** more miniatures to complete the set.")
