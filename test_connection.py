
import getpass
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

password = getpass.getpass("Enter your PostgreSQL password: ")

url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password=password,
    host="localhost",
    port=5432,
    database="olist_review",
)

try:
    engine = create_engine(url)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        print("\nConnection successful!")
        print(result.scalar())

except Exception as error:
    print("\nConnection failed.")
    print(error)
