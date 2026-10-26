import pandas as pd
import streamlit as st

from databricks import sql
from databricks.sdk.core import Config


st.set_page_config(
    page_title="Retail Sales Intelligence",
    page_icon="📊",
    layout="wide"
)


cfg = Config()


def get_connection():

    server_hostname = cfg.host

    server_hostname = server_hostname.replace(
        "https://",
        ""
    ).replace(
        "http://",
        ""
    )

    return sql.connect(
        server_hostname=server_hostname,
        http_path="YOUR_HTTP_PATH",
        credentials_provider=lambda: cfg.authenticate,
        _use_arrow_native_complex_types=False
    )


@st.cache_data(ttl=300)
def run_query(query):

    connection = get_connection()

    with connection.cursor() as cursor:

        cursor.execute(query)

        df = (
            cursor
            .fetchall_arrow()
            .to_pandas()
        )

    connection.close()

    return df


st.title("Retail Sales Intelligence")

st.caption(
    "Databricks Lakehouse Sales Analytics"
)


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


st.dataframe(
    kpi_df,
    use_container_width=True
)