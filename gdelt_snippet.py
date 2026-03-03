import pandas as pd
from google.cloud import bigquery
import os
from datetime import datetime

def get_gdelt_conflict_score(key_path, start_date='20220101', end_date=None):
    print("Connecting to Google BigQuery for GDELT data")

    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path

    client = bigquery.Client()

    query = f"""
        SELECT
            SQLDATE as date_int,
            COUNT(*) as violence_count
        FROM
            `gdelt-bq.full.events`
        WHERE
            SQLDATE BETWEEN {start_date} AND {end_date}
            AND EventRootCode IN ('18', '19', '20') 
            AND ActionGeo_CountryCode IN ('RS', 'UP', 'IR', 'IZ', 'SA', 'SY', 'IS') 
        GROUP BY
            SQLDATE
        ORDER BY
            SQLDATE
    """

    print("Scanning global news databases (won't take too long!)")
    query_job = client.query(query)
    gdelt_df = query_job.to_dataframe()

    gdelt_df['Date'] = pd.to_datetime(gdelt_df['date_int'].astype(str), format='%Y%m%d')
    
    min_val = gdelt_df['violence_count'].min()
    max_val = gdelt_df['violence_count'].max()
    
    gdelt_df['conflict_score'] = (gdelt_df['violence_count'] - min_val) / (max_val - min_val)
    
    gdelt_df = gdelt_df[['Date', 'conflict_score']].copy()
    
    return gdelt_df

if __name__ == "__main__":

    my_key_path = "google_key.json" 
    try:
        df = get_gdelt_conflict_score(my_key_path)
        print("\nSuccess! Here is the real geopolitical conflict data:")
        print(df.head())
    except Exception as e:
        print(f"Failed to fetch GDELT data: {e}")