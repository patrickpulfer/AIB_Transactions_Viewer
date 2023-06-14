from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Date, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Transactions(Base):
    __tablename__ = "transactions"
    __table_args__ = {'sqlite_autoincrement': True}

    _id = Column(Integer, primary_key=True, autoincrement = True)
    file_name = Column("file_name", String)

    account_number = Column("account_number", Integer)
    sort_code = Column("sort_code", Integer)

    transaction_date = Column("transaction_date", Date)
    atm_date = Column("atm_date", String)

    currency = Column("currency", String) #EUR
    amount = Column("amount", Float)
    balance = Column("balance", Float)

    type = Column(Enum("Credit", "Debit", "Direct Debit", "ATM"))
    card_function = Column(Enum("None", "ATM", "VDA", "VDP", "VDC"))

    receiver_name = Column('receiver_name', String)
    receiver_account = Column('receiver_account', String)

    location = Column('location', String)
    location2 = Column('location2', String)

    transaction_reference = Column('transaction_reference', String, nullable=True)


    def __init__(self, file_name, account_number, sort_code, transaction_date, atm_date, currency, amount, balance, type, card_function, receiver_name, receiver_account, location, location2, transaction_reference):
        self.file_name = file_name
        self.account_number = account_number
        self.sort_code = sort_code
        self.transaction_date = transaction_date
        self.atm_date = atm_date
        self.currency = currency
        self.amount = amount
        self.balance = balance
        self.type = type
        self.card_function = card_function
        self.receiver_name = receiver_name
        self.receiver_account = receiver_account
        self.location = location
        self.location2 = location2
        self.transaction_reference = transaction_reference




