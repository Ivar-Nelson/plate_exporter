import hashlib
import os
import zipfile 
import requests
import sqlite3
from contextlib import closing

def init_conf():
    with open('../config/plate_exporter.conf', 'r') as f:
        auth = f.read().splitlines()
    return auth

def make_db(rows, columns):
    column_names = ', '.join(columns)
    placeholders = ', '.join(['?' for _ in range(len(columns)+5)])
    with closing(sqlite3.connect("plate_exporter.db")) as connection:
        with closing(connection.cursor()) as cursor:

            cursor.execute('CREATE TABLE IF NOT EXISTS combinations (user_id INTEGER, plate INTEGER)')
            cursor.execute('INSERT INTO combinations VALUES (0, 1)')

            cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, user_name)')
            cursor.execute('INSERT INTO users (user_name) VALUES ("nelsonivar@gmail.com")')
            
            cursor.execute('CREATE TABLE IF NOT EXISTS updates (id INTEGER PRIMARY KEY AUTOINCREMENT, date DATE, plate_id INTEGER)')
            cursor.execute('INSERT INTO updates (plate_id) VALUES (1)')
                        
            cursor.execute(f"CREATE TABLE IF NOT EXISTS plates (id INTEGER PRIMARY KEY, base, {column_names}, RWY , current_md5, path)")

            # print(len(column_names.split(',')))
            # print(len(placeholders.split(',')))
            # print(set(tuple([len(x) for x in rows])))
            # for row in rows:
            #     print(row)
            # print(f"INSERT INTO plates (id, {column_names}, current_md5, path) VALUES ({placeholders})")
            cursor.executemany(f"INSERT INTO plates (id, base, {column_names}, RWY, current_md5, path) VALUES ({placeholders})", rows)
            connection.commit()

def download_plates():
    auth = init_conf()
    url = 'https://www.lfv.se/globalassets/briefingrummet/nedladdning/mil-aip-till-efb/mil-aip-filer-till-efb-wef-15-jun-2023.zip'
    with requests.get(url, stream=True, auth=auth) as r:
        with open('plates.zip', 'wb') as f:
            for chunk in r.iter_content(chunk_size=16*1024):
                f.write(chunk)

def unzip_plates(types):
    with zipfile.ZipFile('plates.zip', 'r') as zf:
        zf.extractall(path='./bases')
        rows = []
        for path in zf.namelist():
            if path.endswith('/'):
                base = path.split('/')[1][-4:]
            if path.endswith('.pdf'):
                file = path[path.rfind('/')+1:]
                data = file.split()
                t = list(set(data).intersection(set(types)))
                rwy = [int(x) for x in data if x.isdigit()]
                rwy = rwy if rwy else [0]
                abs_path = './bases/'+path
                with open(abs_path, 'rb') as plate:
                    digest = hashlib.file_digest(plate, 'md5').hexdigest()
                row = [base]+ [1 if x in t else 0 for x in types] + rwy + [digest, abs_path]
                rows.append(row)
        return [[i]+ x for i, x in enumerate(rows)]

def compare_hash():
    with zipfile.ZipFile('plates.zip', 'r') as zf:
        # zf.extractall(path='./temp')
        for path in zf.namelist():
            if path.endswith('.pdf'):
                b = zf.read(path)
                digest = hashlib.md5(b).hexdigest()
                print(digest)
                # file = path[path.rfind('/')+1:]



types = ['ILS', 'MILS', 'NDB', 'LOC', 'VAC', 'NAV', 'IAL', 'LC', 'DME', 'TILS', 'TP', 'VOR', 'TAXI', 'ARR', 'DEP']
rows = unzip_plates(types)
make_db(rows, types)
compare_hash()
