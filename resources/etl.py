import pandas as pd
import numpy as np
from google.oauth2 import service_account
from pandas_gbq import to_gbq
from google.cloud import bigquery
from decouple import config

from resources.utils import insert_booking, insert_properties_owner, insert_properties_competitor, get_existing_property_ids

def read_csv(url:str):
    return pd.read_csv(url)

def etl_booking(url:str, save_mysql:bool=False):
    rename_booking = {
            'Property_BookingId': 'booking_id',
            'BookingCreatedDate': 'created_date',
            'ArrivalDate': 'check_in_date',
            'DepartureDate': 'check_out_date',
            'NumNights': 'n_nights',
            'Adults': 'n_adults',
            'Children': 'n_children',
            'Infants': 'n_infants',
            'RoomRate': 'total_without_extras',
            'ADR': 'avg_rate_night',
            'Channel': 'channel',
            'TotalPaid': 'total_paid',
            'PropertyId': 'property_id'
    }

    try:
        # extract
        df_bookings = read_csv(url)

        # transform
        columns_booking = list(rename_booking.keys())
        dim_booking = df_bookings[columns_booking].rename(columns=rename_booking)
        cond_fmt_one = dim_booking['created_date'].str.contains(r'\d{2}/\d{2}/\d{4}', regex=True)
        dim_booking.loc[cond_fmt_one, 'created_date'] = pd.to_datetime(dim_booking[cond_fmt_one]['created_date'], format='%d/%m/%Y')

        dim_booking.loc[dim_booking['n_nights'] <= 0, 'n_nights'] = np.nan
        dim_booking.loc[dim_booking['avg_rate_night'] == 0, 'avg_rate_night'] = np.nan
        dim_booking.loc[dim_booking['total_without_extras'] == 0, 'total_without_extras'] = np.nan
        dim_booking.loc[dim_booking['channel'].isna(), 'channel'] = 'Otros'
        dim_booking['channel'] = dim_booking['channel'].str.replace(r'\..*', '', regex=True)
        dim_booking.loc[dim_booking['total_paid'] == 0, 'total_paid'] = np.nan

        dim_booking.loc[dim_booking['total_without_extras'] < 0, 'total_without_extras'] = dim_booking[dim_booking['total_without_extras'] < 0].\
            apply(lambda row: 
                np.nan if np.abs(row['total_without_extras']) < row['avg_rate_night'] else row['total_without_extras'] * -1, axis=1
                )

        dim_booking.loc[dim_booking['total_paid'] < 0, 'total_paid'] = dim_booking[dim_booking['total_paid'] < 0].\
            apply(lambda row: 
                np.nan if row['total_without_extras'] > np.abs(row['total_paid']) else row['total_paid'] * -1, axis=1
                )

        dim_booking = dim_booking.astype({'n_adults': 'int', 'n_children': 'int', 'n_infants': 'int'})
        dim_booking['channel'] = dim_booking['channel'].str.lower()
        dim_booking.fillna(-1, inplace=True)

        existing_ids = get_existing_property_ids()
        dim_booking = dim_booking[dim_booking['property_id'].isin(existing_ids)]

        # Load
        if save_mysql:
            insert_booking(dim_booking.values.tolist())
        else:
            return dim_booking
    
    except Exception as error:
        print(f"Error en la ejecución: {error}")


def etl_properties_owner(url:str, save_mysql:bool=False):
    rename_properties = {
        'PropertyId': 'property_id',
        'Capacity': 'capacity',
        'Square': 'square_mts',
        'PropertyType': 'property_type',
        'NumBedrooms': 'n_bedrooms',
    }

    mapping_type_prop = {
        'Apa': 'apartamento',
        'Apartment': 'apartamento',
        'House': 'casa'
    }

    try:
        # extract
        df_properties = read_csv(url)

        # transform

        columns_properties = list(rename_properties.keys())
        dim_properties_owner = df_properties[columns_properties].rename(columns=rename_properties)
        dim_properties_owner.loc[dim_properties_owner['property_type'].isna(), 'property_type'] = 'otros'
        dim_properties_owner.drop_duplicates(subset=['property_id'], inplace=True)
        dim_properties_owner['property_type'] = dim_properties_owner['property_type'].replace(mapping_type_prop)
        
        # Load
        if save_mysql:
            tuples = list(dim_properties_owner.itertuples(index=False, name=None))
            insert_properties_owner(tuples)
        else:
            return dim_properties_owner

    except Exception as e:
        print(str(e))


def etl_properties_competitor(url:str, save_mysql:bool=False):
    try:
        # extract
        dim_properties_competitor = read_csv(url)
        # transform
        dim_properties_competitor.drop_duplicates(subset=['property_id'], inplace=True)
        dim_properties_competitor[['property_name', 'city', 'country', 'property_type']] = dim_properties_competitor[['property_name', 'city', 'country', 'property_type']].apply(lambda x: x.str.lower())
        
        # Load
        if save_mysql:
            insert_properties_competitor(dim_properties_competitor.values.tolist())
        else:  
            return dim_properties_competitor
            
    except Exception as error:
        print(f"Error en la ejecución: {error}")


def create_dataset_if_not_exists(dataset_id: str):
    credentials = service_account.Credentials.from_service_account_file(
        config('GOOGLE_APPLICATION_CREDENTIALS')
    )
    
    client = bigquery.Client(credentials=credentials)
    dataset_ref = client.dataset(dataset_id)
    
    try:
        client.get_dataset(dataset_ref)
    except Exception as e:
        client.create_dataset(bigquery.Dataset(dataset_ref))
        
        
def send_to_bigquery(df: pd.DataFrame, table_id: str):
    credentials = service_account.Credentials.from_service_account_file(
        config('GOOGLE_APPLICATION_CREDENTIALS')
    )
    
    to_gbq(df, table_id, project_id=config('GCP_PROJECT_ID'), if_exists='replace', credentials=credentials)

