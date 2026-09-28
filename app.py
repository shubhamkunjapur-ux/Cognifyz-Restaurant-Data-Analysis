import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Cognifyz Restaurant Intelligence",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# PROFESSIONAL CSS
# =========================================================

st.markdown("""
<style>

/* Main App */

.block-container {
    padding-top: 1.8rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}


/* Header */

.dashboard-header {
    padding: 28px 32px;
    border-radius: 18px;
    background: linear-gradient(
        135deg,
        #0f172a 0%,
        #1e293b 50%,
        #334155 100%
    );
    margin-bottom: 25px;
}

.dashboard-title {
    font-size: 38px;
    font-weight: 800;
    color: white;
    margin-bottom: 4px;
}

.dashboard-subtitle {
    font-size: 16px;
    color: #cbd5e1;
}


/* KPI Cards */

.kpi-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 22px 18px;
    box-shadow: 0px 4px 16px rgba(15,23,42,0.06);
    min-height: 135px;
}

.kpi-label {
    color: #64748b;
    font-size: 14px;
    font-weight: 600;
}

.kpi-value {
    color: #0f172a;
    font-size: 30px;
    font-weight: 800;
    margin-top: 8px;
}

.kpi-note {
    color: #94a3b8;
    font-size: 12px;
    margin-top: 5px;
}


/* Section Heading */

.section-title {
    font-size: 24px;
    font-weight: 750;
    color: #0f172a;
    margin-top: 20px;
    margin-bottom: 4px;
}

.section-subtitle {
    color: #64748b;
    font-size: 14px;
    margin-bottom: 18px;
}


/* Insight Box */

.insight-box {
    background: #f8fafc;
    border-left: 5px solid #2563eb;
    padding: 18px 20px;
    border-radius: 10px;
    margin-top: 10px;
    margin-bottom: 20px;
}

.insight-title {
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 5px;
}

.insight-text {
    color: #475569;
    font-size: 14px;
}


/* Footer */

.footer {
    text-align: center;
    color: #94a3b8;
    padding-top: 35px;
    padding-bottom: 10px;
    font-size: 13px;
}


/* Hide Streamlit default menu/footer */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    df = pd.read_csv("Cognifyz_Dashboard_Data.csv")

    # Data cleaning for dashboard safety

    df["Cuisines"] = df["Cuisines"].fillna("Unknown")
    df["City"] = df["City"].fillna("Unknown")

    numeric_columns = [
        "Latitude",
        "Longitude",
        "Average Cost for two",
        "Price range",
        "Aggregate rating",
        "Votes"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    return df


df = load_data()


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="dashboard-header">

<div class="dashboard-title">
Restaurant Intelligence Dashboard
</div>

<div class="dashboard-subtitle">
Cognifyz Data Analysis Internship • Interactive Restaurant Analytics
</div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Dashboard Filters")

st.sidebar.caption(
    "Use the filters below to explore restaurant data interactively."
)


# CITY FILTER

city_options = sorted(
    df["City"]
    .dropna()
    .unique()
    .tolist()
)

selected_cities = st.sidebar.multiselect(
    "City",
    options=city_options,
    placeholder="Select cities"
)


# PRICE RANGE FILTER

price_options = sorted(
    df["Price range"]
    .dropna()
    .unique()
    .tolist()
)

selected_prices = st.sidebar.multiselect(
    "Price Range",
    options=price_options,
    placeholder="Select price ranges"
)


# ONLINE DELIVERY FILTER

delivery_options = (
    df["Has Online delivery"]
    .dropna()
    .unique()
    .tolist()
)

selected_delivery = st.sidebar.multiselect(
    "Online Delivery",
    options=delivery_options,
    placeholder="Select option"
)


# TABLE BOOKING FILTER

booking_options = (
    df["Has Table booking"]
    .dropna()
    .unique()
    .tolist()
)

selected_booking = st.sidebar.multiselect(
    "Table Booking",
    options=booking_options,
    placeholder="Select option"
)


# RATING FILTER

min_rating = float(
    df["Aggregate rating"].min()
)

max_rating = float(
    df["Aggregate rating"].max()
)

rating_range = st.sidebar.slider(
    "Aggregate Rating",
    min_value=min_rating,
    max_value=max_rating,
    value=(min_rating, max_rating),
    step=0.1
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()


if selected_cities:
    filtered_df = filtered_df[
        filtered_df["City"].isin(selected_cities)
    ]


if selected_prices:
    filtered_df = filtered_df[
        filtered_df["Price range"].isin(selected_prices)
    ]


if selected_delivery:
    filtered_df = filtered_df[
        filtered_df["Has Online delivery"].isin(
            selected_delivery
        )
    ]


if selected_booking:
    filtered_df = filtered_df[
        filtered_df["Has Table booking"].isin(
            selected_booking
        )
    ]


filtered_df = filtered_df[
    filtered_df["Aggregate rating"].between(
        rating_range[0],
        rating_range[1]
    )
]


# =========================================================
# EMPTY FILTER CHECK
# =========================================================

if filtered_df.empty:

    st.warning(
        "No restaurants match the selected filters. "
        "Please modify the filters."
    )

    st.stop()


# =========================================================
# SIDEBAR INFO
# =========================================================

st.sidebar.divider()

st.sidebar.metric(
    "Restaurants Displayed",
    f"{len(filtered_df):,}"
)

st.sidebar.caption(
    f"Showing {len(filtered_df):,} of {len(df):,} restaurants"
)


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_restaurants = len(filtered_df)

total_cities = filtered_df["City"].nunique()

average_rating = filtered_df[
    "Aggregate rating"
].mean()

total_votes = filtered_df[
    "Votes"
].sum()

online_delivery_percentage = (
    filtered_df[
        "Has Online delivery"
    ]
    .eq("Yes")
    .mean()
    * 100
)


# =========================================================
# KPI CARDS
# =========================================================

st.markdown(
    '<div class="section-title">Executive Overview</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Key performance indicators based on the selected filters.'
    '</div>',
    unsafe_allow_html=True
)


col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.markdown(
        f"""
        <div class="kpi-card">

        <div class="kpi-label">
        TOTAL RESTAURANTS
        </div>

        <div class="kpi-value">
        {total_restaurants:,}
        </div>

        <div class="kpi-note">
        Restaurant records
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="kpi-card">

        <div class="kpi-label">
        CITIES
        </div>

        <div class="kpi-value">
        {total_cities:,}
        </div>

        <div class="kpi-note">
        Unique locations
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="kpi-card">

        <div class="kpi-label">
        AVG. RATING
        </div>

        <div class="kpi-value">
        {average_rating:.2f}
        </div>

        <div class="kpi-note">
        Out of 5
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="kpi-card">

        <div class="kpi-label">
        ONLINE DELIVERY
        </div>

        <div class="kpi-value">
        {online_delivery_percentage:.1f}%
        </div>

        <div class="kpi-note">
        Delivery availability
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col5:

    st.markdown(
        f"""
        <div class="kpi-card">

        <div class="kpi-label">
        TOTAL VOTES
        </div>

        <div class="kpi-value">
        {total_votes:,.0f}
        </div>

        <div class="kpi-note">
        Customer engagement
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# =========================================================
# TOP CUISINES + CITY ANALYSIS
# =========================================================

st.markdown(
    '<div class="section-title">Market & Cuisine Overview</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Explore the most common cuisines and restaurant concentration by city.'
    '</div>',
    unsafe_allow_html=True
)


left, right = st.columns(2)


# TOP CUISINES

with left:

    cuisine_data = (
        filtered_df["Cuisines"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
        .head(10)
        .reset_index()
    )

    cuisine_data.columns = [
        "Cuisine",
        "Restaurants"
    ]


    fig_cuisine = px.bar(
        cuisine_data.sort_values(
            "Restaurants"
        ),
        x="Restaurants",
        y="Cuisine",
        orientation="h",
        title="Top 10 Cuisines",
        text="Restaurants"
    )

    fig_cuisine.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    fig_cuisine.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_cuisine,
        use_container_width=True
    )


# CITY ANALYSIS

with right:

    city_data = (
        filtered_df["City"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    city_data.columns = [
        "City",
        "Restaurants"
    ]


    fig_city = px.bar(
        city_data.sort_values(
            "Restaurants"
        ),
        x="Restaurants",
        y="City",
        orientation="h",
        title="Top 10 Cities by Restaurant Count",
        text="Restaurants"
    )

    fig_city.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    fig_city.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_city,
        use_container_width=True
    )


# =========================================================
# PRICE + DELIVERY
# =========================================================

st.markdown(
    '<div class="section-title">Pricing & Service Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Understand restaurant pricing patterns and online delivery performance.'
    '</div>',
    unsafe_allow_html=True
)


left, right = st.columns(2)


# PRICE RANGE

with left:

    price_data = (
        filtered_df["Price range"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    price_data.columns = [
        "Price Range",
        "Restaurants"
    ]

    price_data["Percentage"] = (
        price_data["Restaurants"]
        / price_data["Restaurants"].sum()
        * 100
    )


    fig_price = px.bar(
        price_data,
        x="Price Range",
        y="Restaurants",
        text=price_data[
            "Percentage"
        ].map(
            lambda x: f"{x:.1f}%"
        ),
        title="Price Range Distribution"
    )

    fig_price.update_layout(
        height=420
    )

    st.plotly_chart(
        fig_price,
        use_container_width=True
    )


# ONLINE DELIVERY

with right:

    delivery_rating = (
        filtered_df
        .groupby(
            "Has Online delivery",
            as_index=False
        )["Aggregate rating"]
        .mean()
    )


    fig_delivery = px.bar(
        delivery_rating,
        x="Has Online delivery",
        y="Aggregate rating",
        text_auto=".2f",
        title="Average Rating by Online Delivery",
        labels={
            "Has Online delivery":
            "Online Delivery",

            "Aggregate rating":
            "Average Rating"
        }
    )

    fig_delivery.update_layout(
        height=420
    )

    st.plotly_chart(
        fig_delivery,
        use_container_width=True
    )


# =========================================================
# RATING ANALYSIS
# =========================================================

st.markdown(
    '<div class="section-title">Restaurant Rating Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Analyze restaurant rating distribution and customer engagement.'
    '</div>',
    unsafe_allow_html=True
)


left, right = st.columns(
    [1.5, 1]
)


with left:

    fig_rating = px.histogram(
        filtered_df,
        x="Aggregate rating",
        nbins=25,
        title="Distribution of Aggregate Ratings",
        labels={
            "Aggregate rating":
            "Aggregate Rating"
        }
    )

    fig_rating.update_layout(
        height=420
    )

    st.plotly_chart(
        fig_rating,
        use_container_width=True
    )


with right:

    rating_text = (
        filtered_df["Rating text"]
        .value_counts()
        .reset_index()
    )

    rating_text.columns = [
        "Rating Category",
        "Restaurants"
    ]


    fig_rating_text = px.pie(
        rating_text,
        names="Rating Category",
        values="Restaurants",
        hole=0.55,
        title="Rating Category Distribution"
    )

    fig_rating_text.update_layout(
        height=420
    )

    st.plotly_chart(
        fig_rating_text,
        use_container_width=True
    )


# =========================================================
# CUISINE COMBINATIONS
# =========================================================

st.markdown(
    '<div class="section-title">Cuisine Combination Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Compare frequently occurring cuisine combinations and their ratings.'
    '</div>',
    unsafe_allow_html=True
)


combination_stats = (
    filtered_df
    .groupby("Cuisines")
    .agg(
        Restaurant_Count=(
            "Restaurant ID",
            "count"
        ),
        Average_Rating=(
            "Aggregate rating",
            "mean"
        )
    )
    .reset_index()
)


combination_stats = (
    combination_stats[
        combination_stats[
            "Restaurant_Count"
        ] >= 5
    ]
    .sort_values(
        "Restaurant_Count",
        ascending=False
    )
    .head(15)
)


fig_combination = px.scatter(
    combination_stats,
    x="Restaurant_Count",
    y="Average_Rating",
    size="Restaurant_Count",
    hover_name="Cuisines",
    title=(
        "Cuisine Combination: "
        "Popularity vs Average Rating"
    ),
    labels={
        "Restaurant_Count":
        "Number of Restaurants",

        "Average_Rating":
        "Average Rating"
    }
)

fig_combination.update_layout(
    height=500
)

st.plotly_chart(
    fig_combination,
    use_container_width=True
)


# =========================================================
# GEOGRAPHIC ANALYSIS
# =========================================================

st.markdown(
    '<div class="section-title">Geographic Restaurant Distribution</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Interactive map showing restaurant locations using latitude and longitude.'
    '</div>',
    unsafe_allow_html=True
)


geo_df = filtered_df.dropna(
    subset=[
        "Latitude",
        "Longitude"
    ]
).copy()


# Remove invalid zero coordinates

geo_df = geo_df[
    (geo_df["Latitude"] != 0)
    &
    (geo_df["Longitude"] != 0)
]


if not geo_df.empty:

    fig_map = px.scatter_map(
        geo_df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Restaurant Name",
        hover_data={
            "City": True,
            "Cuisines": True,
            "Aggregate rating": True,
            "Votes": True,
            "Latitude": False,
            "Longitude": False
        },
        color="Aggregate rating",
        size="Votes",
        size_max=14,
        zoom=1,
        height=600,
        map_style="carto-positron"
    )


    fig_map.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=30,
            b=0
        )
    )


    st.plotly_chart(
        fig_map,
        use_container_width=True
    )

else:

    st.info(
        "No valid geographic coordinates "
        "are available for the selected filters."
    )


# =========================================================
# RESTAURANT CHAIN ANALYSIS
# =========================================================

st.markdown(
    '<div class="section-title">Restaurant Chain Intelligence</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Compare restaurant chains based on outlet presence, ratings and popularity.'
    '</div>',
    unsafe_allow_html=True
)


restaurant_frequency = (
    filtered_df[
        "Restaurant Name"
    ]
    .value_counts()
)


chain_names = restaurant_frequency[
    restaurant_frequency > 1
].index


chain_df = filtered_df[
    filtered_df[
        "Restaurant Name"
    ].isin(chain_names)
]


chain_stats = (
    chain_df
    .groupby(
        "Restaurant Name"
    )
    .agg(
        Outlets=(
            "Restaurant ID",
            "count"
        ),
        Average_Rating=(
            "Aggregate rating",
            "mean"
        ),
        Total_Votes=(
            "Votes",
            "sum"
        )
    )
    .reset_index()
    .sort_values(
        "Outlets",
        ascending=False
    )
    .head(15)
)


if not chain_stats.empty:

    left, right = st.columns(2)


    with left:

        fig_chain = px.bar(
            chain_stats.sort_values(
                "Outlets"
            ),
            x="Outlets",
            y="Restaurant Name",
            orientation="h",
            text="Outlets",
            title="Top Restaurant Chains by Outlets"
        )

        fig_chain.update_layout(
            height=500
        )

        st.plotly_chart(
            fig_chain,
            use_container_width=True
        )


    with right:

        fig_chain_rating = px.scatter(
            chain_stats,
            x="Average_Rating",
            y="Total_Votes",
            size="Outlets",
            hover_name="Restaurant Name",
            title="Chain Rating vs Popularity",
            labels={
                "Average_Rating":
                "Average Rating",

                "Total_Votes":
                "Total Votes"
            }
        )

        fig_chain_rating.update_layout(
            height=500
        )

        st.plotly_chart(
            fig_chain_rating,
            use_container_width=True
        )

else:

    st.info(
        "No restaurant chains are available "
        "for the selected filters."
    )


# =========================================================
# DYNAMIC INSIGHTS
# =========================================================

st.markdown(
    '<div class="section-title">Key Insights</div>',
    unsafe_allow_html=True
)


# TOP CITY

top_city = (
    filtered_df["City"]
    .value_counts()
    .idxmax()
)

top_city_count = (
    filtered_df["City"]
    .value_counts()
    .max()
)


# TOP CUISINE

exploded_cuisine = (
    filtered_df["Cuisines"]
    .str.split(",")
    .explode()
    .str.strip()
)

top_cuisine = (
    exploded_cuisine
    .value_counts()
    .idxmax()
)

top_cuisine_count = (
    exploded_cuisine
    .value_counts()
    .max()
)


# HIGHEST AVG CITY

city_rating_stats = (
    filtered_df
    .groupby("City")
    .agg(
        Restaurants=(
            "Restaurant ID",
            "count"
        ),
        Average_Rating=(
            "Aggregate rating",
            "mean"
        )
    )
)


highest_city = (
    city_rating_stats[
        "Average_Rating"
    ]
    .idxmax()
)

highest_city_rating = (
    city_rating_stats[
        "Average_Rating"
    ]
    .max()
)


st.markdown(
    f"""
    <div class="insight-box">

    <div class="insight-title">
    Dashboard Insights
    </div>

    <div class="insight-text">

    • <b>{top_city}</b> has the highest restaurant
    concentration with <b>{top_city_count:,}</b>
    restaurants under the current filters.

    <br><br>

    • <b>{top_cuisine}</b> is the most common cuisine,
    appearing in <b>{top_cuisine_count:,}</b>
    restaurant records.

    <br><br>

    • <b>{highest_city}</b> records the highest
    average rating of
    <b>{highest_city_rating:.2f}</b>.

    <br><br>

    • Restaurants in the current selection have an
    overall average rating of
    <b>{average_rating:.2f}</b>.

    </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DATA EXPLORER
# =========================================================

st.markdown(
    '<div class="section-title">Restaurant Data Explorer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Explore and download the restaurant records matching your filters.'
    '</div>',
    unsafe_allow_html=True
)


display_columns = [
    "Restaurant Name",
    "City",
    "Cuisines",
    "Average Cost for two",
    "Price range",
    "Aggregate rating",
    "Rating text",
    "Votes",
    "Has Online delivery",
    "Has Table booking"
]


available_columns = [
    col for col in display_columns
    if col in filtered_df.columns
]


st.dataframe(
    filtered_df[
        available_columns
    ].sort_values(
        "Aggregate rating",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)


# =========================================================
# DOWNLOAD DATA
# =========================================================

csv = filtered_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name="filtered_restaurant_data.csv",
    mime="text/csv"
)


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

    Cognifyz Data Analysis Internship Project
    <br>
    Developed by Shubham Maity

    </div>
    """,
    unsafe_allow_html=True
)
