import re
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
    placeholders = ', '.join(['?' for _ in range(len(columns)+6)])
    with closing(sqlite3.connect("plate_exporter.db")) as connection:
        with closing(connection.cursor()) as cursor:

            cursor.execute('CREATE TABLE IF NOT EXISTS combinations (user_id INTEGER, plate INTEGER)')
            # cursor.execute('INSERT INTO combinations VALUES (0, 1)')

            cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, user_name)')
            cursor.execute('INSERT INTO users (user_name) VALUES ("nelsonivar@gmail.com")')
            
            cursor.execute('CREATE TABLE IF NOT EXISTS updates (id INTEGER PRIMARY KEY AUTOINCREMENT, date DATE, plate_id INTEGER)')
            # cursor.execute('INSERT INTO updates (plate_id) VALUES (1)')
                        
            cursor.execute(f"CREATE TABLE IF NOT EXISTS plates (id INTEGER PRIMARY KEY, base, {column_names}, RWY , current_md5, plate, path)")

            # print(len(column_names.split(',')))
            # print(len(placeholders.split(',')))
            # print(set(tuple([len(x) for x in rows])))
            # for row in rows:
            #     print(row)
            # print(f"INSERT INTO plates (id, {column_names}, current_md5, path) VALUES ({placeholders})")
            cursor.executemany(f"INSERT INTO plates (id, base, {column_names}, RWY, current_md5, plate, path) VALUES ({placeholders})", rows)
            connection.commit()

def download_plates():
    auth = init_conf()
    url = 'https://www.lfv.se/globalassets/briefingrummet/nedladdning/mil-aip-till-efb/mil-aip-filer-till-efb-wef-15-jun-2023.zip'
    with requests.get(url, stream=True, auth=auth) as r:
        with open('plates.zip', 'wb') as f:
            for chunk in r.iter_content(chunk_size=16*1024):
                f.write(chunk)

def unzip_plates():
    types = ['ILS', 'MILS', 'NDB', 'LOC', 'VAC', 'NAV', 'IAL', 'LC', 'DME', 'TILS', 'TP', 'VOR', 'TAXI', 'ARR', 'DEP']
    base_pattern = r'[A-Z]{4}\d-\d{1,2}'
    rwy_pattern = r'RWY \d{2}[A-Z]?'

    with zipfile.ZipFile('plates.zip', 'r') as zf:
        rows = []
        for path in zf.namelist():
            if path.endswith('.pdf'):
                plate = re.search(base_pattern, path).group()
                rwy = re.search(rwy_pattern, path)
                rwy = [rwy.group().split()[1]] if rwy else [0]
                with open('./bases/' + path, 'rb') as pdf:
                    digest = hashlib.file_digest(pdf, 'md5').hexdigest()
                row = [plate[:4]]+ [1 if re.findall(x, path) else 0 for x in types] + rwy + [digest, plate, path]
                rows.append(row)
        return [[i+1]+ x for i, x in enumerate(rows)], types


def main():
    # download_plates()
    rows, types = unzip_plates()
    make_db(rows, types)

if __name__ == "__main__":
    main()
