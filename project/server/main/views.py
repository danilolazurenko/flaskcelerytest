# project/server/main/views.py


from celery.result import AsyncResult
from flask import render_template, Blueprint, jsonify, request

from project.server.tasks import download_and_preprocess_files, save_csv_to_mongo
from project.server.constants import TASK_TYPES, DB_NAME
from project.server.utils import get_mongo_connection_to_db

main_blueprint = Blueprint("main", __name__,)


@main_blueprint.route("/", methods=["GET"])
def home():
    return render_template("main/home.html")


@main_blueprint.route("/tasks", methods=["POST"])
def run_task():
    content = request.json
    task_type = content["type"]
    if task_type == TASK_TYPES['files_download']:
        task = download_and_preprocess_files.delay()
    elif task_type == TASK_TYPES['save_to_mongo']:
        task = save_csv_to_mongo.delay()
    return jsonify({"task_id": task.id}), 202


@main_blueprint.route("/tasks/<task_id>", methods=["GET"])
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return jsonify(result), 200


@main_blueprint.route("/mongo", methods=["POST"])
def search():
    content = request.json
    term = content["term"]
    db = get_mongo_connection_to_db(DB_NAME)
    result = db.sec_info.find({"$text": {"$search": term}}).limit(10)
    return jsonify(result), 200
