import sys
from datetime import datetime
import sqlalchemy
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Date, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import text


import models.transactions


class Database_Service():

    session = ''
    engine = ''

    def __init__(self, engine, session):
        self.engine = engine
        self.session = session

        #Base = declarative_base()
        
        #engine = create_engine("sqlite:///database.db", echo=True, connect_args={'check_same_thread':False}, poolclass=StaticPool)
        #Base.metadata.create_all(bind=engine)



    def add_from_transaction_file(self, dictionary):
        dictionary = dictionary
        
        for key, value in dictionary.items():
            #pass
            #print(value['filename'])
            #print('transaction_reference: ', end='')
            #print(value['transaction_reference'])

            date = datetime.strptime(value['transaction_date'], '%d/%m/%Y').date()

            data_to_add = models.transactions.Transactions(
                value['file_name'],
                value['account_number'],
                value['sort_code'],
                date,
                value['atm_date'],
                value['currency'],
                value['amount'],
                value['balance'],
                value['type'],
                value['card_function'],
                value['receiver_name'],
                value['receiver_account'],
                value['location'],
                value['location2'],
                value['transaction_reference'],
            )

            self.session.add(data_to_add)
            self.session.commit()

    def get_all_transactions(self):
        model = models.transactions.Transactions
        sql = text("SELECT * from 'TRANSACTIONS'")
        results = self.session.execute(sql).all()
        return results
    
    def get_empty(self):
        model = models.transactions.Transactions
        sql = text("SELECT * from 'TRANSACTIONS'")
        results = self.session.execute(sql)
        return results
    
    def delete_all_records(self):
        model = models.transactions.Transactions
        sql = text("DELETE from 'TRANSACTIONS'")
        results = self.session.execute(sql)
        self.session.commit()
        return results