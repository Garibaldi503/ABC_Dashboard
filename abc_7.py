import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# --- Page Configuration ---
st.set_page_config(page_title="ABC Analysis Dashboard", layout="wide")
st.title("📊 ABC Analysis Dashboard")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your sales Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df_sales = pd.read_excel(uploaded_file)

        # --- Rename Only Sales Column if Needed ---
        rename_map = {
            'LINeSales': 'value',
            'linesales': 'value'
        }
        df_sales.rename(columns={k: v for k, v in rename_map.items() if k in df_sales.columns}, inplace=True)

        # --- Validate Required Columns ---
        required_cols = ['item_id', 'value', 'qty', 'description']
        missing_cols = [col for col in required_cols if col not in df_sales.columns]

        if missing_cols:
            st.error(f"❌ Missing required column(s): {missing_cols}. Please check your Excel file.")
            st.stop()

        # --- Clean and Prepare ---
        df_sales = df_sales.dropna(subset=['qty'])
        df_sales = df_sales.sort_values(by='description', ascending=True)

        # --- ABC Thresholds ---
        A, B, C = 80, 15, 5

        # --- Group by item_id ---
        df1 = df_sales.groupby('item_id', as_index=False)['value'].sum()
        df1 = df1.sort_values(by='value', ascending=False)
        df1['cumsum'] = df1['value'].cumsum()
        df1['cumperc'] = 100 * df1['cumsum'] / df1['value'].sum()

        # --- ABC Class ---
        df1['class'] = np.where(df1['cumperc'] <= A, 'A',
                        np.where(df1['cumperc'] <= A + B, 'B', 'C'))

        # --- Merge Back ---
        df_sales = df_sales.merge(df1[['item_id', 'class']], on='item_id', how='left')

        # --- Filter Controls ---
        st.subheader("🔎 Filter Your View")
        col1, col2 = st.columns(2)

        with col1:
            categories = ["All"] + sorted(df_sales['description'].unique().tolist())
            selected_category = st.radio("Select Category", categories, horizontal=True)

        with col2:
            class_options = ["All", "A", "B", "C"]
            selected_class = st.radio("Select ABC Class", class_options, horizontal=True)

        # --- Apply Filters ---
        filtered_df = df_sales.copy()
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df['description'] == selected_category]
        if selected_class != "All":
            filtered_df = filtered_df[filtered_df['class'] == selected_class]

        # --- Pareto Chart ---
        st.subheader("Pareto Chart - Cumulative Value %")
        fig_pareto = px.line(df1, x='item_id', y='cumperc', title="Pareto Cumulative % by Item")
        st.plotly_chart(fig_pareto, use_container_width=True)

        # --- Show Filtered Data ---
        st.subheader("📋 Filtered Data Based on Your Selection")
        st.dataframe(filtered_df)

        # --- Bar Chart for Selected Group ---
        st.subheader("📊 Value by Item (Filtered, Descending)")
        if not filtered_df.empty:
            df_bar = filtered_df.groupby('item_id', as_index=False)['value'].sum().sort_values(by='value', ascending=False)
            fig_bar = px.bar(df_bar, x='item_id', y='value', title="Item Value (Descending)")
            st.plotly_chart(fig_bar, use_container_width=True)

        # --- Download Filtered Data ---
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='ABC Analysis')
        st.download_button(
            label="📥 Download Filtered Data as Excel",
            data=output.getvalue(),
            file_name="abc_analysis_filtered.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")

# --- Footer ---
st.markdown("""
---
<div style='text-align: center;'>
    With compliments<br>
    <strong>Email:</strong> <a href='mailto:promotions@realanalytics101.co.za'>promotions@realanalytics101.co.za</a><br>
    <strong>Website:</strong> <a href='http://www.realanalytics101.co.za' target='_blank'>www.realanalytics101.co.za</a>
</div>
""", unsafe_allow_html=True)
