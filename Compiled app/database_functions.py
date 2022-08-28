from ast import literal_eval

import sqlite3
from sqlite3 import Error

from configparser import ConfigParser 


CFILE = "config.ini"

config = ConfigParser()

def read_config():
    global config
    config.read(CFILE)
    
def write_config():
    global config
    with open(CFILE, 'w') as f:
        config.write(f)

read_config()

# SETUP

def validate(db_file):
    conntemp = None
    conntemp = sqlite3.connect(db_file)
    cur = conntemp.cursor()
    cur.execute('SELECT name from sqlite_master where type= "table"')

def validate_table(db, table):
    cur = db.cursor()
    cur.execute('SELECT * from {}'.format(table))

def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn
    
def list_tables(conn):
    cur = conn.cursor()
    cur.execute('SELECT name from sqlite_master where type= "table"')
    rows = cur.fetchall()
    templist = []
    for i in rows:
        templist.append(i)
    return templist


# Funkcje
# Funkcje związane z wyświetleniem opcji

def print_all_col_names(db):
    read_config()
    cur = db.cursor()
    cur.execute('SELECT name FROM pragma_table_info("{}")'.format(config.get('database', 'table')))
    output_list = []
    rows = cur.fetchall()
    for i in rows:
        output_list.append(i[0])
    return(output_list)

def exclude_filters(rows):
    read_config()
    temprows = rows[:]
    filters = literal_eval(config.get('database','filters'))
    for i in filters:
        for j in range(0, len(temprows)):
            if temprows[j] == i[0]:
                temprows.pop(j)
                break
    return temprows
        
# Funkcje związane z edycją funkcji:
def db_values(db, headers):
    read_config()
    cur = db.cursor()
    row_str = ''
    for i in headers:
        row_str += (i) 
        row_str += (', ')
    row_str = row_str[:-2]
    cur.execute("SELECT {} from {}".format(row_str, config.get('database', 'table')))
    rows = cur.fetchall()
    return rows

def query_group(db, col):
    read_config()
    cur = db.cursor()
    cur.execute("SELECT {} FROM {} GROUP BY {}".format(col, config.get('database', 'table'), col))
    output_list = []
    rows = cur.fetchall()
    for i in rows:
        output_list.append(i[0])
    return(output_list)

def query_table(db, col=None):
    read_config()
    cur = db.cursor()
    filters = literal_eval(config.get('database','filters'))
    query_string = ''
    for i in range(len(filters)):
        query_string += filters[i][0]
        query_string += " = "
        try:
            filters[i][1] = int(filters[i][1])
            query_string += "{}".format(filters[i][1])
        except:
            query_string += "'{}'".format(filters[i][1])
        query_string += " AND "
    if col == None:
        if query_string == '':
            cur.execute("SELECT * from {}".format(config.get('database', 'table')))
        else:
            query_string = query_string[:-5]
            cur.execute("SELECT * from {} WHERE {}".format(config.get('database', 'table'), query_string))
    else:
        if query_string == '':
            cur.execute("SELECT {} from {}".format(col,config.get('database', 'table')))
        else:
            query_string = query_string[:-5]
            cur.execute("SELECT {} from {} WHERE {}".format(col,config.get('database', 'table'), query_string))
    rows = cur.fetchall()
    return (rows)

def query_col(db, col):
    read_config()
    cur = db.cursor()
    cur.execute("SELECT {} from {}".format(col, config.get('database', 'table')))
    rows = cur.fetchall()
    return (rows)
    
print("\nPROME: wersja alfa")