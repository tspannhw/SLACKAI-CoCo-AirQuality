# Air Quality Dashboard

Streamlit app for analyzing air quality data from the `DEMO.DEMO.AQ` table.

## Features
- Filter by state, parameter type, and AQI category
- View AQI metrics and charts
- Download filtered data as CSV

## Deploy to Snowflake Streamlit

```sql
CREATE STAGE IF NOT EXISTS DEMO.DEMO.STREAMLIT_STAGE;
```

Upload files to stage, then:

```sql
CREATE OR REPLACE STREAMLIT DEMO.DEMO.AQ_DASHBOARD
  ROOT_LOCATION = '@DEMO.DEMO.STREAMLIT_STAGE/aq-streamlit-app'
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = 'YOUR_WAREHOUSE';
```

## Local Development

```bash
streamlit run streamlit_app.py
```

Requires `~/.snowflake/connections.toml` with a `[snowflake]` connection configured.
