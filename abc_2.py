import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# Page config
st.set_page_config(page_title="ABC Analysis Dashboard", layout="wide")
st.title("📊 ABC Analysis Dashboard")

# File upload
uploaded_file = st.file_uploader("Upload your sales Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df_sales = pd.read_excel(uploaded_file)

        # Clean and prepare
        df_sales = df_sales.dropna(subset=['qty'])
        df_sales = df_sales.sort_values(by='description', ascending=True)
        df_sales.rename(columns={
            'ProductName': 'item_code',
            'LINeSales': 'value'
        }, inplace=True)

        # ABC Classification thresholds
        A, B, C = 80, 15, 5

        # Group by item and calculate total value
        df1 = df_sales.groupby(['item_id'], as_index=False)['value'].sum()
        df1 = df1.sort_values(by='value', ascending=False)
        df1['cumsum'] = df1['value'].cumsum()
        df1['cumperc'] = 100 * df1['cumsum'] / df1['value'].sum()

        # Classify ABC
        df1['class'] = np.where(df1['cumperc'] <= A, 'A',
                        np.where(df1['cumperc'] <= A + B, 'B', 'C'))

        # Merge classification back
        df_sales = df_sales.merge(df1[['item_id', 'class']], on='item_id', how='left')

        # --- Main Area Radio Filters ---
        st.subheader("🔎 Filter Your View")

        col1, col2 = st.columns(2)

        with col1:
            categories = ["All"] + sorted(df_sales['description'].unique().tolist())
            selected_category = st.radio("Select Category", categories, horizontal=True)

        with col2:
            class_options = ['All', 'A', 'B', 'C']
            selected_class = st.radio("Select ABC Class", class_options, horizontal=True)

        # Apply filters
        filtered_df = df_sales.copy()
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df['description'] == selected_category]
        if selected_class != "All":
            filtered_df = filtered_df[filtered_df['class'] == selected_class]

        # Pareto chart (always shown for full dataset)
        st.subheader("Pareto Chart - Cumulative Value %")
        fig_pareto = px.line(df1, x='item_id', y='cumperc', title="Pareto Cumulative % of Value")
        st.plotly_chart(fig_pareto, use_container_width=True)

        # Show filtered results
        st.subheader("Filtered Data Preview")
        st.dataframe(filtered_df)

        # Download button
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

# Footer
st.markdown("""
---
<div style='text-align: center;'>
    With compliments<br>
    <strong>Email:</strong> <a href='mailto:promotions@realanalytics101.co.za'>promotions@realanalytics101.co.za</a><br>
    <strong>Website:</strong> <a href='http://www.realanalytics101.co.za' target='_blank'>www.realanalytics101.co.za</a>
</div>
""", unsafe_allow_html=True)
