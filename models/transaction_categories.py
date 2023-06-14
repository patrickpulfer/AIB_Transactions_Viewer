from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Date, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Transaction_Categories(Base):
    __tablename__ = "transaction_categories"

    id = Column("transaction_id", Integer, primary_key=True)
    import_string = Column("import_string", String) #String in CSV
    merchant = Column("date", String) #Lidl
    category = Column("category", String) #Groceries

    def __init__(self, id, import_string, merchant, category):
        self.id = id
        self.import_string = import_string
        self.merchant = merchant
        self.category = category
