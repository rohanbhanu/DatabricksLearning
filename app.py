import os
import streamlit as st

from databricks import sql
from databricks.sdk.core import Config


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Retail Sales Intelligence",
    page_icon="📊",
    layout="wide"
)

st.title("Retail Sales Intelligence")

st.caption(
    "Databricks Lakehouse Sales Analytics"
)


# =========================================================
# DATABRICKS CONFIGURATION
# =========================================================

cfg = Config()

warehouse_id = os.getenv(
    "DATABRICKS_WAREHOUSE_ID"
)


# =========================================================
# VALIDATE SQL WAREHOUSE RESOURCE
# =========================================================

if not warehouse_id:

    st.error(
        "DATABRICKS_WAREHOUSE_ID was not found."
    )

    st.stop()


# =========================================================
# SQL CONNECTION
# =========================================================

def get_connection():

    server_hostname = (
        cfg.host
        .replace("https://", "")
        .replace("http://", "")
    )

    http_path = (
        f"/sql/1.0/warehouses/{warehouse_id}"
    )

    return sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
        _use_arrow_native_complex_types=False
    )


# =========================================================
# GENERIC QUERY FUNCTION
# =========================================================

def run_query(query):

    connection = None

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute(query)

            result = (
                cursor
                .fetchall_arrow()
                .to_pandas()
            )

        return result

    finally:

        if connection is not None:

            connection.close()


# =========================================================
# LOAD GOLD KPI DATA
# =========================================================

try:

    kpi_df = run_query(
        """
        SELECT
            total_orders,
            total_customers,
            net_sales,
            gross_profit,
            avg_order_value,
            profit_margin_pct
        FROM retail_demo.gold.sales_kpi
        """
    )


    # =====================================================
    # DISPLAY KPI CARDS
    # =====================================================

    if not kpi_df.empty:

        row = kpi_df.iloc[0]


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                label="Net Sales",
                value=f"₹{row['net_sales']:,.0f}"
            )


        with col2:

            st.metric(
                label="Gross Profit",
                value=f"₹{row['gross_profit']:,.0f}"
            )


        with col3:

            st.metric(
                label="Total Orders",
                value=f"{row['total_orders']:,.0f}"
            )


        col4, col5, col6 = st.columns(3)


        with col4:

            st.metric(
                label="Total Customers",
                value=f"{row['total_customers']:,.0f}"
            )


        with col5:

            st.metric(
                label="Average Order Value",
                value=f"₹{row['avg_order_value']:,.0f}"
            )


        with col6:

            st.metric(
                label="Profit Margin",
                value=f"{row['profit_margin_pct']:.2f}%"
            )


    else:

        st.warning(
            "Gold sales KPI table returned no records."
        )


except Exception as error:

    st.error(
        "Unable to query retail_demo.gold.sales_kpi."
    )

    st.exception(error)