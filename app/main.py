"""API server definition.

Endpoints:
    /pvs -
        GET - Return all configurations. If a JSON is sent it will be used to
              query a configuration.
        POST - Insert a new configuration received as a JSON.
    /pvs/<string:id> -
        GET - Query a configuration based on the id
        PUT - Update a configuration based on the id. The attributes to be
              updated are received via JSON.
        DELETE - Delete a configuration based on the id.
    /pvs/<string:id>/values -
        POST - Insert new pv in configuration.
    /pvs/<string:id>/values/<string:pv_name> -
        GET - Query a configuration based on the id.
        PUT - Update a pv item based on the configuration id and pv name.
        DELETE - Delete a pv from a configuration.

    /lists -
        GET - Return all documents on the list collection.
        POST - Insert new configuration.
    /lists/<string:name> -
        GET - Return a documents.
        PUT - Update a documents.
        DELETE - Delete a document.
"""
import logging
import datetime

from flask import Flask, request, jsonify
from flask_pymongo import PyMongo

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
            # return getAllLists()
            return queryLists(data={})
        else:
            return queryLists(data)
    elif request.method == "POST":
        data = request.get_json()
        if data is None:
            raise InvalidUsage("No data sent", status_code=400)
        return insertList(data)


@app.route("/configs/<string:config_type>/<string:name>",
           methods=["GET", "PUT", "DELETE"])
def configsByKey(config_type, name):
    """Endpoint to get, update and delete a document in the lists coll."""
    if request.method == "GET":
        return getListByKey(name, config_type)
    elif request.method == "PUT":
        data = request.get_json()
        if data is None:
            raise InvalidUsage("No data sent", status_code=400)
        return updateList(name, config_type, data)
    elif request.method == "DELETE":
        return deleteList(name, config_type)


# Lists collection db functions
# def getAllLists():
#     """Return all documents in the lists collection."""
#     output = []
#     results = mongo.db.lists.find()
#     for result in results:
#         result.update({"_id": str(result["_id"])})
#         output.append(result)
#     return jsonify(result=output)


def queryLists(data):
    """Return lists document."""
    output = []
    # Convert timestamps to datetime objects
    if "timestamp" in data:
        for key, value in data["timestamp"].items():
            date = datetime.datetime.utcfromtimestamp(value)
            data["timestamp"].update({key: date})
    try:
        results = mongo.db.lists.find(data)
    except Exception as e:
        raise InvalidUsage("{}".format(e), status_code=404)
    for document in results:
        document.update({"_id": str(document["_id"])})
        output.append(document)
    return jsonify({"result": output, "code": 200, "message": "ok"})


def insertList(data):
    """Insert new document in the lists collection."""
    data.update({"timestamp": datetime.datetime.utcnow()})
    try:
        mongo.db.lists.insert_one(data)
    except Exception as e:
        raise InvalidUsage("{}".format(e), status_code=409)
    else:
        return jsonify({"code": 200, "message": "ok"})


def getListByKey(name, config_type):
    """Return a document from the lists collection."""
    try:
        result = mongo.db.lists.find_one(
            {"name": name, "config_type": config_type})
    except Exception as e:
        raise InvalidUsage("{}".format(e), status_code=404)
    else:
        if result is None:
            raise InvalidUsage("Configuration not found", status_code=404)
        result.update({"_id": str(result["_id"])})
        return jsonify({"result": result, "code": 200, "message": "ok"})


def updateList(name, config_type, data):
    """Update a document in the lists collection."""
    try:
        result = mongo.db.lists.update_one(
            {"name": name, "config_type": config_type}, {"$set": data})
    except Exception as e:
        raise InvalidUsage("{}".format(e), status_code=409)
    else:
        return jsonify(
            {"result": result.modified_count, "code": 200, "message": "ok"})


def deleteList(name, config_type):
    """Delete a document in the lists collection."""
    try:
        result = mongo.db.lists.delete_one(
            {"name": name, "config_type": config_type})
    except Exception as e:
        raise InvalidUsage("{}".format(e), status_code=400)
    else:
        return jsonify(
            {"result": result.deleted_count, "code": 200, "message": "ok"})

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
