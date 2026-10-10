
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Message Ordering Simulator",
    page_icon="📨",
    layout="wide"
)

st.title("📨 Message Ordering Simulator")
st.subheader("Distributed Computing Mini Project")
st.write(
    "This project simulates message delivery between "
    "distributed processes using different ordering algorithms."
)

# Sample message dataset
messages = [
    {"ID": "M1", "Sender": "P1", "Receiver": "P2",
     "Send Time": 1, "Delay": 4, "Depends On": "-"},
    {"ID": "M2", "Sender": "P1", "Receiver": "P3",
     "Send Time": 2, "Delay": 1, "Depends On": "M1"},
    {"ID": "M3", "Sender": "P2", "Receiver": "P3",
     "Send Time": 3, "Delay": 0, "Depends On": "-"},
    {"ID": "M4", "Sender": "P3", "Receiver": "P1",
     "Send Time": 4, "Delay": 2, "Depends On": "M2"},
    {"ID": "M5", "Sender": "P2", "Receiver": "P1",
     "Send Time": 5, "Delay": 1, "Depends On": "M3"}
]


def simulate(data, algorithm):
    pending = data.to_dict("records")
    delivered = []

    # Keep each sender's messages in send order
    sender_messages = {}

    for msg in pending:
        sender_messages.setdefault(msg["Sender"], [])
        sender_messages[msg["Sender"]].append(msg)

    for sender in sender_messages:
        sender_messages[sender].sort(
            key=lambda m: m["Send Time"]
        )

    # Total ordering: one common global ordering
    if algorithm == "Total Ordering":
        return sorted(
            pending,
            key=lambda m: (m["Send Time"], m["ID"])
        )

    # FIFO or causal ordering
    while pending:
        eligible = []

        for msg in pending:
            sender = msg["Sender"]
            previous = sender_messages[sender]

            position = previous.index(msg)

            # Check whether previous messages from this sender
            # have already been delivered.
            sender_ok = all(
                old["ID"] in [d["ID"] for d in delivered]
                for old in previous[:position]
            )

            dependency_ok = True

            if algorithm == "Causal Ordering":
                dependency = msg["Depends On"]

                if dependency != "-":
                    dependency_ok = dependency in [
                        d["ID"] for d in delivered
                    ]

            if sender_ok and dependency_ok:
                eligible.append(msg)

        if not eligible:
            break

        # Deliver the eligible message with earliest arrival time
        chosen = min(
            eligible,
            key=lambda m: (
                m["Send Time"] + m["Delay"],
                m["Send Time"],
                m["ID"]
            )
        )

        delivered.append(chosen)
        pending.remove(chosen)

    return delivered


# Sidebar controls
st.sidebar.header("Simulation Settings")

algorithm = st.sidebar.selectbox(
    "Select Ordering Algorithm",
    [
        "FIFO Ordering",
        "Causal Ordering",
        "Total Ordering"
    ]
)

st.sidebar.write("**Processes:** P1, P2, P3")
st.sidebar.write("**Total sample messages:** 5")

# Convert data into a DataFrame
df = pd.DataFrame(messages)
df["Arrival Time"] = df["Send Time"] + df["Delay"]

st.header("1. Message Information")
st.dataframe(df, use_container_width=True, hide_index=True)

st.header("2. Run Simulation")

if st.button("Simulate Message Delivery", type="primary"):
    result = simulate(df, algorithm)

    if result:
        result_df = pd.DataFrame(result)
        result_df["Delivery Order"] = range(
            1, len(result_df) + 1
        )

        st.success("Simulation completed successfully!")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Messages", len(result_df))
        col2.metric("Processes", 3)
        col3.metric("Selected Algorithm", algorithm)

        st.header("3. Message Delivery Sequence")

        sequence = " → ".join(result_df["ID"].tolist())
        st.info(sequence)

        st.header("4. Delivery Details")

        st.dataframe(
            result_df[
                [
                    "Delivery Order",
                    "ID",
                    "Sender",
                    "Receiver",
                    "Send Time",
                    "Arrival Time",
                    "Depends On"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.header("5. Message Arrival Chart")

        chart_df = result_df.set_index("ID")[["Arrival Time"]]
        st.bar_chart(chart_df)

        st.header("6. Algorithm Explanation")

        if algorithm == "FIFO Ordering":
            st.write(
                "FIFO ensures messages from the same sender "
                "are delivered in the order they were sent."
            )

        elif algorithm == "Causal Ordering":
            st.write(
                "Causal ordering ensures that a message's "
                "declared dependency is delivered first."
            )

        else:
            st.write(
                "Total ordering uses one common global sequence "
                "based on send time and message ID."
            )

    else:
        st.error(
            "No valid delivery sequence found. "
            "Check the message dependencies."
        )

st.divider()

st.caption(
    "Distributed Computing Mini Project | "
    "Message Ordering Simulator"
)
