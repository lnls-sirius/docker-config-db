"""API server definition.

Endpoints:
    /configs -
        GET - Return all different configs types
    /stats -
        GET - Return number of documents and DB size
    /configs/<config_type>
        GET - List all non-discarded documents matching config_type
    /configs/discarded/<config_type>
        GET - List all discarded documents matching config_type
    /configs/<config_type>/<name>
        GET - Return document
        POST - Insert document. Data is passed via JSON. Discard existing
            document in case of name conflict.
        DELETE - Mark document as discarded and return its new name
    /configs/discarded/<config_type>/<name>
        GET - Return document
        POST - Mark document as non-discarded
    /configs/rename/<config_type>/<oldname>/<newname>
        POST - Rename document if newname is not being used.
"""
import logging
# import datetime
import time
import uuid
import json

from flask import Flask, request, jsonify
from flask_pymongo import PyMongo, ObjectId
import gridfs

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "config_database"
app.config["MONGO_URI"] = "mongodb://config-db:27017/config_database"

mongo = PyMongo(app)


# Taken from Flask site
class InvalidUsage(Exception):
    """Exception to issue client error with messages."""

    stscode = 400

    def __init__(self, message, stscode=None, payload=None):
        """Sub class exception."""
        Exception.__init__(self)
        self.message = message
        if stscode is not None:
            self.stscode = stscode
        self.payload = payload

    def to_dict(self):
        """Return a dict with info on error."""
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Return json message with error info."""
    response = jsonify(error.to_dict())
    response.stscode = error.stscode
    return jsonify({"code": error.stscode, "message": error.message})


# ############## Endpoints ###############

@app.route('/')
@app.route("/configs")
def configtypes():
    """Return config types."""
    if request.method != "GET":
        raise InvalidUsage("Forbidden method", stscode=400)
    result = get_configsinfo(dict())
    result = list({res['config_type'] for res in result})
    return _create_ok_message(result)


@app.route("/stats")
def database_info():
    """Return collection size."""
    if request.method != "GET":
        raise InvalidUsage(
            "Endpoint does not support {} action".format(request.method),
            stscode=400)
    return _create_ok_message({
        'size': mongo.db.command("dbStats")["dataSize"],
        'count': len(get_configsinfo(dict()))})


@app.route('/configs/discarded/<string:config_type>')
@app.route("/configs/<string:config_type>")
def configsinfo(config_type):
    """Return config types."""
    if request.method != "GET":
        raise InvalidUsage(
            'Forbidden method: {}'.format(request.method), stscode=400)
    data = request.get_json() or dict()
    data['config_type'] = config_type
    data['discarded'] = '/discarded/' in request.path
    result = get_configsinfo(data)
    return _create_ok_message(result)


@app.route(
    "/configs/<string:config_type>/<string:name>",
    methods=["GET", "POST", "DELETE"])
def oneconfig(config_type, name):
    """Endpoint to get a document in the configs collection."""
    if request.method == "GET":
        result = get_one_config(config_type, name)
    elif request.method == "POST":
        data = request.get_json()
        if data is None:
            raise InvalidUsage("No data sent", stscode=400)
        result = insert_one_config(config_type, name, data)
    elif request.method == "DELETE":
        result = discard_one_config(config_type, name)
    else:
        raise InvalidUsage(
            "Endpoint does not support {} action".format(request.method),
            stscode=400)

    return _create_ok_message(result)


@app.route(
    "/configs/rename/<string:config_type>/<string:oldname>/<string:newname>",
    methods=["POST", ])
def oneconfig_rename(config_type, oldname, newname):
    """Endpoint to get a document in the configs collection."""
    if request.method == "POST":
        result = rename_one_config(config_type, oldname, newname)
        return _create_ok_message(result)

    raise InvalidUsage(
        "Endpoint does not support {} action".format(request.method),
        stscode=400)


@app.route(
    "/configs/discarded/<string:config_type>/<string:name>",
    methods=["GET", "POST"])
def oneconfig_discarded(config_type, name):
    """Endpoint to get a document in the configs collection."""
    if request.method == "GET":
        result = get_one_config(config_type, name, discarded=True)
    elif request.method == "POST":
        result = retrieve_one_config(config_type, name)
    else:
        raise InvalidUsage(
            "Endpoint does not support {} action".format(request.method),
            stscode=400)

    return _create_ok_message(result)


# ####### Lists collection db functions #########

def get_configsinfo(data, projection=None):
    """Return config documents."""
    if projection is None:
        projection = {
            "name": True, "config_type": True,
            "created": True, "modified": True, 'discarded': True}
    projection['_id'] = False
    results = _query_configs(data, projection)
    return list(results)


def get_one_config(config_type, name, discarded=False):
    """Return a document from the lists collection."""
    result = _find_config(config_type, name, discarded)
    result.pop('_id')
    fs = gridfs.GridFS(mongo.db)
    result['value'] = json.loads(fs.get(ObjectId(result['value'])).read())
    return result


def discard_one_config(config_type, name, silent=False):
    """Mark a document in the lists collection as discarded."""
    result = _find_config(config_type, name, False, silent=silent)
    name_discarded = ''
    if result:
        name_discarded = _get_discarded_name(name)
        _update_config(result['_id'], name_discarded, discarded=True)
    return name_discarded


def insert_one_config(config_type, name, value):
    """Insert new document in the lists collection."""
    ret = discard_one_config(config_type, name, silent=True)

    timestamp = _getDate()
    data = dict(
        config_type=config_type,
        name=name,
        created=timestamp,
        modified=[timestamp, ],
        discarded=False)
    try:
        data['value'] = _create_file(value)
        mongo.db.configs.insert_one(data)
    except Exception as e:
        raise InvalidUsage("{}".format(e), stscode=409)

    return ret


def rename_one_config(config_type, oldname, newname):
    if _find_config(config_type, newname, False, silent=True):
        raise InvalidUsage("Name already in use.", stscode=409)
    result = _find_config(config_type, oldname, False)
    return _update_config(result['_id'], newname, discarded=False)


def retrieve_one_config(config_type, name):
    result = _find_config(config_type, name, True)
    return _update_config(result['_id'], name, discarded=False)


# ################# Helpers #######################

def _update_config(id, new_name, discarded=True):
    """Update a document in the lists collection."""
    id = _get_object_id(id)
    try:
        data = dict(discarded=discarded, name=new_name)
        result = mongo.db.configs.update_one(
            {"_id": id}, {"$set": data, "$push": {"modified": _getDate()}})
    except Exception as e:
        raise InvalidUsage("{}".format(e), stscode=409)
    else:
        return result.modified_count


def _find_config(config_type, name, discarded, silent=False):
    try:
        data = dict(config_type=config_type, name=name, discarded=discarded)
        res = mongo.db.configs.find_one(data)
    except Exception as e:
        raise InvalidUsage("{}".format(e), stscode=409)

    if not silent and not res:
        raise InvalidUsage("Configuration not found", stscode=404)
    return res


def _query_configs(data, projection={}):
    """Return configs document."""
    try:
        return mongo.db.configs.find(data, projection)
    except Exception as e:
        raise InvalidUsage("{}".format(e), stscode=404)


def _create_file(value):
    fs = gridfs.GridFS(mongo.db)
    file_id = fs.put(json.dumps(value).encode())
    return str(file_id)


def _get_discarded_name(name):
    try:
        test = uuid.UUID(name[-36:])
    except:
        return name + '_' + str(uuid.uuid4())

    if test != name[-36:]:
        return name + '_' + str(uuid.uuid4())
    return name


def _get_object_id(id):
    if isinstance(id, ObjectId):
        return id
    try:
        return ObjectId(id)
    except Exception as e:
        raise InvalidUsage("Invalid ID", stscode=400)


def _create_ok_message(result):
    return jsonify(
        {"code": 200, "message": "ok", "result": result})


def _getDate():
    return time.time()
    # return datetime.datetime.utcnow()


# ################# NOT USED #######################

def deleteConfig(id):
    """Delete a document in the lists collection."""
    try:
        result = mongo.db.configs.delete_one({"_id": id})
    except Exception as e:
        raise InvalidUsage("{}".format(e), stscode=400)
    else:
        return jsonify(
            {"result": result.deleted_count, "code": 200, "message": "ok"})


def get_configtypes():
    """Return config types."""
    try:
        results = mongo.db.configs.aggregate([
            {
                "$group": {
                    "_id": "null",
                    "config_type": {
                        "$addToSet": "$config_type"}
                }
            }
        ])
    except Exception as e:
        raise InvalidUsage("{}".format(e), stscode=404)
    results = list(results)
    if results:
        return results[0]["config_type"]
    else:
        return []


def get_confignames(config_type):
    """Return config names."""
    try:
        results = mongo.db.configs.aggregate([
            {
                "$match": {
                    "config_type": config_type,
                    "discarded": False}
            },
            {
                "$group": {
                    "_id": "null",
                    "names": {
                        "$addToSet": "$name"}
                }
            }
        ])
    except Exception as e:
        raise InvalidUsage("{}".format(e), stscode=404)
    results = list(results)
    if results:
        return results[0]["names"]
    else:
        return []


def _parseTimestamps():
    pass


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
