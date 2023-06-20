import hashlib
import os
import zipfile 
import requests
import sqlite3
from contextlib import closing

auth = []
with open('../config/plate_exporter.conf', 'r') as f:
    auth = f.read().splitlines()
url = 'https://www.lfv.se/globalassets/briefingrummet/nedladdning/mil-aip-till-efb/mil-aip-filer-till-efb-wef-15-jun-2023.zip'

# with requests.get(url, stream=True, auth=auth) as r:
#     with open('plates.zip', 'wb') as f:
#         for chunk in r.iter_content(chunk_size=16*1024):
#             f.write(chunk)

with zipfile.ZipFile('plates.zip', 'r') as zf:
    zf.extractall(path='./bases')
    types = ['ILS', 'MILS', 'NDB', 'LOC', 'VAC', 'NAV', 'IAL', 'LC', 'NDB',
    'DME', 'TILS', 'TP', 'VOR']
    arr = ['ARR', 'DEP']
    
    for path in zf.namelist():
        if path.endswith('/'):
            print(path.split('/')[1][-4:])
        start = path.rfind('/')
        file = path[start+1:]
        if file.endswith('.pdf'):
            data = file.split()
            t = list(set(data) & set(types))
            rwy = [x for x in data if x.isdigit() or x in arr]
            abs_path = './bases/'+path
            with open(abs_path, 'rb') as plate:
                digest = hashlib.file_digest(plate, 'md5')
            # print(digest.hexdigest())
            print(tuple(t + rwy + [digest.hexdigest()]))
            # print(data)

            


# with closing(sqlite3.connect("test.db")) as connection:
#     with closing(connection.cursor()) as cursor:
#         cursor.execute('CREATE TABLE IF NOT EXISTS combinations (user_id integer, plate integer)')
#         cursor.execute('INSERT INTO combinations VALUES (0, 1)')

#         cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, user_name)')
#         cursor.execute('INSERT INTO users (user_name) VALUES ("nelsonivar@gmail.com")')
        
#         cursor.execute('CREATE TABLE IF NOT EXISTS updates (id INTEGER PRIMARY KEY AUTOINCREMENT, date DATE, plate_id INTEGER)')
#         cursor.execute('INSERT INTO updates (plate_id) VALUES (1)')
        
#         cursor.execute('CREATE TABLE IF NOT EXISTS plates (id integer primary key, base, type, current_md5, path)')
#         for i, data in enumerate(bases_list):
#             cursor.execute("INSERT INTO plates (id, base) VALUES (?,?)", [i, data])

#         connection.commit()

# for base in bases_list:
#     os.mkdir(f'./bases/{base}')
