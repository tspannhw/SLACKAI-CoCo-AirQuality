import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

st.set_page_config(
    page_title="Air Quality Dashboard",
    page_icon="🌬️",
    layout="wide"
)

AQI_THRESHOLDS = {
    "Good": (0, 50, "green"),
    "Moderate": (51, 100, "yellow"),
    "Unhealthy for Sensitive Groups": (101, 150, "orange"),
    "Unhealthy": (151, 200, "red"),
    "Very Unhealthy": (201, 300, "purple"),
    "Hazardous": (301, 500, "maroon")
}

def get_aqi_color(aqi):
    for category, (low, high, color) in AQI_THRESHOLDS.items():
        if low <= aqi <= high:
            return color
    return "gray"

def get_aqi_category(aqi):
    for category, (low, high, _) in AQI_THRESHOLDS.items():
        if low <= aqi <= high:
            return category
    return "Unknown"

st.title("🌬️ Air Quality Dashboard")

@st.cache_data(ttl=600)
def load_data():
    session = get_active_session()
    df = session.sql("SELECT * FROM DEMO.DEMO.AQ").to_pandas()
    return df

df = load_data()

with st.sidebar:
    st.header("Filters")
    
    states = sorted(df["STATECODE"].dropna().unique().tolist())
    selected_states = st.multiselect("State", states, default=states[:5] if len(states) >= 5 else states)
    
    parameters = sorted(df["PARAMETERNAME"].dropna().unique().tolist())
    selected_params = st.multiselect("Parameter", parameters, default=parameters)
    
    categories = sorted(df["CATEGORYNAME"].dropna().unique().tolist())
    selected_categories = st.multiselect("Category", categories, default=categories)
    
    st.markdown("---")
    st.header("Alert Settings")
    aqi_threshold = st.slider("AQI Alert Threshold", 0, 300, 100)
    show_alerts_only = st.checkbox("Show only alerts", value=False)

filtered_df = df[
    (df["STATECODE"].isin(selected_states)) &
    (df["PARAMETERNAME"].isin(selected_params)) &
    (df["CATEGORYNAME"].isin(selected_categories))
]

if show_alerts_only:
    filtered_df = filtered_df[filtered_df["AQI"] >= aqi_threshold]

alert_count = len(df[df["AQI"] >= aqi_threshold])
if alert_count > 0:
    st.error(f"⚠️ **{alert_count} readings** exceed AQI threshold of {aqi_threshold}")

metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
with metric_col1:
    st.metric("Total Records", len(filtered_df))
with metric_col2:
    avg_aqi = filtered_df['AQI'].mean() if len(filtered_df) > 0 else 0
    st.metric("Avg AQI", f"{avg_aqi:.1f}")
with metric_col3:
    max_aqi = int(filtered_df['AQI'].max()) if len(filtered_df) > 0 else 0
    st.metric("Max AQI", max_aqi)
with metric_col4:
    st.metric("Reporting Areas", filtered_df['REPORTINGAREA'].nunique())
with metric_col5:
    unhealthy = len(filtered_df[filtered_df["AQI"] > 100])
    st.metric("Unhealthy Readings", unhealthy)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📍 Map", "📈 Time Series", "🔄 Comparison", "📊 Charts", "📋 Data"])

with tab1:
    st.subheader("AQI by Location")
    if len(filtered_df) > 0:
        map_df = filtered_df.groupby(["REPORTINGAREA", "LATITUDE", "LONGITUDE"]).agg({
            "AQI": "mean"
        }).reset_index()
        map_df = map_df.rename(columns={"LATITUDE": "latitude", "LONGITUDE": "longitude"})
        map_df["size"] = map_df["AQI"].clip(lower=10) * 5
        
        st.map(map_df, latitude="latitude", longitude="longitude", size="size")
        
        st.caption("Bubble size represents AQI level")
    else:
        st.info("No data available for map.")

