# Note: This file interfaces with Microsoft SQl
# In fall 2023, interfaced with an Azure SQL Database with goals to move it to dedicated internal Microsoft SQL Server.
#
# Note: This file interfaces with Microsoft SQl
# In fall 2023, interfaced with an Azure SQL Database with goals to move it to dedicated internal Microsoft SQL Server.
import sqlalchemy
from sqlalchemy import text
import os
import dotenv
import pandas as pd
import urllib
from store import Store
dotenv.load_dotenv()

ODBC_STRING = os.getenv('ODBC_STRING')
engine = None
conn = None
cursor = None
# Set up Function
# Needs to be ran first to intialize everything
# You could move everything here out so it is ran when imported, but I have a thing for it
def set_up() -> None:
    global engine
    global conn
    global cursor
    quoted = urllib.parse.quote_plus(ODBC_STRING)
    engine = sqlalchemy.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted)) # oroginal from pyodbc, but need to format string in sqlalchemy way. See stackoverflwo for why its broken.
    conn = engine.connect()

# Query database and return respective table as a pandas dataframe.    
def query(query_string: str) -> pd.DataFrame:
    if not engine:
        raise Exception("Engine is Null, please use set_up()")
    return pd.read_sql(query_string, engine)


# Given Store Data, we save infromation into our stores table in the Database
# If the store is already present, we update, otherwise we create the store with an insert (i.e, upsert)
# -> Update Date is historical due to Google TOS. Originally help meatdata like Address, Name, etc. Please see Commits for old sql.py and store_table.sql files.
def store_to_db(s: Store) -> None:
    if not engine:
        raise Exception("Engine is Null, please use set_up()")
    else:
        place = s.place
        query = f'''MERGE INTO stores
        USING ( VALUES(\'{place['place_id']}\')) AS source (place_id)
        ON stores.place_id = source.place_id
        WHEN MATCHED THEN
        UPDATE SET last_updated = GETDATE() AT TIME ZONE 'UTC'
        WHEN NOT MATCHED THEN
        INSERT (place_id)
        VALUES (\'{place['place_id']}\');'''.replace('\n',' ')
        conn.execute(text(query))
        conn.commit()
        return None

# Need Update with additional flags
# Right now working with is_triggering to set flag_text  

#Client wants microsoft sql to be used but Imam only gave us DB2 database. You may have to change this to be compatiple with the other code above.
def store_flag(s: Store) -> None:
    query = f'''
        UPDATE stores
        SET last_flagged = CURRENT_TIMESTAMP,
            flag_text = {1 if s.is_triggering else 0},
            flag_street = {1 if s.trigger_street else 0},
            flag_review_image = {1 if s.trigger_review_image else 0},
            flag_review = {1 if s.trigger_review else 0},
            flag_website = {1 if s.trigger_website else 0} 
        WHERE place_id = '{s.place['place_id']}'
    '''
    conn.execute(text(query))
    conn.commit()
set_up()


# Execute the query and fetch the results into a Pandas DataFrame
# Print the DataFrame to view the contents of the 'businesses' table
