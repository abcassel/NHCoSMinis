import streamlit as st
from streamlit_gsheets import GSheetsConnection
import random

st.set_page_config(page_title="D&D Mini Tracker", layout="centered")

# --- CONNECT TO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# Initialize session state for navigation
if 'nav_mode' not in st.session_state:
    st.session_state.nav_mode = "ABC"

st.title("⚔️ Creature Verification")

# --- SEARCH BAR ---
# Creates a searchable list of all creature names
search_query = st.selectbox("🔍 Quick Search for a Creature:", 
                            options=[""] + list(df['name'].sort_values().unique()),
                            help="Start typing a name to jump directly to that creature")

st.divider()

# --- NAVIGATION MODES ---
st.write("### Queue Order:")
c1, c2, c3 = st.columns(3)
if c1.button("🔤 ABC (Needed)"): st.session_state.nav_mode = "ABC"
if c2.button("🐾 TYPE (Needed)"): st.session_state.nav_mode = "TYPE"
if c3.button("🎲 RANDOM (All)"): st.session_state.nav_mode = "RANDOM"

# --- FILTERING LOGIC ---
if search_query != "":
    # If user searched for something, prioritize that specific row
    display_queue = df[df['name'] == search_query]
    st.caption(f"Viewing search result for: {search_query}")
else:
    # Otherwise, use the standard queue logic
    needed_df = df[df['owned'] == False].copy()
    
    if st.session_state.nav_mode == "ABC":
        display_queue = needed_df.sort_values(by='name')
    elif st.session_state.nav_mode == "TYPE":
        display_queue = needed_df.sort_values(by=['category', 'name'])
    elif st.session_state.nav_mode == "RANDOM":
        display_queue = df.sample(frac=1)

# --- DISPLAY CARD ---
if not display_queue.empty:
    item = display_queue.iloc[0]
    item_index = df[df['id'] == item['id']].index[0]

    with st.container(border=True):
        st.header(f"{item['name']}")
        st.write(f"**ID:** {item['id']} | **Type:** {item['category']}")
        st.write(f"**Target:** {item['qty_target']} | **Priority:** {item['priority']}")
        
        if item['owned']:
            st.success("✅ ALREADY IN INVENTORY")
        
        col_a, col_b = st.columns(2)
        
        if col_a.button("✅ Mark as Exists", use_container_width=True):
            df.at[item_index, 'owned'] = True
            conn.update(data=df)
            st.balloons()
            st.rerun()
            
        if col_b.button("⏭️ Next Creature", use_container_width=True):
            st.rerun()
else:
    st.success("All caught up! No more items match your current filter.")
