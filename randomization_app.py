import random
import csv
from datetime import datetime
import pandas as pd
import streamlit as st

st.title("Block Randomization App - Parallel Design 1:1 with Withdrawals")

# Initialize session state
if "randomized" not in st.session_state:
    st.session_state.randomized = []
if "withdrawn" not in st.session_state:
    st.session_state.withdrawn = []
if "seed" not in st.session_state:
    st.session_state.seed = 42
if "block_queue" not in st.session_state:
    st.session_state.block_queue = []

# Input seed for reproducibility
seed = st.number_input("Enter a seed for reproducibility (optional)", value=st.session_state.seed, step=1)
st.session_state.seed = seed
random.seed(seed)

# Input for total number of participants needed
target_enrollment = st.number_input("Target number of enrolled participants", min_value=2, max_value=1000, value=50, step=2)

# Determine current enrollment
current_enrolled = len(st.session_state.randomized) - len(st.session_state.withdrawn)
remaining_slots = target_enrollment - current_enrolled

st.markdown(f"**Current Enrolled:** {current_enrolled} / {target_enrollment}")

# Create new block if block_queue is empty
def generate_block():
    block_size = 4  # Must be even for 1:1 allocation
    block = ["M+K group", "SOC group"] * (block_size // 2)
    random.shuffle(block)
    return block

if remaining_slots > 0:
    if st.button("Randomize Next Participant"):
        if not st.session_state.block_queue:
            st.session_state.block_queue = generate_block()

        participant_id = f"P{len(st.session_state.randomized) + 1:03d}"
        group = st.session_state.block_queue.pop(0)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.randomized.append({"ID": participant_id, "Group": group, "Timestamp": timestamp, "Note": ""})

# Display randomized participants
if st.session_state.randomized:
    df = pd.DataFrame(st.session_state.randomized)
    df["Status"] = df["ID"].apply(lambda x: "Withdrawn" if x in st.session_state.withdrawn else "Enrolled")

    for i, row in df.iterrows():
        with st.expander(f"{row['ID']} - {row['Group']} ({row['Status']})"):
            note = st.text_input(f"Note for {row['ID']}", value=row['Note'], key=f"note_{row['ID']}")
            st.session_state.randomized[i]["Note"] = note

            if row['Status'] == "Enrolled":
                if st.button(f"Mark {row['ID']} as Withdrawn", key=f"withdraw_{row['ID']}"):
                    st.session_state.withdrawn.append(row['ID'])
            else:
                if st.button(f"Undo Withdrawal for {row['ID']}", key=f"undo_{row['ID']}"):
                    st.session_state.withdrawn.remove(row['ID'])

    # Filter to only enrolled participants
    enrolled_df = df[df["Status"] == "Enrolled"]
    enrolled_df = enrolled_df.drop(columns=["Status"])

    csv = enrolled_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Enrolled Participants as CSV",
        data=csv,
        file_name='enrolled_randomization_results.csv',
        mime='text/csv',
    )
else:
    st.info("No participants randomized yet.")
