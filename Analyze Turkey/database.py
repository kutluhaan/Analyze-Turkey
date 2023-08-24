"""
Host: "sql7.freesqldatabase.com"
Database_name: "sql7634014"
Database_user: "sql7634014"
Database_password: "XdXugmbeHN"
Port_number: 3306
connection_URL = "jdbc:mysql://sql7.freesqldatabase.com:3306/sql7634014"
"""

import mysql.connector
from sqlalchemy import create_engine
import pandas as pd

class Database():
    def __init__(self):
        self.host = "localhost"  # Change to 'localhost'
        self.user = "root"       # Change to your MySQL username
        self.password = ""       # Change to your MySQL password
        self.database = "cs210devam"  # Change to your MySQL database name
        self.port = 3306         # Change if your MySQL server is using a different port

        # Connect to MySQL Database
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port
        )
        self.URL = f"mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.database}"
        self.engine = create_engine(self.URL)
    
    def try_to_connect(self):
        #checks if it is connected, if not raises error
        try:
            if self.connection.is_connected():
                print("Connected to the database.")
                return True
            else:
                print("Failed to connect to the database.")
                return False
        except mysql.connector.Error as error:
            print("Error connecting to the database:", error)
            return False
        
    def create_table(self, table_name, df):
        #creates a table in a matching format with given dataframe and names it as table_name
        try:
            df.head(0).to_sql(table_name, self.engine, if_exists='fail', index=True)
            print(f"Table {table_name} created succesfully.")
        except mysql.connector.Error as error:
            print(f"Error creating table {table_name}:", error)
    
    def get_column_count(self, table_name):
        #gets the number of columns of a table
        
        # Create a cursor to execute SQL queries
        cursor = self.connection.cursor()

        # SQL query to get the column count for the table
        query = f"""
        SELECT COUNT(*) AS column_count
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{self.database}' AND TABLE_NAME = '{table_name}'
        """
        # Execute the query
        cursor.execute(query)
        # Fetch the result
        column_count = cursor.fetchone()[0]
        # Close the cursor and the connection
        cursor.close()
        self.connection.close()
        return column_count
    
    def get_column_names(self, table_name):
        #gets the names of the columns of a table
        
        try:
            # Create a cursor to execute SQL queries
            cursor = self.connection.cursor()
            # SQL query to get the column names for the table
            query = f"""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{self.database}' AND TABLE_NAME = '{table_name}'
            """
            # Execute the query
            cursor.execute(query)
            # Fetch all the column names
            column_names = [row[0] for row in cursor.fetchall()]
            # Close the cursor
            cursor.close()
            return column_names
        
        except mysql.connector.Error as error:
            print("Error retrieving column names:", error)
            return None
    
    def insert_data(self, table_name, df):
        #inserts a pandas dataframe table
        #be sure that there is no table with same name in database
        try:
            df.to_sql(table_name, self.engine, if_exists='append', index=True)
            print("Succesful insertion")
            return True
        except mysql.connector.Error as error:
            print("Error inserting data:", error)
            return False
        
    def delete_table(self, table_name):
        #deletes the table named as table_name
        try:
            cursor = self.connection.cursor()
            if isinstance(table_name, list):
                for table in table_name:
                    delete_query = f"DROP TABLE IF EXISTS {table}"
                    cursor.execute(delete_query)
                    self.connection.commit()
                cursor.close()
                print("All tables deleted successfully.")

            else:
                
                delete_query = f"DROP TABLE IF EXISTS {table_name}"
                cursor.execute(delete_query)
                self.connection.commit()
                cursor.close()

                print(f"Table '{table_name}' deleted successfully.")
        except mysql.connector.Error as error:
            print("Error deleting table:", error)
            
    def get_table_names(self):
        #gets all the table names and returns it as a list
        
        try:
            # Create a cursor to execute SQL queries
            cursor = self.connection.cursor()
            # SQL query to get all table names in the database
            query = f"""
            SHOW TABLES FROM {self.database}
            """
            # Execute the query
            cursor.execute(query)
            # Fetch all the table names
            table_names = [row[0] for row in cursor.fetchall()]
            # Close the cursor
            cursor.close()
            return table_names

        except mysql.connector.Error as error:
            print("Error retrieving table names:", error)
            return None

    def delete_all(self):
        #gets name of all the tables and deletes all of them
        
        try:
            # Get all table names in the database
            table_names = self.get_table_names()

            if table_names:
                # Create a cursor to execute SQL queries
                cursor = self.connection.cursor()

                # Loop through each table name and delete the table
                for table_name in table_names:
                    delete_query = f"DROP TABLE IF EXISTS {table_name}"
                    cursor.execute(delete_query)
                    self.connection.commit()

                cursor.close()
                print("All tables deleted successfully.")
            else:
                print("No tables found in the database.")
        
        except mysql.connector.Error as error:
            print("Error deleting tables:", error)
            
    def get_tables(self, table_name):
        # Retrieve all matching tables with the given name as a list of DataFrames
        try:
            query = f"SHOW TABLES LIKE '{table_name}'"
            cursor = self.connection.cursor()
            cursor.execute(query)
            table_names = [row[0] for row in cursor.fetchall()]
            cursor.close()

            if table_names:
                dfs = []
                for name in table_names:
                    df = self.get_table_dataframe(name)
                    if df is not None:
                        dfs.append(df)
                    else:
                        print(f"Failed to retrieve data for table '{name}'.")
                return dfs
            else:
                print(f"No tables found with name '{table_name}'.")
                return None
        except mysql.connector.Error as error:
            print("Error retrieving matching tables:", error)
            return None
        
    def show_content(self, table_name):
        # Display the content of the table in a proper format
        try:
            # Retrieve the table data as a pandas dataframe
            df = self.get_table_dataframe(table_name)
            
            if df is not None:
                print(f"Content of table '{table_name}':")
                print(df)
            else:
                print(f"Table '{table_name}' not found.")
        except mysql.connector.Error as error:
            print("Error retrieving table content:", error)