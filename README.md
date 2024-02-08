# capstone-poc
Barebones proof-of-concept for capstone project
## Features
- Main.py with commandline usage and options for cronjob
- Utilizes Google Maps, Vision, and Places API to information.
- BeautifulSoup4 for webscraping.
- Google VertexAI to get descriptions of photos
- Microsoft SQL Server integration (or Azure, similar Syntax)
## TO-DO
- There is a Trello board you may request access to.
## Contacts:
- Alvin Tran | alvin.tran@louisville.edu
- J Sanders | jacob.sanders@louisville.edu
- Hoang Chau | hoang.chau@louisville.edu
- Lomus Hona | lomus.hona@louisville.edu
- Huy Le | huy.le.2@louisville.edu
- Zane Sorensen | zgsore01@louisville.edu
- Collin Shields | collin.shields@louisville.edu

## Notes on Notebooks
- `check_with_db.ipynb` - Reconciles the permit database with the triggers we find. Also to see if we can find the addresses in our permit database with Google Places API
- `files.ipynb` - Azure files testing (depricated)
- `refactor_main.ipynb` - Great Refactor of mainy.py -> store.py
- `refactor_store.ipynb` - Great Refactor of main.py -> store.py
- `store_to_db.ipynb` - `sql.py` testing environment
- 
# Setup
Please do `python -m pip install -r requirements.txt`
## Google API
1. Create a Google Cloud account
2. Create a Google Cloud project
3. Activate Cloud Vision API
4. Activate Maps APIs and get API key
5. Activate Places API
6. Activate Street View Static API
7. Create .env file and add entry with Maps API key: `MAPS_API_KEY=YOUR_API_KEY`
8. Download, install and initialize [gcloud CLI](https://cloud.google.com/sdk/gcloud) and authorize access
9. Setup virtual environment, enable virtual environment and install requirements `pip install -r requirements.txt`

## SQL.py Connection
1. in .env, add variable named ODBC_STRING = <br>
`Driver={**ODBC Driver XX for SQL Server**};Server=tcp:**server**,port;Database=**database**;Uid=**user**;Pwd=**pass**;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;`
2. Obtain ODBC_STRING from your server or service providing database (or learn to make one)
3. Open "ODBC Sources (64-bit)" on Windows, if unavailable you may need to install ODBC Drivers for SQL Server
4. Select Drivers and check what version of "ODBC Driver XY for SQL Server" is present
5. Change ODBC String to match above version.

## Database tools
Note: Using dbeaver
1. Database Dropdown -> New Database Connection -> Azure SQL SErver or SQL Server (will just autofill some information).
2. Fill out [Host], [Database/Schema], and [Authentication] feilds appropiately.
    - Information will be very similar to ODBC string above if you already have it
3. Connect
4. Please view `sql/` directory for scripts to recreate the database.

## Azure Files
Deprecated but I'm sure you can look into it if you want.
