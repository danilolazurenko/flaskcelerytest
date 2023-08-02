import os

from celery import Celery

from project.server.constants import DOWNLOADS_DIR
from project.server.utils import (preprocess_downloaded_files,
                                  download_files,
                                  file_format_handlers)

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="save_csv_to_mongo")
def save_csv_to_mongo():
    with os.scandir(DOWNLOADS_DIR) as entries:
        for entry in entries:
            if entry.name.split('.')[-1] == 'csv':
                file_format_handlers['csv'](f'{DOWNLOADS_DIR}/{entry.name}')
    return True


@celery.task(name="download_and_preprocess")
def download_and_preprocess_files():
    download_files()
    preprocess_downloaded_files()

    return True
