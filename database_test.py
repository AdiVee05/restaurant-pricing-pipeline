from sqlalchemy import create_engine
# engine = create_engine("sqlite://", echo=True) 
# only for a random SQL Lite Server

engine = create_engine("mssql+pyodbc://adityav:########@adityavserver.database.windows.net/free-sql-db-6841086?driver=ODBC+Driver+18+for+SQL+Server")
with engine.connect() as conn:
    print("Connection!")