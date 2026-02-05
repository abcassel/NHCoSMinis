import streamlit as st
from streamlit_gsheets import GSheetsConnection

# --- APP CONFIG ---
st.set_page_config(page_title="D&D Permanent Tracker", layout="centered")

st.title("⚔️ Permanent Inventory Tracker")

# --- CONNECT TO GOOGLE SHEETS ---
# This creates a connection object
conn = st.connection("gsheets", type=GSheetsConnection)

# Read the existing data
# Replace 'YOUR_SHEET_URL_HERE' with your actual sheet link in the next step
df = conn.read(ttl=0) # ttl=0 ensures we always get fresh data

# --- LOGIC ---
tabs = st.tabs(["Verification Feed", "Inventory So Far", "Still Needed"])

with tabs[0]:
    # Filter for items where owned is False
    queue = df[df['owned'] == False]
    
    if len(queue) > 0:
        item = queue.iloc[0]
        # Find the exact row index in the original dataframe
        item_index = queue.index[0]

        with st.container(border=True):
            st.subheader(f"{item['name']} ({item['id']})")
            st.write(f"**Target Qty:** {item['qty_target']} | **Priority:** {item['priority']}")
            
            col1, col2 = st.columns(2)
            
            if col1.button("✅ Exists", use_container_width=True):
                # Update the value in the dataframe
                df.at[item_index, 'owned'] = True
                # Write the whole dataframe back to the Google Sheet
                conn.update(data=df)
                st.success(f"Updated {item['name']}!")
                st.rerun()
                
            if col2.button("📁 File Needed", use_container_width=True):
                st.info("Item remains in 'Still Needed' list.")
                # You could add logic here to flag 'needs_filing' if you add a column for it
    else:
        st.success("🎉 All items verified!")

with tabs[1]:
    st.dataframe(df[df['owned'] == True][['id', 'name', 'category']])

with tabs[2]:
    st.dataframe(df[df['owned'] == False][['id', 'name', 'priority']])