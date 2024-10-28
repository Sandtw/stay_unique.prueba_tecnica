from decouple import config
import pandas as pd

from config.database import Database



db = Database(host=config('SERVER_MYSQL'),
              user=config('USERNAME_MYSQL'),
              password=config('PASSWORD_MYSQL'),
              db=config('DATABASE_MYSQL'))

def insert_properties_owner(properties: list):
    query = """
        INSERT INTO properties_owner VALUES (%s, %s, %s, %s, %s)
    """
    db.insert_many(query, properties)

def insert_properties_competitor(properties:list):
    query = f"""
    INSERT INTO properties_competitor VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    db.insert_many(query, properties)

def insert_booking(bookings: list):
    query = """
    INSERT INTO booking VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    db.insert_many(query, bookings)

def export_to_csv(list_properties:list):
    df = pd.DataFrame(list_properties, columns=['property_id', 'property_name', 'reference_rate_night', 'rating', 'n_reviews', 'city', 'country', 'property_type', 'url_property'])
    df.to_csv('data/properties_scrapping.csv', index=False)

def get_existing_property_ids():
    query = """
    SELECT property_id FROM properties_owner
    """
    results = db.find_many(query)
    existing_ids = [result['property_id'] for result in results]
    return existing_ids
