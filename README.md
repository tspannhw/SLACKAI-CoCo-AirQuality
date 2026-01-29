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

## Run

<img width="2190" height="1245" alt="image" src="https://github.com/user-attachments/assets/403ccf28-a6f5-4c43-bad0-31336d943bf5" />

<img width="2223" height="1209" alt="image" src="https://github.com/user-attachments/assets/daddc8aa-ba28-431f-9a34-b68e8ecef53b" />

<img width="2188" height="1253" alt="image" src="https://github.com/user-attachments/assets/77e4dd3f-1ca7-41f6-9ad0-3247ba0febe1" />

<img width="2203" height="1161" alt="image" src="https://github.com/user-attachments/assets/0eaacd38-4e36-41ef-b7e9-fd36d2218ad4" />



