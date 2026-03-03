import requests
import pandas as pd

def get_eia_inventory_data(api_key):
    print("Fetching real EIA Inventory data...")
    
    url = "https://api.eia.gov/v2/petroleum/stoc/wstk/data/"
    
    params = {"api_key": api_key,
              "frequency": "weekly",
              "data[0]": "value",
              "facets[series][]": "WCRSTUS1",
              "sort[0][column]": "period",
              "sort[0][direction]": "desc"}
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"API Error: {response.text}")
        
    raw_json = response.json()
    
    records = raw_json.get('response', {}).get('data', [])
    
    eia_df = pd.DataFrame(records)
    
    eia_df = eia_df[['period', 'value']].copy()
    eia_df.rename(columns={'period': 'Date', 'value': 'inventory_barrels'}, inplace=True)
    
    eia_df['Date'] = pd.to_datetime(eia_df['Date'])
    eia_df.sort_values('Date', inplace=True)
    
    eia_df['inventory_barrels'] = pd.to_numeric(eia_df['inventory_barrels'])

    eia_df['inventory_change'] = eia_df['inventory_barrels'].diff()
    
    return eia_df

if __name__ == "__main__":

    my_api_key = "place your own eia api key here" 
    
    try:
        df = get_eia_inventory_data(my_api_key)
        print("Here is the latest EIA data:")
        print(df.tail())
    except Exception as e:
        print(f"Failed to fetch data: {e}")