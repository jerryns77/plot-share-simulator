import streamlit as st
import pandas as pd

st.set_page_config(page_title="Plot Share Simulator", layout="wide")

# --- Sidebar inputs ---
st.sidebar.header("Global Parameters")
price_per_cent = st.sidebar.slider(
    "Sale price per cent (currency units)", min_value=100, max_value=10000, value=2500, step=50
)
developer_comm = st.sidebar.slider(
    "Developer commission %", min_value=0.0, max_value=10.0, value=4.5, step=0.1
) / 100.0

st.sidebar.header("Partner P3 Settings")
p3_share_pct = st.sidebar.slider(
    "P3 share of net sale %", min_value=1, max_value=50, value=25, step=1
) / 100.0
p3_cash_pct = st.sidebar.slider(
    "P3 cash payout % of P3 total", min_value=0, max_value=100, value=60, step=5
) / 100.0
p3_advance_paid = st.sidebar.number_input(
    "Total advance paid (currency units)", min_value=0, max_value=1_000_000, value=10000, step=1000
)

# Plots
st.sidebar.header("Plot Configuration")
default_sizes = ",".join([str(5) for _ in range(14)])
plot_sizes_input = st.sidebar.text_input(
    "Plot sizes (cents, comma-separated)", value=default_sizes
)

# Parse plot sizes
sizes = []
try:
    sizes = [float(s.strip()) for s in plot_sizes_input.split(",") if s.strip()]
except:
    st.sidebar.error("Invalid plot sizes format. Use comma-separated numbers.")

# --- DataFrame computation ---
if sizes:
    df = pd.DataFrame({
        "Plot": list(range(1, len(sizes) + 1)),
        "Size (cents)": sizes,
    })
    # Gross sale value per plot
    df["Gross Value"] = df["Size (cents)"] * price_per_cent
    # Net after developer commission
    df["Net Value"] = df["Gross Value"] * (1 - developer_comm)
    # P3 total entitlement
    df["P3 Total"] = df["Net Value"] * p3_share_pct
    df["P3 Cash"] = df["P3 Total"] * p3_cash_pct
    df["P3 Check"] = df["P3 Total"] * (1 - p3_cash_pct)
    # Allocate advance proportionally by plot share
    total_entitlement = df["P3 Total"].sum()
    df["P3 Advance Allocated"] = df["P3 Total"] / total_entitlement * p3_advance_paid
    # Remaining payout after advance
    df["P3 Remaining"] = df["P3 Total"] - df["P3 Advance Allocated"]

    st.title("P3 Plot Share & Payout Simulator")
    # Display table
    st.dataframe(df.style.format({
        "Gross Value": "{:.0f}",
        "Net Value": "{:.0f}",
        "P3 Total": "{:.0f}",
        "P3 Cash": "{:.0f}",
        "P3 Check": "{:.0f}",
        "P3 Advance Allocated": "{:.0f}",
        "P3 Remaining": "{:.0f}"
    }))

    # Charts
    chart_df = df.set_index("Plot")[ ["P3 Cash", "P3 Check", "P3 Advance Allocated", "P3 Remaining"] ]
    st.bar_chart(chart_df)

    # Summary metrics
    st.sidebar.header("Summary for P3")
    st.sidebar.metric("Total Gross for P3", f"{df['P3 Total'].sum():,.0f}")
    st.sidebar.metric("Total Advance Paid", f"{p3_advance_paid:,.0f}")
    st.sidebar.metric("Total Remaining", f"{df['P3 Remaining'].sum():,.0f}")
else:
    st.write("Please enter valid plot sizes in the sidebar.")
