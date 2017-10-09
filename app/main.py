"""API server definition.

Endpoints:
    Get all PvConfiguration
    Insert new configuration
    Get PvConfiguration by id
    Update configuration by id
    Delete configuration by id

    Get all Values of a PvConfiguration
    Insert new Value for PvConfiguration
"""
import json
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo, ObjectId


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
    """Retrun json message with error info."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def check_pv_collection(collection):
    """Check pv_configuration docuements."""
    for document in collection:
        if not check_pv_document(document):
            return False
    return True


def check_values_collection(collection):
    """Check pv_configuration_value docuements."""
    for document in collection:
        if not check_values_document(document):
            return False
    return True


def check_pv_document(document):
    """Check if document has the required fields."""
    if "name" not in document:
        print("name not found")
        return False
    if "config_type" not in document:
        print("config_type not found")
        return False
    if "values" not in document:
        print("values not found")
        return False
    return check_values_collection(document["values"])


def check_values_document(document):
    """Check if embedded document has the required fields."""
    if "pv_name" not in document:
        print("pvname not found")
        return False
    if "pv_type" not in document:
        print("pvtype not found")
        return False
    if "value" not in document:
        print("value not found")
        return False
    return True


# Endpoints
@app.route("/")
@app.route("/configs", methods=["GET", "POST"])
def pvConfigurations():
    """Endpoint to get and insert configuration."""
    if request.method == "GET":
        data = request.get_json()
        if data is None:
            return getAllPvConfigurations()
        else:
            return queryPvConfiguration(data)
    elif request.method == "POST":
        data = request.get_json()
        # Insert new configuration
        return makeNewPvConfiguration(data)


@app.route("/configs/<string:id>", methods=["GET", "PUT", "DELETE"])
def pvConfigurationsId(id):
    """Endpoint to get, update or delete a pv configuration by the id."""
    id = ObjectId(id)
    if request.method == "GET":
        return queryPvConfiguration({"_id": id})
    elif request.method == "PUT":
        data = request.get_json()
        if data is None:
            raise InvalidUsage("Update parameters missing", status_code=400)
        return updatePvConfiguration(id, data)
    elif request.method == "DELETE":
        return deletePvConfiguration(id)


# PvConfiguration DB access functions
def getAllPvConfigurations():
    """Return all pv configurations."""
    output = []
    for pv_configuration in mongo.db.pv_configuration.find():
        output.append(serialize(pv_configuration))
    return jsonify(result=output)


def makeNewPvConfiguration(data):
    """Insert new Pv configuration."""
    if type(data) is dict:
        # Sanity check
        if not check_pv_document(data):
            raise InvalidUsage("Invalid document", status_code=400)
        # Insert
        try:
            result = mongo.db.pv_configuration.insert_one(data)
        except Exception as e:  # Change to specific exception
            raise InvalidUsage("Duplicate Key", status_code=409)
        else:
            return jsonify(result=str(result.inserted_id))
    elif type(data) is list:  # Bulk write
        # raise InvalidUsage("Bulk write not allowed", status_code=400)
        if not check_pv_collection(data):
            raise InvalidUsage("Invalid document", status_code=400)
        try:
            result = mongo.db.pv_configuration.insert_many(data)
        except Exception as e:
            raise InvalidUsage("Error", status_code=409)
        else:
            return jsonify(result=[str(id) for id in result.inserted_ids])


def queryPvConfiguration(data):
    """Return a pv configuration based on data."""
    output = []
    results = mongo.db.pv_configuration.find(data)
    for pv_configuration in results:
        output.append(serialize(pv_configuration))
    return jsonify(result=output)


def updatePvConfiguration(id, data):
    """Update a pv configuration."""
    try:
        result = mongo.db.pv_configuration.update_one(
            {"_id": id}, {"$set": data})
    except Exception as e:
        raise InvalidUsage("Duplicate Key?", status_code=409)
    else:
        return jsonify(result=result.modified_count)


def deletePvConfiguration(id):
    """Delete a PV configuration."""
    try:
        result = mongo.db.pv_configuration.delete_one({"_id": id})
    except Exception as e:
        raise InvalidUsage("{}".format(e), status_code=400)
    else:
        return jsonify(result=result.deleted_count)


# Helpers
def serialize(document):
    """Serialize pv_configuration dict."""
    return {
        "_id": str(document["_id"]),
        "name": document["name"],
        "config_type": document["config_type"],
        "values": document["values"]
    }

    
if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
