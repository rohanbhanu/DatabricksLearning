import os
import streamlit as st

from databricks import sql
from databricks.sdk.core import Config


st.set_page_config(
    page_title="Retail Sales Intelligence",
    page_icon="📊",
    layout="wide"
)


st.title("Retail Sales Intelligence")

st.caption(
    "Databricks Lakehouse Sales Analytics"
)


cfg = Config()


warehouse_id = os.getenv(
    "DATABRICKS_WAREHOUSE_ID"
)


# ---------------------------------------------------------
# Diagnostic information
# ---------------------------------------------------------

if warehouse_id:

    st.success(
        "SQL Warehouse resource detected."
    )

    st.write(
        "Warehouse ID:",
        warehouse_id
    )

else:

    st.error(
        "DATABRICKS_WAREHOUSE_ID was not found."
    )

    st.stop()


# ---------------------------------------------------------
# Create connection
# ---------------------------------------------------------

def get_connection():

    server_hostname = (
        cfg.host
        .replace(
            "https://",
            ""
        )
        .replace(
            "http://",
            ""
        )
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


# ---------------------------------------------------------
# Test simple SQL query first
# ---------------------------------------------------------

try:

    st.info(
        "Connecting to SQL Warehouse..."
    )

    connection = get_connection()

    st.success(
        "SQL Warehouse connection created."
    )


    with connection.cursor() as cursor:

        st.info(
            "Running SELECT 1..."
        )

        cursor.execute(
            "SELECT 1 AS connection_test"
        )

        result = cursor.fetchall()

        st.success(
            "SQL query completed successfully."
        )

        st.write(result)


    connection.close()


except Exception as error:

    st.error(
        "SQL Warehouse connection failed."
    )

    st.exception(error)

    st.stop()