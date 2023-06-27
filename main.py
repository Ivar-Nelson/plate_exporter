import re
import hashlib
import os
import zipfile 
import requests
import sqlite3
from contextlib import closing
from datetime import date
import setup

def check_for_updates():
    # download_plates()
    types = ['ILS', 'MILS', 'NDB', 'LOC', 'VAC', 'NAV', 'IAL', 'LC', 'DME', 'TILS', 'TP', 'VOR', 'TAXI', 'ARR', 'DEP']
    base_pattern = r'[A-Z]{4}\d-\d{1,2}'
    rwy_pattern = r'RWY \d{2}[A-Z]?'
    changed_plates = []
    with zipfile.ZipFile('plates.zip', 'r') as zf:
        with closing(sqlite3.connect("plate_exporter.db")) as connection:
            with closing(connection.cursor()) as cursor:
                for path in zf.namelist():
                    if path.endswith('.pdf'):
                        plate = re.search(base_pattern, path).group()
                        digest = hashlib.md5(zf.read(path)).hexdigest()
                        cursor.execute(f"SELECT id, current_md5 FROM plates WHERE plate = ?", (plate,))
                        res = cursor.fetchone()
                        if not res or res[1] != digest:
                            print('something changed!')
                            insert_stmt = 'INSERT INTO updates (date, plate_id) VALUES (?,?)'
                            cursor.execute(insert_stmt, (date.today(), res[0]))
                            connection.commit()
                            zf.extract(path, path='./bases')
                            changed_plates.append(res[0])
                        else:
                            cursor.execute(f"SELECT id FROM updates WHERE plate_id = ?", (res[0],))
                            updated = cursor.fetchone()
                            if not updated:
                                print(f'first occurence of {res[0]}')
                                insert_stmt = 'INSERT INTO updates (date, plate_id) VALUES (?,?)'
                                cursor.execute(insert_stmt, (date.today(), res[0]))
                                connection.commit()
    return changed_plates



def main():
    types = ['ILS', 'MILS', 'NDB', 'LOC', 'VAC', 'NAV', 'IAL', 'LC', 'DME', 'TILS', 'TP', 'VOR', 'TAXI', 'ARR', 'DEP']
    check_for_updates()





if __name__ == '__main__':
    main()
