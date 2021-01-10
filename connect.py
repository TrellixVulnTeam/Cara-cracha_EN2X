# Created by Davi Soares at 09/01/2021
# Projeto: AppCaraCracha
# Feature: # Enter feature name here
# Enter feature description here

# Scenario: # Enter scenario name here
# Enter steps here

# email: davi_soares@hotmail.com
import mysql.connector
from mysql.connector import Error


def connect():
    """ Connect to MySQL database """
    conn = None
    try:
        conn = mysql.connector.connect(host='awsfromto.cdvzay4qi0q6.sa-east-1.rds.amazonaws.com',
                                       database='FromTo',
                                       user='admin',
                                       password='daviSO2309')
        if conn.is_connected():
            print('Connected to MySQL database')

    except Error as e:
        print(e)

    finally:
        if conn is not None and conn.is_connected():
            conn.close()


if __name__ == '__main__':
    connect()
