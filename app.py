import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from databricks import sql
from databricks.sdk.core import Config


# =========================================================
# CONSTANTS
# =========================================================

IVORY = "#FFFFF0"
MUTED_IVORY = "#DEDCCB"
NAVY = "#071426"
SECONDARY_NAVY = "#0B2442"
PANEL_NAVY = "#102F52"

SKY_BLUE = "#38BDF8"
MINT_GREEN = "#59E3AE"
LAVENDER = "#C084FC"
INDIGO = "#818CF8"
CORAL = "#FB7185"
AMBER = "#FBBF24"

CHART_COLORS = [
    SKY_BLUE,
    MINT_GREEN,
    LAVENDER,
    INDIGO,
    CORAL,
    AMBER,
    "#22D3EE",
    "#A3E635"
]


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Retail Sales Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM STREAMLIT STYLING
# =========================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background:
            linear-gradient(
                145deg,
                {NAVY} 0%,
                {SECONDARY_NAVY} 55%,
                {PANEL_NAVY} 100%
            );
        color: {IVORY};
    }}

    [data-testid="stHeader"] {{
        background: rgba(0, 0, 0, 0);
    }}

    [data-testid="stToolbar"] {{
        color: {IVORY};
    }}

    [data-testid="stAppViewContainer"] {{
        color: {IVORY};
    }}

    [data-testid="stMainBlockContainer"] {{
        padding-top: 2rem;
    }}

    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {{
        color: {IVORY} !important;
    }}

    p,
    label,
    span {{
        color: {IVORY};
    }}

    [data-testid="stMarkdownContainer"] {{
        color: {IVORY};
    }}

    [data-testid="stMarkdownContainer"] p {{
        color: {MUTED_IVORY};
    }}

    [data-testid="stCaptionContainer"] {{
        color: {MUTED_IVORY} !important;
    }}

    [data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.075);
        border: 1px solid rgba(255, 255, 240, 0.16);
        border-radius: 14px;
        padding: 17px;
        min-height: 130px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.14);
    }}

    [data-testid="stMetricLabel"] {{
        color: {IVORY} !important;
        font-size: 15px;
        font-weight: 600;
    }}

    [data-testid="stMetricLabel"] p {{
        color: {IVORY} !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {IVORY} !important;
        font-weight: 700;
    }}

    [data-testid="stMetricDelta"] {{
        color: {MINT_GREEN} !important;
    }}

    [data-testid="stRadio"] label {{
        color: {IVORY} !important;
    }}

    [data-testid="stRadio"] p {{
        color: {IVORY} !important;
        font-size: 15px;
    }}

    div[role="radiogroup"] label {{
        color: {IVORY} !important;
    }}

    div[role="radiogroup"] span {{
        color: {IVORY} !important;
    }}

    button[data-baseweb="tab"] {{
        color: {MUTED_IVORY} !important;
        font-weight: 600;
        font-size: 14px;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {IVORY} !important;
    }}

    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
        background-color: {SKY_BLUE};
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid rgba(255, 255, 240, 0.16);
        border-radius: 10px;
        overflow: hidden;
    }}

    [data-testid="stAlert"] {{
        color: {IVORY};
        border-radius: 10px;
    }}

    [data-testid="stAlert"] p {{
        color: {IVORY} !important;
    }}

    hr {{
        border-color: rgba(255, 255, 240, 0.15);
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DATABRICKS CONFIGURATION
# =========================================================

cfg = Config()

warehouse_id = os.getenv(
    "DATABRICKS_WAREHOUSE_ID"
)


if not warehouse_id:

    st.error(
        "The SQL Warehouse resource is not configured."
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
# QUERY FUNCTION
# =========================================================

@st.cache_data(
    ttl=300,
    show_spinner=False
)
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
# DATA CONVERSION HELPERS
# =========================================================

def convert_numeric_columns(
    dataframe,
    columns
):

    for column in columns:

        if column in dataframe.columns:

            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce"
            ).fillna(0)

    return dataframe


def numeric_value(value):

    if pd.isna(value):
        return 0.0

    return float(value)


def format_currency(value):

    return f"₹{numeric_value(value):,.0f}"


def format_number(value):

    return f"{numeric_value(value):,.0f}"


def format_percentage(value):

    return f"{numeric_value(value):,.2f}%"


# =========================================================
# PLOTLY THEME HELPER
# =========================================================

def apply_ivory_theme(
    figure,
    height=520,
    legend_title=""
):

    figure.update_layout(
        height=height,
        template="plotly_dark",

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color=IVORY,
            family="Arial",
            size=13
        ),

        title=dict(
            font=dict(
                color=IVORY,
                size=21,
                family="Arial"
            ),
            x=0.01,
            xanchor="left"
        ),

        legend=dict(
            font=dict(
                color=IVORY,
                size=12
            ),

            title=dict(
                text=legend_title,
                font=dict(
                    color=IVORY,
                    size=13
                )
            ),

            bgcolor="rgba(7,20,38,0.40)",
            bordercolor="rgba(255,255,240,0.15)",
            borderwidth=1
        ),

        xaxis=dict(
            title_font=dict(
                color=IVORY,
                size=14
            ),

            tickfont=dict(
                color=IVORY,
                size=12
            ),

            gridcolor="rgba(255,255,240,0.10)",
            zerolinecolor="rgba(255,255,240,0.18)",
            linecolor="rgba(255,255,240,0.20)"
        ),

        yaxis=dict(
            title_font=dict(
                color=IVORY,
                size=14
            ),

            tickfont=dict(
                color=IVORY,
                size=12
            ),

            gridcolor="rgba(255,255,240,0.10)",
            zerolinecolor="rgba(255,255,240,0.18)",
            linecolor="rgba(255,255,240,0.20)"
        ),

        hoverlabel=dict(
            bgcolor=SECONDARY_NAVY,
            bordercolor=IVORY,
            font=dict(
                color=IVORY,
                size=13
            )
        ),

        margin=dict(
            l=30,
            r=30,
            t=70,
            b=40
        )
    )

    return figure


# =========================================================
# HEADER
# =========================================================

st.title(
    "Retail Sales Intelligence"
)

st.caption(
    "Animated Databricks Lakehouse Sales Analytics"
)


# =========================================================
# LOAD GOLD DATA
# =========================================================

try:

    with st.spinner(
        "Loading Gold-layer analytics..."
    ):

        kpi_df = run_query(
            """
            SELECT
                total_orders,
                total_customers,
                total_quantity,
                gross_sales,
                discount_amount,
                net_sales,
                gross_profit,
                avg_order_value,
                profit_margin_pct,
                avg_delivery_days
            FROM retail_demo.gold.sales_kpi
            """
        )


        monthly_df = run_query(
            """
            SELECT
                MAKE_DATE(
                    order_year,
                    order_month,
                    1
                ) AS month_date,

                net_sales,
                gross_profit,
                total_orders,
                unique_customers,
                avg_order_value,
                profit_margin_pct

            FROM retail_demo.gold.monthly_sales

            ORDER BY
                order_year,
                order_month
            """
        )


        driver_df = run_query(
            """
            SELECT
                month_date,
                dimension_type,
                dimension_value,
                net_sales,
                gross_profit,
                total_orders,
                unique_customers

            FROM retail_demo.gold.monthly_sales_drivers

            WHERE dimension_value IS NOT NULL

            ORDER BY
                month_date,
                dimension_type,
                net_sales DESC
            """
        )


        product_df = run_query(
            """
            SELECT
                product_name,
                category,
                subcategory,
                brand,
                units_sold,
                net_sales,
                gross_profit,
                profit_margin_pct

            FROM retail_demo.gold.product_performance

            ORDER BY net_sales DESC

            LIMIT 15
            """
        )


        channel_df = run_query(
            """
            SELECT
                sales_channel,
                total_orders,
                unique_customers,
                units_sold,
                net_sales,
                gross_profit,
                avg_order_value,
                avg_delivery_days

            FROM retail_demo.gold.channel_performance

            ORDER BY net_sales DESC
            """
        )


        campaign_df = run_query(
            """
            SELECT
                campaign_name,
                marketing_channel,
                objective,
                budget_inr,
                total_orders,
                unique_customers,
                net_sales,
                gross_profit,
                sales_to_budget_ratio

            FROM retail_demo.gold.campaign_performance

            ORDER BY sales_to_budget_ratio DESC
            """
        )


except Exception as error:

    st.error(
        "Unable to load Gold-layer analytics."
    )

    st.exception(error)

    st.stop()


# =========================================================
# DATA PREPARATION
# =========================================================

monthly_df["month_date"] = pd.to_datetime(
    monthly_df["month_date"]
)

driver_df["month_date"] = pd.to_datetime(
    driver_df["month_date"]
)


monthly_df = convert_numeric_columns(
    monthly_df,
    [
        "net_sales",
        "gross_profit",
        "total_orders",
        "unique_customers",
        "avg_order_value",
        "profit_margin_pct"
    ]
)


driver_df = convert_numeric_columns(
    driver_df,
    [
        "net_sales",
        "gross_profit",
        "total_orders",
        "unique_customers"
    ]
)


product_df = convert_numeric_columns(
    product_df,
    [
        "units_sold",
        "net_sales",
        "gross_profit",
        "profit_margin_pct"
    ]
)


channel_df = convert_numeric_columns(
    channel_df,
    [
        "total_orders",
        "unique_customers",
        "units_sold",
        "net_sales",
        "gross_profit",
        "avg_order_value",
        "avg_delivery_days"
    ]
)


campaign_df = convert_numeric_columns(
    campaign_df,
    [
        "budget_inr",
        "total_orders",
        "unique_customers",
        "net_sales",
        "gross_profit",
        "sales_to_budget_ratio"
    ]
)


monthly_df["month_label"] = (
    monthly_df["month_date"]
    .dt.strftime("%b %Y")
)


driver_df["month_label"] = (
    driver_df["month_date"]
    .dt.strftime("%b %Y")
)


month_order = (
    monthly_df
    .sort_values("month_date")["month_label"]
    .drop_duplicates()
    .tolist()
)


# =========================================================
# EXECUTIVE KPI CARDS
# =========================================================

if not kpi_df.empty:

    kpi = kpi_df.iloc[0]


    row1_col1, row1_col2, row1_col3 = (
        st.columns(3)
    )


    with row1_col1:

        st.metric(
            label="Net Sales",
            value=format_currency(
                kpi["net_sales"]
            )
        )


    with row1_col2:

        st.metric(
            label="Gross Profit",
            value=format_currency(
                kpi["gross_profit"]
            )
        )


    with row1_col3:

        st.metric(
            label="Total Orders",
            value=format_number(
                kpi["total_orders"]
            )
        )


    row2_col1, row2_col2, row2_col3 = (
        st.columns(3)
    )


    with row2_col1:

        st.metric(
            label="Total Customers",
            value=format_number(
                kpi["total_customers"]
            )
        )


    with row2_col2:

        st.metric(
            label="Average Order Value",
            value=format_currency(
                kpi["avg_order_value"]
            )
        )


    with row2_col3:

        st.metric(
            label="Profit Margin",
            value=format_percentage(
                kpi["profit_margin_pct"]
            )
        )


st.markdown("---")


# =========================================================
# APPLICATION TABS
# =========================================================

overview_tab, momentum_tab, product_tab, campaign_tab = (
    st.tabs(
        [
            "Executive Overview",
            "Animated Sales Momentum",
            "Product & Channel Intelligence",
            "Campaign Intelligence"
        ]
    )
)


# =========================================================
# EXECUTIVE OVERVIEW
# =========================================================

with overview_tab:

    st.subheader(
        "Monthly Sales and Profit Trend"
    )


    trend_figure = go.Figure()


    trend_figure.add_trace(
        go.Scatter(
            x=monthly_df["month_date"],
            y=monthly_df["net_sales"],
            mode="lines+markers",
            name="Net Sales",

            line=dict(
                color=SKY_BLUE,
                width=3
            ),

            marker=dict(
                size=8,
                color=SKY_BLUE
            ),

            hovertemplate=(
                "%{x|%b %Y}"
                "<br>Net Sales: ₹%{y:,.0f}"
                "<extra></extra>"
            )
        )
    )


    trend_figure.add_trace(
        go.Scatter(
            x=monthly_df["month_date"],
            y=monthly_df["gross_profit"],
            mode="lines+markers",
            name="Gross Profit",

            line=dict(
                color=MINT_GREEN,
                width=3
            ),

            marker=dict(
                size=8,
                color=MINT_GREEN
            ),

            hovertemplate=(
                "%{x|%b %Y}"
                "<br>Gross Profit: ₹%{y:,.0f}"
                "<extra></extra>"
            )
        )
    )


    trend_figure = apply_ivory_theme(
        trend_figure,
        height=500
    )


    trend_figure.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount (₹)",
        legend_title="",
        hovermode="x unified"
    )


    st.plotly_chart(
        trend_figure,
        use_container_width=True
    )


    overview_left, overview_right = (
        st.columns(2)
    )


    with overview_left:

        monthly_orders_figure = px.bar(
            monthly_df,
            x="month_date",
            y="total_orders",
            title="Monthly Orders",
            color_discrete_sequence=[
                INDIGO
            ]
        )


        monthly_orders_figure = apply_ivory_theme(
            monthly_orders_figure,
            height=470
        )


        monthly_orders_figure.update_layout(
            xaxis_title="Month",
            yaxis_title="Orders",
            showlegend=False
        )


        monthly_orders_figure.update_traces(
            hovertemplate=(
                "%{x|%b %Y}"
                "<br>Orders: %{y:,.0f}"
                "<extra></extra>"
            )
        )


        st.plotly_chart(
            monthly_orders_figure,
            use_container_width=True
        )


    with overview_right:

        monthly_customer_figure = px.line(
            monthly_df,
            x="month_date",
            y="unique_customers",
            markers=True,
            title="Monthly Unique Customers",
            color_discrete_sequence=[
                LAVENDER
            ]
        )


        monthly_customer_figure = apply_ivory_theme(
            monthly_customer_figure,
            height=470
        )


        monthly_customer_figure.update_layout(
            xaxis_title="Month",
            yaxis_title="Customers",
            showlegend=False
        )


        monthly_customer_figure.update_traces(
            line=dict(
                width=3
            ),

            marker=dict(
                size=8
            ),

            hovertemplate=(
                "%{x|%b %Y}"
                "<br>Customers: %{y:,.0f}"
                "<extra></extra>"
            )
        )


        st.plotly_chart(
            monthly_customer_figure,
            use_container_width=True
        )


