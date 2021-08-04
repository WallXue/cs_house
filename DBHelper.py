import os
from sqlalchemy import create_engine
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "data/house.sqlite")

engine = create_engine('sqlite:///' + db_path, echo=False)
