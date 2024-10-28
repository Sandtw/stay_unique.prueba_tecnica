import os

from resources.scraper import scrap_airbnb
from resources.etl import etl_booking, etl_properties_owner, etl_properties_competitor, create_dataset_if_not_exists, send_to_bigquery

url_bookings = 'data/Bookings.csv'
url_prop_scrap = 'data/properties_scrapping.csv'
url_prop = 'data/properties.csv'
bigquery_db = 'bd_stay_unique'


if __name__ == "__main__":

    if not os.path.exists(url_prop_scrap):
       scrap_airbnb('EUR', 'Barcelona', 'España')
    etl_properties_owner(url_prop)
    etl_properties_competitor(url_prop_scrap)
    etl_booking(url_bookings, save_mysql=False)