# =========================================================
# ANIMATED SALES MOMENTUM
# =========================================================

with momentum_tab:

    st.subheader(
        "Monthly Business Driver Race"
    )

    st.markdown(
        """
        Press Play to view how Category, Channel, or Region
        rankings change month by month.
        """
    )


    selected_dimension = st.radio(
        "Analyze monthly momentum by",
        options=[
            "Category",
            "Channel",
            "Region"
        ],
        horizontal=True
    )


    selected_driver_df = (
        driver_df[
            driver_df["dimension_type"]
            == selected_dimension
        ]
        .copy()
    )


    selected_driver_df["rank"] = (
        selected_driver_df
        .groupby("month_label")["net_sales"]
        .rank(
            method="first",
            ascending=False
        )
    )


    selected_driver_df = (
        selected_driver_df[
            selected_driver_df["rank"] <= 5
        ]
        .copy()
    )


    selected_driver_df["display_value"] = (
        selected_driver_df["net_sales"]
        .map(
            lambda value:
                f"₹{value:,.0f}"
        )
    )


    maximum_sales = (
        selected_driver_df["net_sales"].max()
        if not selected_driver_df.empty
        else 1
    )


    race_figure = px.bar(
        selected_driver_df,

        x="net_sales",
        y="dimension_value",

        color="dimension_value",

        animation_frame="month_label",
        animation_group="dimension_value",

        orientation="h",

        text="display_value",

        title=(
            f"Monthly Net Sales Momentum "
            f"by {selected_dimension}"
        ),

        labels={
            "net_sales": "Net Sales (₹)",
            "dimension_value":
                selected_dimension,
            "month_label": "Month"
        },

        category_orders={
            "month_label": month_order
        },

        range_x=[
            0,
            maximum_sales * 1.15
        ],

        color_discrete_sequence=CHART_COLORS
    )


    race_figure.update_traces(
        textposition="outside",

        textfont=dict(
            color=IVORY,
            size=13,
            family="Arial"
        ),

        cliponaxis=False,

        hovertemplate=(
            f"{selected_dimension}: "
            "%{y}"
            "<br>Net Sales: ₹%{x:,.0f}"
            "<extra></extra>"
        )
    )


    race_figure = apply_ivory_theme(
        race_figure,
        height=640
    )


    race_figure.update_layout(
        showlegend=False,

        xaxis_title="Net Sales (₹)",

        yaxis=dict(
            title=selected_dimension,

            title_font=dict(
                color=IVORY,
                size=14
            ),

            tickfont=dict(
                color=IVORY,
                size=13
            ),

            categoryorder="total ascending",

            gridcolor="rgba(255,255,240,0.05)"
        ),

        margin=dict(
            l=50,
            r=110,
            t=80,
            b=60
        )
    )


    if race_figure.layout.updatemenus:

        race_figure.layout.updatemenus[
            0
        ].font = dict(
            color=IVORY
        )

        race_figure.layout.updatemenus[
            0
        ].bgcolor = PANEL_NAVY

        race_figure.layout.updatemenus[
            0
        ].bordercolor = IVORY


        race_figure.layout.updatemenus[
            0
        ].buttons[0].args[1][
            "frame"
        ]["duration"] = 1200


        race_figure.layout.updatemenus[
            0
        ].buttons[0].args[1][
            "transition"
        ]["duration"] = 700


    if race_figure.layout.sliders:

        race_figure.layout.sliders[
            0
        ].font = dict(
            color=IVORY
        )


        race_figure.layout.sliders[
            0
        ].currentvalue = dict(
            prefix="Month: ",

            font=dict(
                color=IVORY,
                size=15
            )
        )


        race_figure.layout.sliders[
            0
        ].activebgcolor = SKY_BLUE


        race_figure.layout.sliders[
            0
        ].bordercolor = IVORY


    st.plotly_chart(
        race_figure,
        use_container_width=True
    )


    st.info(
        "Use Play/Pause underneath the chart to control the "
        "animation. Switch between Category, Channel, and "
        "Region using the selector."
    )


