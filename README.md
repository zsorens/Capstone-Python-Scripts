# capstone-poc
Barebones proof-of-concept for capstone project
## Features
- Main.py with commandline usage and options for cronjob
- Utilizes Google Maps, Vision, and Places API to information.
- BeautifulSoup4 for webscraping.
- Google VertexAI to get descriptions of photos
- Microsoft SQL Server integration (or Azure, similar Syntax)
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
7. Generate a service account key:
    -   In the "Service accounts" page, find the service account you just created.
    -   Click on the "Actions" menu (three vertical dots) for the service account.
    -   Select "Manage keys" from the dropdown menu.
    -   Click on the "Add Key" button and select "Create new key".
    -   Choose "JSON" as the key type and click "Create".
    -   The JSON key file will be downloaded to your computer.
8. Create .env file and add entry with Maps API key: `MAPS_API_KEY=YOUR_API_KEY` and path to key json `KEY_JSON_PATH = PATH/TO/KEY`
9. Download, install and initialize [gcloud CLI](https://cloud.google.com/sdk/gcloud) and authorize access
10. Setup virtual environment, enable virtual environment and install requirements `pip install -r requirements.txt`



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

## What needs to be fixed:
1.   The UI as it stands uses a CSV to get store data. Next group you need to connect the UI directly from the database. The store_flag function in sql may need to be changed to be copatible with  Microsoft SQL Server. While we were working on this project Imam only gave us a DB2 server to work on so we had to change the code from last semester to be compatible with DB2. The client directly told us that they do not want DB2 they want Microsoft SQL. I have given you what the sql code from the group before which is in Microsoft sql but they had not implemted the store_flag function yet. So I put the new DB2 store_flag function together with the old sql.py file. You may or may not have to change the sql in that function to get it to work.

2.   There is a unused table column, flag_image, which needs to be remove. Last group added it but it is useless. I no longer have time or Google Cloud credits left to fix it. You will need to remove that colomn from the database and remove it from store_flag function as well as remove it from the UI.

3. There is a method to create a CSV without the database using -l. I cannot test it as I have no Google Cloud credits. The client should use this until the UI is connected to the database, but I cannot 100% confirm it works. If it does not, the client can still use the -sql method to get a CSV from the database.

 PS: When you create your Google Cloud account, you get $300 in free credit. You will probably need much more than this for all your testing. Try contacting the client to see if they can provide additional credits.