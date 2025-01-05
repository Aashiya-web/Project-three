# Crime Data Ingestion Pipeline

## Overview
This project is designed to ingest crime data from an Excel file and insert it into a MySQL database. The process involves connecting to a database, creating the necessary table (if it does not already exist), loading and cleaning the data, and finally inserting it into the database in batch mode.

```

## Requirements
- Python 3.x
- MySQL Database
- Required Python Packages:
  - pandas
  - pymysql
  - SQLAlchemy
  - openpyxl

Install required packages using:
```
pip install pandas pymysql sqlalchemy openpyxl
```

## Configuration
The database connection settings are retrieved from environment variables.

### Environment Variables:
- `DB_USERNAME` (default: `root`)
- `DB_PASSWORD` (default: `root`)
- `DB_HOST` (default: `localhost`)
- `DB_PORT` (default: `3306`)
- `DB_NAME` (default: `crime_data`)

To set these, run:
```
export DB_USERNAME=myuser
export DB_PASSWORD=mypassword
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=crime_data
```

## How It Works
### 1. Database Connection
The script connects to the MySQL database using SQLAlchemy and pymysql.

### 2. Table Creation
A table named `incident_reports` is created if it does not already exist. The schema includes fields for case ID, report date, location, incident type, description, arrest status, domestic incident, coordinates, and year.

### 3. Data Loading
An Excel file (e.g., `Crime_Data.xlsx`) is loaded using pandas. The script checks for required columns and loads the first five rows.

### 4. Data Cleaning
- Dates are converted to the proper format.
- Missing coordinates (`X Coordinate`, `Y Coordinate`) are filled with the median.
- Incident types are capitalized.
- Invalid latitude and longitude values are filtered out.
- Duplicate rows (based on ID) are dropped.

### 5. Data Insertion
Data is inserted into the MySQL table in batch mode to optimize performance.

## Running the Script
Ensure the database and environment variables are set up. Place the Excel file (`Crime_Data.xlsx`) in the project directory, then run:
```
python crime_data_pipeline.py
```

## Troubleshooting
- **Missing Columns**: Ensure the Excel file contains all required columns:
  `ID`, `Date`, `Block`, `Primary Type`, `Description`, `Arrest`, `Domestic`, `X Coordinate`, `Y Coordinate`, `Year`, `Latitude`, `Longitude`.
- **Database Connection Error**: Verify your database credentials and that MySQL is running.
- **Excel Parsing Error**: Make sure the file is in `.xlsx` format.

## Logging
The script logs important steps, including table creation, data loading, cleaning, and insertion. Logs are displayed in the console and indicate the success or failure of each stage.

## Notes
- The table schema is designed to fit common crime data fields. Modify the table creation SQL query if needed.
- Adjust the latitude and longitude validation ranges based on your dataset's geographic area.

## Author
Aashiya .Z

## License
This project is licensed under the MIT License.