# =========================================================
# PRODUCT AND CHANNEL INTELLIGENCE
# =========================================================

with product_tab:

    product_left, product_right = (
        st.columns(2)
    )


    with product_left:

        st.subheader(
            "Top Products by Net Sales"
        )


        top_products_figure = px.bar(
            product_df.head(10),

            x="net_sales",
            y="product_name",

            color="category",

            orientation="h",

            labels={
                "net_sales": "Net Sales (₹)",
                "product_name": "Product"
            },

            color_discrete_sequence=CHART_COLORS
        )


        top_products_figure = apply_ivory_theme(
            top_products_figure,
            height=580,
            legend_title="Category"
        )


        top_products_figure.update_layout(
            yaxis=dict(
                title="Product",

                title_font=dict(
                    color=IVORY
                ),

                tickfont=dict(
                    color=IVORY,
                    size=11
                ),

                categoryorder="total ascending"
            ),

            xaxis_title="Net Sales (₹)"
        )


        top_products_figure.update_traces(
            hovertemplate=(
                "Product: %{y}"
                "<br>Net Sales: ₹%{x:,.0f}"
                "<extra></extra>"
            )
        )


        st.plotly_chart(
            top_products_figure,
            use_container_width=True
        )


    with product_right:

        st.subheader(
            "Channel Performance"
        )


        channel_figure = px.scatter(
            channel_df,

            x="avg_order_value",
            y="gross_profit",

            size="net_sales",

            color="sales_channel",

            hover_name="sales_channel",

            labels={
                "avg_order_value":
                    "Average Order Value (₹)",
                "gross_profit":
                    "Gross Profit (₹)",
                "net_sales":
                    "Net Sales"
            },

            color_discrete_sequence=CHART_COLORS,

            size_max=65
        )


        channel_figure = apply_ivory_theme(
            channel_figure,
            height=580,
            legend_title="Sales Channel"
        )


        st.plotly_chart(
            channel_figure,
            use_container_width=True
        )


    st.subheader(
        "Product Performance Detail"
    )


    st.dataframe(
        product_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# CAMPAIGN INTELLIGENCE
# =========================================================

with campaign_tab:

    st.subheader(
        "Campaign Sales Relative to Budget"
    )


    campaign_figure = px.scatter(
        campaign_df,

        x="budget_inr",
        y="net_sales",

        size="gross_profit",

        color="marketing_channel",

        hover_name="campaign_name",

        hover_data={
            "objective": True,
            "sales_to_budget_ratio": ":.2f",
            "total_orders": True,
            "unique_customers": True
        },

        labels={
            "budget_inr":
                "Campaign Budget (₹)",
            "net_sales":
                "Net Sales (₹)",
            "gross_profit":
                "Gross Profit"
        },

        color_discrete_sequence=CHART_COLORS,

        size_max=70
    )


    campaign_figure = apply_ivory_theme(
        campaign_figure,
        height=620,
        legend_title="Marketing Channel"
    )


    st.plotly_chart(
        campaign_figure,
        use_container_width=True
    )


    st.caption(
        "Sales-to-Budget Ratio represents Net Sales divided "
        "by Campaign Budget. It is not presented as marketing ROI."
    )


    st.dataframe(
        campaign_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    f"""
    <div style="
        color: {IVORY};
        font-size: 13px;
        text-align: center;
        padding: 12px;
    ">
        Powered by Databricks Auto Loader, Delta Lake,
        Unity Catalog, Medallion Architecture and Streamlit.
    </div>
    """,
    unsafe_allow_html=True
)