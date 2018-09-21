"""API server definition.

Endpoints:
    /configs -
        GET - Return configs collection documents, filter can be passed
              via JSON
        POST - Insert document on configs collection, data is passed via JSON
    /configs/count -
        GET - Return number of documents matched by the find criteria passed
              via JSON
    /configs/<config>/<name>
        GET - Return document matched by config and name
    /configs/<id>
        GET - Return docuement matched by id
        PUT - Update document matched by id with parameters passed via JSON
        DELETE - Delete document matched by id
    /configs/stats/size -
        GET - Return size of configs collection in bytes
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

    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        """Sub class exception."""
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
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
    response.status_code = error.status_code
    return jsonify({"code": error.status_code, "message": error.message})


# Endpoints
@app.route("/")
# Configs collection endpoints
@app.route("/configs", methods=["GET", "POST"])
def configs():
    """Endpoint to get and insert a list."""
    if request.method == "GET":
        data = request.get_json()
        if data is None:
            return getConfigs(data={})
        else:
            return getConfigs(data)
    elif request.method == "POST":
        data = request.get_json()
        if data is None:
            raise InvalidUsage("No data sent", status_code=400)
        return insertConfig(data)


@app.route("/configs/count", methods=["GET"])
def configsCount():
    """Endpoint that return number of configs."""
    if request.method == "GET":
        data = request.get_json()
        if data is None:
            return countConfigs(data={})
        else:
            return countConfigs(data)
    else:
        return InvalidUsage("Forbidden method", status_code=400)


@app.route("/configs/<string:config_type>/<string:name>", methods=["GET"])
def configsByKeys(config_type, name):
    """Endpoint to get a document in the configs collection."""
    if request.method == "GET":
        return getOneConfig({"config_type": config_type, "name": name})
    else:
        raise InvalidUsage(
            "Endpoint does not support {} action".format(request.method))


@app.route("/configs/<string:id>",
           methods=["GET", "PUT", "DELETE"])
def configsById(id):
    """Endpoint to get, update and delete a document in the configs coll."""
    try:
        id = ObjectId(id)
    except Exception as e:
        raise InvalidUsage("Invalid ID", status_code=400)
    if request.method == "GET":
        return getOneConfig({"_id": id})
    elif request.method == "PUT":
        data = request.get_json()
        if data is None:
            raise InvalidUsage("No data sent", status_code=400)
        return updateConfig(id, data)
    elif request.method == "DELETE":
        return markDiscardedConfig(id)


@app.route("/configs/stats/size", methods=["GET"])
def configsSize():
    """Return collection size."""
    if request.method == "GET":
        return jsonify(
            {"code": 200, "message": "ok",
             "result": {
                "size": mongo.db.command("dbStats")["dataSize"]}})


@app.route("/config_types", methods=["GET"])
def configTypes():
    """Return config types."""
    if request.method == "GET":
        return jsonify(
            {"code": 200, "message": "ok", "result": getConfigTypes()})
    else:
        return InvalidUsage("Forbidden method", status_code=400)


@app.route("/config_types/<string:config_type>", methods=["GET"])
def configNames(config_type):
    """Return config types."""
    if request.method == "GET":
        return jsonify(
            {"code": 200, "message": "ok",
             "result": getConfigNames(config_type)})
    else:
        return InvalidUsage("Forbidden method", status_code=400)


# Lists collection db functions
def _queryConfigs(data, projection={}):
    """Return configs document."""
    # Convert timestamps to datetime objects
    # if "created" in data:
    #     for key, value in data["created"].items():
    #         date = datetime.datetime.utcfromtimestamp(value)
    #         data["created"].update({key: date})
    try:
        results = mongo.db.configs.find(data, projection)
    except Exception as e:
        raise InvalidUsage("{}".format(e), status_code=404)
    return results


def getConfigs(data):
    """Return config documents."""
    output = []
    results = _queryConfigs(data, {"name": 1,
                                   "config_type": 1,
                                   "created": 1,
                                   "modified": 1})
    for document in results:
        document.update({"_id": str(document["_id"])})
        output.append(document)
    return jsonify({"result": output, "code": 200, "message": "ok"})


def countConfigs(data):
    """Return number of configs."""
    count = _queryConfigs(data).count()
    return jsonify({"result": count, "code": 200, "message": "ok"})


def insertConfig(data):
    """Insert new document in the lists collection."""
    timestamp = _getDate()
    data.update({"created": timestamp})
    data.update({"modified": [timestamp, ]})
    data.update({"discarded": False})
    try:
        # content = data['value']
        # fs = gridfs.GridFS(mongo.cx.configs)
        # file_id = fs.put(json.dumps(content).encode())
        # data['value'] = str(file_id)
        _createFile(data)
        result = mongo.db.configs.insert_one(data)
    except Exception as e:
        raise InvalidUsage("{}".format(e), status_code=409)
    else:
        data.update({"_id": str(result.inserted_id)})
        return jsonify({"code": 200, "message": "ok", "result": data})


def getOneConfig(data):
    """Return a document from the lists collection."""
    try:
        result = mongo.db.configs.find_one(data)
    except Exception as e:
        raise InvalidUsage("{}".format(e), status_code=404)
    else:
        if result is None:
            raise InvalidUsage("Configuration not found", status_code=404)
        result.update({"_id": str(result["_id"])})
        fs = gridfs.GridFS(mongo.db)
        result.update({"value": json.loads(fs.get(ObjectId(result['value'])).read())})
        return jsonify({"result": result, "code": 200, "message": "ok"})


def updateConfig(id, data):
    """Update a document in the lists collection."""
    _createFile(data)
    try:
        result = mongo.db.configs.update_one(
            {"_id": id}, {"$set": data, "$push": {"modified": _getDate()}})
    except Exception as e:
        raise InvalidUsage("{}".format(e), status_code=409)
    else:
        return jsonify(
            {"result": result.modified_count, "code": 200, "message": "ok"})


def markDiscardedConfig(id):
    """Mark a document in the lists collection as discarded."""
    try:
        result = mongo.db.configs.find_one({"_id": id})
    except Exception as e:
        raise InvalidUsage("{}".format(e), status_code=409)
    else:
        name_discarded = result["name"] + '_' + str(uuid.uuid4())
        return updateConfig(id, {"discarded": True, "name": name_discarded})


def deleteConfig(id):
    """Delete a document in the lists collection."""
    try:
        result = mongo.db.configs.delete_one({"_id": id})
    except Exception as e:
        raise InvalidUsage("{}".format(e), status_code=400)
    else:
        return jsonify(
            {"result": result.deleted_count, "code": 200, "message": "ok"})


def getConfigTypes():
    """Return config types."""
    try:
        results = mongo.db.configs.aggregate([
            {
                "$group": {
                    "_id": "null",
                    "config_types": {
                        "$addToSet": "$config_type"}
                }
            }
        ])
    except Exception as e:
        raise InvalidUsage("{}".format(e), status_code=404)
    results = list(results)
    if results:
        return results[0]["config_types"]
    else:
        return []


def getConfigNames(config_type):
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
        raise InvalidUsage("{}".format(e), status_code=404)
    results = list(results)
    if results:
        return results[0]["names"]
    else:
        return []


def _createFile(data):
    if 'value' in data:
        content = data['value']
        fs = gridfs.GridFS(mongo.db)
        file_id = fs.put(json.dumps(content).encode())
        data['value'] = str(file_id)


# PV Endpoint
# @app.route("/pvs", methods=["GET", "POST"])
# def pvConfigurations():
#     """Endpoint to get and insert configuration."""
#     if request.method == "GET":
#         data = request.get_json()
#         if data is None:
#             return getAllPvConfigurations()
#         else:
#             return queryPvConfiguration(data)
#     elif request.method == "POST":
#         data = request.get_json()
#         # Insert new configuration
#         return makeNewPvConfiguration(data)
#
#
# @app.route("/pvs/<string:id>", methods=["GET", "PUT", "DELETE"])
# def pvConfigurationsId(id):
#     """Endpoint to get, update or delete a pv configuration by the id."""
#     try:
#         id = ObjectId(id)
#     except Exception as e:
#         raise InvalidUsage("invalid id", status_code=400)
#     if request.method == "GET":
#         return queryPvConfiguration({"_id": id})
#     elif request.method == "PUT":
#         data = request.get_json()
#         if data is None:
#             raise InvalidUsage("Update parameters missing", status_code=400)
#         return updatePvConfiguration(id, data)
#     elif request.method == "DELETE":
#         return deletePvConfiguration(id)
#
#
# @app.route("/pvs/<string:id>/values", methods=["POST"])
# def pvConfigurationsItems(id):
#     """Endpoint to insert new pvs to configuration."""
#     try:
#         id = ObjectId(id)
#     except Exception as e:
#         raise InvalidUsage("invalid id", status_code=400)
#     if request.method == "POST":
#         data = request.get_json()
#         if data is None:
#             raise InvalidUsage("Insert parameters missing", status_code=400)
#         return makeNewPvConfigurationItem(id, data)
#     else:
#         pass
#
#
# @app.route("/pvs/<string:id>/values/<string:pv_name>",
#            methods=["GET", "PUT", "DELETE"])
# def pvConfigurationsValuesId(id, pv_name):
#     """Endpoint to get, update or delete a pv config value by the pv name."""
#     try:
#         id = ObjectId(id)
#     except Exception as e:
#         raise InvalidUsage("invalid id", status_code=400)
#
#     if request.method == "GET":
#         return queryPvConfiguration({"_id": id})
#     elif request.method == "PUT":
#         data = request.get_json()
#         if data is None:
#             raise InvalidUsage("Update parameters missing", status_code=400)
#         return updatePvConfigurationItem(id, pv_name, data)
#     elif request.method == "DELETE":
#         return deletePvConfigurationItem(id, pv_name)


# PvConfiguration DB access functions
# def getAllPvConfigurations():
#     """Return all pv configurations."""
#     output = []
#     for pv_configuration in mongo.db.pv_configuration.find():
#         pv_configuration.update({"_id": str(pv_configuration["_id"])})
#         output.append(pv_configuration)
#     return jsonify(result=output)
#
#
# def makeNewPvConfiguration(data):
#     """Insert new Pv configuration."""
#     if type(data) is dict:
#         # Sanity check
#         if not check_pv_document(data):
#             raise InvalidUsage("Invalid document", status_code=400)
#         # Insert
#         data.update({"timestamp": datetime.datetime.utcnow()})
#         try:
#             result = mongo.db.pv_configuration.insert_one(data)
#         except Exception as e:  # Change to specific exception
#             raise InvalidUsage("Duplicate Key", status_code=409)
#         else:
#             return jsonify(result=str(result.inserted_id))
#     # elif type(data) is list:  # Bulk write
#     #     # raise InvalidUsage("Bulk write not allowed", status_code=400)
#     #     if not check_pv_collection(data):
#     #         raise InvalidUsage("Invalid document", status_code=400)
#     #     try:
#     #         result = mongo.db.pv_configuration.insert_many(data)
#     #     except Exception as e:
#     #         raise InvalidUsage("Error", status_code=409)
#     #     else:
#     #         return jsonify(result=[str(id) for id in result.inserted_ids])
#
#
# def queryPvConfiguration(data):
#     """Return a pv configuration based on data."""
#     output = []
#     # Convert timestamps to datetime objects
#     if "timestamp" in data:
#         for key, value in data["timestamp"].items():
#             date = datetime.datetime.utcfromtimestamp(value)
#             data["timestamp"].update({key: date})
#     try:
#         results = mongo.db.pv_configuration.find(data)
#     except Exception as e:
#         raise InvalidUsage("{}".format(e), status_code=404)
#     for pv_configuration in results:
#         pv_configuration.update({"_id": str(pv_configuration["_id"])})
#         output.append(pv_configuration)
#     return jsonify(result=output)
#
#
# def updatePvConfiguration(id, data):
#     """Update a pv configuration."""
#     try:
#         result = mongo.db.pv_configuration.update_one(
#             {"_id": id}, {"$set": data})
#     except Exception as e:
#         raise InvalidUsage("Duplicate Key? - {}".format(e), status_code=409)
#     else:
#         return jsonify(result=result.modified_count)
#
#
# def deletePvConfiguration(id):
#     """Delete a PV configuration."""
#     try:
#         result = mongo.db.pv_configuration.delete_one({"_id": id})
#     except Exception as e:
#         raise InvalidUsage("{}".format(e), status_code=400)
#     else:
#         return jsonify(result=result.deleted_count)
#
#
# def makeNewPvConfigurationItem(id, data):
#     """Insert new pv value in configuration."""
#     # TODO: check data
#     if type(data) is dict:
#         try:
#             result = mongo.db.pv_configuration.update_one(
#                 {"_id": id},
#                 {"$push": {"values": data}})
#         except Exception as e:
#             raise InvalidUsage("{}".format(e), status_code=400)
#         else:
#             return jsonify(result=result.modified_count)
#     elif type(data) is list:
#         try:
#             result = mongo.db.pv_configuration.update_many(
#                 {"_id": id},
#                 {"$push": {"values": {"$each": data}}})
#         except Exception as e:
#             raise InvalidUsage("{}".format(e), status_code=400)
#         else:
#             return jsonify(result=result.modified_count)
#
#
# def updatePvConfigurationItem(id, pv_name, data):
#     """Update a pv configuration value."""
#     try:
#         result = mongo.db.pv_configuration.update_one(
#             {"_id": id, "values.pv_name": pv_name},
#             {"$set": {"values.$.value": data["value"]}})
#     except Exception as e:
#         raise InvalidUsage("Duplicate Key? - {}".format(e), status_code=409)
#     else:
#         return jsonify(result=result.modified_count)
#
#
# def deletePvConfigurationItem(id, pv_name):
#     """Delete a pv configuration value."""
#     try:
#         result = mongo.db.pv_configuration.update_one(
#             {"_id": id},
#             {"$pull": {"values": {"pv_name": pv_name}}})
#     except Exception as e:
#         raise InvalidUsage("{}".format(e), status_code=400)
#     else:
#         return jsonify(result=result.modified_count)


# Helpers
def _getDate():
    return time.time()
    # return datetime.datetime.utcnow()


def _parseTimestamps():
    pass
# def serialize(document):
#     """Serialize pv_configuration dict."""
#     return {
#         "_id": str(document["_id"]),
#         "name": document["name"],
#         "config_type": document["config_type"],
#         "values": document["values"]
#     }
#
#
# def check_pv_collection(collection):
#     """Check pv_configuration docuements."""
#     for document in collection:
#         if not check_pv_document(document):
#             return False
#     return True
#
#
# def check_values_collection(collection):
#     """Check pv_configuration_value docuements."""
#     for document in collection:
#         if not check_values_document(document):
#             return False
#     return True
#
#
# def check_pv_document(document):
#     """Check if document has the required fields."""
#     if "name" not in document:
#         print("name not found")
#         return False
#     if "config_type" not in document:
#         print("config_type not found")
#         return False
#     if "values" not in document:
#         print("values not found")
#         return False
#     return check_values_collection(document["values"])
#
#
# def check_values_document(document):
#     """Check if embedded document has the required fields."""
#     if "pv_name" not in document:
#         print("pvname not found")
#         return False
#     if "pv_type" not in document:
#         print("pvtype not found")
#         return False
#     if "value" not in document:
#         print("value not found")
#         return False
#     return True
#
#
# @app.route("/test",  methods=["GET", "POST", "PUT", "DELETE"])
# def test():
#     """Test endpoint."""
#     if request.method == "GET":
#         raise InvalidUsage("message", status_code=404)
#     elif request.method == "POST":
#         return jsonify({"result": "data", "status": 200})


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
