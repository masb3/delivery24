#!/usr/bin/python
import psycopg2
import os
import pytz

from datetime import datetime, timedelta
from delivery24 import settings


DB_NAME = os.getenv('DELIVERY24_DB_NAME')
DB_USER = os.getenv('DELIVERY24_DB_USER')
DB_PASS = os.getenv('DELIVERY24_DB_PASS')
DB_HOST = os.getenv('DELIVERY24_DB_HOST')
DB_PORT = os.getenv('DELIVERY24_DB_PORT')


def connect(**params):
    """ Connect to the PostgreSQL database server """
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        return psycopg2.connect(**params)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def show_all_emails():
    conn = connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()

    cur.execute("SELECT email, created_at, email_confirmed "
                "FROM accounts_user "
                "ORDER BY created_at")
    print("The number of parts to show: ", cur.rowcount)
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def delete_unconfirmed_emails():
    conn = connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()

    delete_sql = "DELETE FROM accounts_user WHERE email_confirmed = %s AND created_at < %s;"
    time_to_delete = datetime.date(datetime.now(tz=pytz.timezone('UTC')) -
                                   timedelta(days=settings.PASSWORD_RESET_TIMEOUT_DAYS))
    cur.execute(delete_sql, (False, time_to_delete,))
    print("The number of parts to delete: ", cur.rowcount)

    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    delete_unconfirmed_emails()
