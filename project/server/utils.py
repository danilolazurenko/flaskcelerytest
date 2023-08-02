import os
import csv
import zipfile
import requests
from project.server.constants import DOWNLOADS_DIR, BULK_SIZE, DB_NAME
from pymongo import MongoClient


def get_urls():
    """We can obtain those urls by scraping sites, but it outside of work scope."""
    return [
        'https://cwe.mitre.org/data/csv/1425.csv.zip',
        'https://cwe.mitre.org/data/csv/1344.csv.zip'
    ]


def csv_handler(filename):
    db = get_mongo_connection_to_db(DB_NAME)
    with open(filename) as f:
        reader = csv.DictReader(f)
        counter = 0
        bulk = []
        for row in reader:
            row.pop(None)
            row = {str(key): value for key, value in row.items()}
            bulk.append(row)
            counter += 1
            if counter == BULK_SIZE:
                db.sec_info.insert_many(bulk)
                bulk = []
                counter = 0

def zip_handler(filename):
    with zipfile.ZipFile(f'{DOWNLOADS_DIR}/{filename}', 'r') as zip:
        zip.extractall(f'{DOWNLOADS_DIR}')


# we do not handle what exactly is in file, what to do with info depends on business logic
file_format_handlers = {
    'csv': csv_handler,
    'zip': zip_handler  # assume that all zipped are in csv for example
}


def preprocess_downloaded_files():
    with os.scandir(DOWNLOADS_DIR) as entries:
        for entry in entries:
            file_format_handlers[entry.name.split('.')[-1]](entry.name)


def download_files():
    urls = get_urls()

    # can use asyncio here, but will not for now
    for url in urls:
        r = requests.get(url, allow_redirects=True)
        with open(f'{DOWNLOADS_DIR}/{url.split("/")[-1]}', 'wb') as f:
            f.write(r.content)


def get_mongo_connection_to_db(db_name):
    uri = (f"mongodb://"
           f"{os.environ.get('MONGO_INITDB_ROOT_USERNAME')}:"
           f"{os.environ.get('MONGO_INITDB_ROOT_PASSWORD')}@"
           f"mongodb:27017")
    db = MongoClient(uri)[db_name]
    return db