with tab2:
    st.subheader("AQI Over Time")
    if len(filtered_df) > 0 and "DATEOBSERVED" in filtered_df.columns:
        time_df = filtered_df.copy()
        time_df["DATE"] = pd.to_datetime(time_df["DATEOBSERVED"], errors="coerce")
        time_df = time_df.dropna(subset=["DATE"])
        
        if len(time_df) > 0:
            time_agg = time_df.groupby(["DATE", "PARAMETERNAME"])["AQI"].mean().reset_index()
            time_pivot = time_agg.pivot(index="DATE", columns="PARAMETERNAME", values="AQI")
            
            st.line_chart(time_pivot)
            
            st.markdown("#### Hourly Pattern")
            hourly_df = filtered_df.copy()
            hourly_df["HOUR"] = pd.to_numeric(hourly_df["HOUROBSERVED"], errors="coerce")
            hourly_agg = hourly_df.groupby("HOUR")["AQI"].mean()
            st.bar_chart(hourly_agg)
        else:
            st.info("No valid date data available.")
    else:
        st.info("No time series data available.")

with tab3:
    st.subheader("Area Comparison")
    if len(filtered_df) > 0:
        areas = sorted(filtered_df["REPORTINGAREA"].dropna().unique().tolist())
        selected_areas = st.multiselect("Select areas to compare", areas, default=areas[:5] if len(areas) >= 5 else areas, key="compare_areas")
        
        if selected_areas:
            compare_df = filtered_df[filtered_df["REPORTINGAREA"].isin(selected_areas)]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Average AQI by Area")
                area_avg = compare_df.groupby("REPORTINGAREA")["AQI"].mean().sort_values(ascending=True)
                st.bar_chart(area_avg)
            
            with col2:
                st.markdown("#### AQI Range by Area")
                area_stats = compare_df.groupby("REPORTINGAREA")["AQI"].agg(["min", "mean", "max"]).reset_index()
                area_stats.columns = ["Area", "Min", "Avg", "Max"]
                st.dataframe(area_stats, use_container_width=True, hide_index=True)
            
            st.markdown("#### Side-by-Side Comparison")
            comparison_cols = st.columns(len(selected_areas))
            for i, area in enumerate(selected_areas):
                area_data = compare_df[compare_df["REPORTINGAREA"] == area]
                with comparison_cols[i]:
                    avg = area_data["AQI"].mean()
                    st.metric(area[:15], f"{avg:.0f}")
                    category = get_aqi_category(avg)
                    color = get_aqi_color(avg)
                    st.markdown(f":{color}[{category}]")
    else:
        st.info("No data available for comparison.")

with tab4:
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Average AQI by State")
        if len(filtered_df) > 0:
            aqi_by_state = filtered_df.groupby("STATECODE")["AQI"].mean().sort_values(ascending=False).head(10)
            st.bar_chart(aqi_by_state)
        else:
            st.info("No data available.")
    
    with chart_col2:
        st.subheader("AQI Distribution by Category")
        if len(filtered_df) > 0:
            category_counts = filtered_df["CATEGORYNAME"].value_counts()
            st.bar_chart(category_counts)
        else:
            st.info("No data available.")
    
    st.subheader("Average AQI by Reporting Area (Top 15)")
    if len(filtered_df) > 0:
        aqi_by_area = filtered_df.groupby("REPORTINGAREA")["AQI"].mean().sort_values(ascending=False).head(15)
        st.bar_chart(aqi_by_area)

with tab5:
    st.subheader("Data Table")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("Search by area name", "")
    with col2:
        sort_by = st.selectbox("Sort by", ["AQI", "DATEOBSERVED", "STATECODE", "REPORTINGAREA"])
    
    display_df = filtered_df.copy()
    if search:
        display_df = display_df[display_df["REPORTINGAREA"].str.contains(search, case=False, na=False)]
    
    display_df = display_df.sort_values(sort_by, ascending=False if sort_by == "AQI" else True)
    
    def highlight_aqi(val):
        if pd.isna(val):
            return ""
        if val > 150:
            return "background-color: #ff6b6b"
        elif val > 100:
            return "background-color: #ffa502"
        elif val > 50:
            return "background-color: #ffeaa7"
        return "background-color: #55efc4"
    
    styled_df = display_df[["DATEOBSERVED", "HOUROBSERVED", "REPORTINGAREA", "STATECODE", "PARAMETERNAME", "AQI", "CATEGORYNAME"]].style.applymap(
        highlight_aqi, subset=["AQI"]
    )
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="air_quality_data.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("Data source: DEMO.DEMO.AQ | AQI thresholds based on EPA standards")
