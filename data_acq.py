# data acqusition module 

import csv
from os import name
import pandas as pd 
from init import *
import sqlite3
from sqlite3 import Error
from datetime import datetime
import time as tm
from icecream import ic as ic2
import matplotlib.pyplot as plt
import random


def time_format():
    return f'{datetime.now()}  data acq|> '

ic2.configureOutput(prefix=time_format)



def create_connection(db_file=db_name):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        pp = ('Conected to version: '+ sqlite3.version)
        ic2(pp)
        return conn
    except Error as e:
        ic2(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:

        ic2(e)
        


def init_db(database):
    #database = r"data\homedata.db"    
    tables = [
    """CREATE TABLE IF NOT EXISTS `kick_sensor` (
        `timestamp` TEXT NOT NULL,
        `duration` integer NOT NULL,
        `power` integer NOT NULL
    );""",
    """CREATE TABLE IF NOT EXISTS `speed_sensor` (
        `timestamp` TEXT NOT NULL,
        `speed` integer NOT NULL
    );""",
    """CREATE TABLE IF NOT EXISTS `air_sensor` (
        `timestamp` TEXT NOT NULL,
        `psi` integer NOT NULL
    );"""
    ]

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create tables
        for table in tables:
            create_table(conn, table)
        conn.close()            
    else:
        ic2("Error! cannot create the database connection.")


def create_IOT_dev(timestamp, duration, power):
    """
    Create a new IOT device into the kick_sensor table
    :param conn:
    :param :
    :return: sys_id
    """
    sql = ''' INSERT INTO kick_sensor(timestamp, duration, power)
              VALUES(?,?,?) '''
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, [timestamp, duration, power,])
        conn.commit()
        re = cur.lastrowid
        conn.close()
        return re
    else:
        ic2("Error! cannot create the database connection.")  

    
def create_IOT_dev1(timestamp, speed):
    """
    Create a new IOT device into the speed_sensor table
    :param conn:
    :param :
    :return: sys_id
    """
    sql = ''' INSERT INTO speed_sensor(timestamp, speed)
              VALUES(?,?) '''
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, [timestamp, speed])
        conn.commit()
        re = cur.lastrowid
        conn.close()
        return re
    else:
        ic2("Error! cannot create the database connection.")   

    
def create_IOT_dev2(timestamp, psi):
    """
    Create a new IOT device into the air_sensor table
    :param conn:
    :param :
    :return: sys_id
    """
    sql = ''' INSERT INTO air_sensor(timestamp, psi)
              VALUES(?,?) '''
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, [timestamp, psi])
        conn.commit()
        re = cur.lastrowid
        conn.close()
        return re
    else:
        ic2("Error! cannot create the database connection.")   

def timestamp():
    return str(datetime.fromtimestamp(datetime.timestamp(datetime.now()))).split('.')[0]
           

def read_IOT_data(table, name):
    """
    Query tasks by name
    :param conn: the Connection object
    :param name:
    :return: selected by name rows list
    """
    
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()        
        cur.execute("SELECT * FROM " + table +" WHERE name=?", (name,))
        rows = cur.fetchall() 
       
        return rows
    else:
        ic2("Error! cannot create the database connection.")   

    

def fetch_table_data_into_df(table_name, conn):
    return pd.read_sql_query("SELECT * from " + table_name, conn)

def filter_by_date(table_name,start_date,end_date):
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()                
        cur.execute("SELECT * FROM " + table_name +" WHERE timestamp BETWEEN '"+ start_date +"' AND '"+ end_date +"'")
        #cur.execute("SELECT * FROM " + table_name +" WHERE timestamp BETWEEN '2023-06-11' AND '2023-06-13'")
        rows = cur.fetchall()
        print(rows)
        return rows
    else:
        ic2("Error! cannot create the database connection.")     

def fetch_data(database,table_name):
    TABLE_NAME = table_name    
    conn = create_connection(database)
    with conn:        
        return fetch_table_data_into_df(TABLE_NAME, conn)
        
def show_graph(meter, date):
    df = fetch_data(db_name,'data', meter)       
    #df.timestamp=pd.to_numeric(df.timestamp)
    df.value=pd.to_numeric(df.value)
    ic2(len(df.value))
    ic2(df.value[len(df.value)-1])
    ic2(max(df.value))
    ic2(df.timestamp)
    df.plot(x='timestamp',y='value')    
    # fig, axes = plt.subplots (2,1)
    # # Draw a horizontal bar graph and a vertical bar graph
    # df.plot.bar (ax = axes [0])
    # df.plot.barh (ax = axes [1])
    plt.show()


if __name__ == '__main__':
    if 1:
        init_db(db_name)
