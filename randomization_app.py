import random
import csv
from datetime import datetime
import pandas as pd
import streamlit as st

st.title("Simple Randomization App - Parallel Design 1:1 with Withdrawals")

# Initialize session state
if "randomized" not in st.session_state:
    st.session_state.randomized = []
if "withdrawn" not in st.session_state:
    st.session_state.withdrawn = []
if "seed" not in st.session_state:
    st.session_state.seed = 42
if "to_remove" not in st.session_state:
    st.session_state.to_remove = None

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

if remaining_slots > 0:
    if st.button("Randomize Next Participant"):
        participant_id = f"P{len(st.session_state.randomized) + 1:03d}"
        group_counts = {
            "M+K group": sum(1 for p in st.session_state.randomized if p['Group'] == "M+K group" and p['ID'] not in st.session_state.withdrawn),
            "SOC group": sum(1 for p in st.session_state.randomized if p['Group'] == "SOC group" and p['ID'] not in st.session_state.withdrawn),
        }
        if group_counts["M+K group"] > group_counts["SOC group"]:
            group = "SOC group"
        elif group_counts["M+K group"] < group_counts["SOC group"]:
            group = "M+K group"
        else:
            group = random.choice(["M+K group", "SOC group"])

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.randomized.append({"ID": participant_id, "Group": group, "Timestamp": timestamp, "Note": ""})

# Handle participant removal
if st.session_state.to_remove:
    st.session_state.randomized = [p for p in st.session_state.randomized if p["ID"] != st.session_state.to_remove]
    if st.session_state.to_remove in st.session_state.withdrawn:
        st.session_state.withdrawn.remove(st.session_state.to_remove)
    st.session_state.to_remove = None

# Display randomized participants
if st.session_state.randomized:
    df = pd.DataFrame(st.session_state.randomized)
    df["Status"] = df["ID"].apply(lambda x: "Withdrawn" if x in st.session_state.withdrawn else "Enrolled")

    for i, row in df.iterrows():
        with st.expander(f"{row['ID']} - {row['Group']} ({row['Status']})"):
            note = st.text_input(f"Note for {row['ID']}", value=row['Note'], key=f"note_{row['ID']}")
            st.session_state.randomized[i]["Note"] = note

            cols = st.columns([1, 1, 2])
            if row['Status'] == "Enrolled":
                if cols[0].button(f"Withdraw", key=f"withdraw_{row['ID']}"):
                    st.session_state.withdrawn.append(row['ID'])
            else:
                if cols[0].button(f"Undo", key=f"undo_{row['ID']}"):
                    st.session_state.withdrawn.remove(row['ID'])

            if cols[1].button(f"Remove", key=f"remove_{row['ID']}"):
                st.session_state.to_remove = row['ID']
                st.experimental_rerun()

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
