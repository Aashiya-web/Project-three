import pandas as pd
import pymysql
import os
from datetime import datetime
from sqlalchemy import create_engine, text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection settings (from environment variables)
DB_USERNAME = os.getenv('DB_USERNAME', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'crime_data')

# Table name change
TABLE_NAME = 'incident_reports'

# Step 1: Connect to the database
def connect_to_db():
    engine = create_engine(f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
    return engine

# Step 2: Create table if not exists
def create_table_if_not_exists(engine):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        case_id VARCHAR(50),
        report_date DATETIME,
        location_block VARCHAR(255),
        incident_type VARCHAR(100),
        incident_description TEXT,
        arrest_status TINYINT(1),
        domestic_incident TINYINT(1),
        x_coord FLOAT,
        y_coord FLOAT,
        report_year INT,
        latitude DECIMAL(9,6),
        longitude DECIMAL(9,6)
    );
    """
    with engine.connect() as conn:
        conn.execute(text(create_table_query))
    logging.info(f"Table '{TABLE_NAME}' created or already exists.")

# Step 3: Load the Excel file (with first 5 records)
def load_excel_file(file_path):
    logging.info("Loading Excel file...")
    required_columns = ['ID', 'Date', 'Block', 'Primary Type', 'Description', 'Arrest', 'Domestic', 'X Coordinate', 'Y Coordinate', 'Year', 'Latitude', 'Longitude']
    
    df = pd.read_excel(file_path)
    
    if not all(col in df.columns for col in required_columns):
        missing = set(required_columns) - set(df.columns)
        print(missing)
        raise ValueError(f"Missing required columns in Excel: {missing}")

    logging.info("Data Loaded Successfully!")
    logging.info(df.head())
    return df

# Step 4: Clean the data
def clean_data(df):
    logging.info("Cleaning data...")

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

    df['X Coordinate'] = df['X Coordinate'].fillna(df['X Coordinate'].median())
    df['Y Coordinate'] = df['Y Coordinate'].fillna(df['Y Coordinate'].median())
    df['Primary Type'] = df['Primary Type'].str.title()

    valid_lat = (df['Latitude'] >= 41.6445) & (df['Latitude'] <= 42.0231)
    valid_lon = (df['Longitude'] >= -87.9401) & (df['Longitude'] <= -87.5245)
    df = df[valid_lat & valid_lon]

    df = df.drop_duplicates(subset=['ID'])

    logging.info("Data Cleaning Completed!")
    logging.info(df.head())
    return df

# Step 5: Batch insert into SQL table
def insert_into_database(df):
    logging.info("Inserting data into the database...")

    columns = ['ID', 'Date', 'Block', 'Primary Type', 'Description', 'Arrest', 'Domestic', 'X Coordinate', 'Y Coordinate', 'Year', 'Latitude', 'Longitude']
    df = df[columns]

    data = df.to_records(index=False).tolist()

    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    insert_query = f"""
        INSERT INTO {TABLE_NAME} (
            case_id, report_date, location_block, incident_type, incident_description,
            arrest_status, domestic_incident, x_coord, y_coord, report_year,
            latitude, longitude
        ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    with connection.cursor() as cursor:
        cursor.executemany(insert_query, data)
        connection.commit()

    connection.close()
    logging.info("Batch data insertion completed!")

# Main execution
if __name__ == "__main__":
    engine = connect_to_db()
    create_table_if_not_exists(engine)

    file_path = 'Crime_Data.xlsx'
    df = load_excel_file(file_path)

    df = clean_data(df)

    insert_into_database(df)

    logging.info("Process completed successfully!")
