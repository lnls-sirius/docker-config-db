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
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from models import Base, PvConfiguration, PvConfigurationValue

app = Flask(__name__)

engine = create_engine(
    "mysql+pymysql://root:root@config-db/config_db")
Base.metadata.bind = engine
# Base.metadata.create_all(engine)

db_session = sessionmaker(bind=engine)
session = db_session()


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


# Endpoints
@app.route("/")
@app.route("/configs", methods=["GET", "POST"])
def pvConfigurations():
    """Endpoint to get and insert configuration."""
    if request.method == "GET":
        return getAllPvConfigurations()
    elif request.method == "POST":
        # Insert new configuration
        name = request.args.get("name")
        config_type = request.args.get("config_type")
        return makeNewPvConfiguration(name, config_type)


@app.route("/configs/<int:id>", methods=["GET", "PUT", "DELETE"])
def pvConfigurationsId(id):
    """Endpoint to get, update or delete a pv configuration by the id."""
    if request.method == "GET":
        return getPvConfiguration(id)
    elif request.method == "PUT":
        name = request.args.get("name", None)
        config_type = request.args.get("config_type", None)
        return updatePvConfiguration(id, name, config_type)
    elif request.method == "DELETE":
        return deletePvConfiguration(id)


@app.route("/configs/<int:config_id>/values", methods=["GET", "POST"])
def pvConfigurationsValues(config_id):
    """Endpoint that return all values of configuration."""
    if request.method == "GET":
        return getAllPvConfigurationValues(config_id)
    if request.method == "POST":
        pv_name = request.args.get("pv_name")
        pv_type = request.args.get("pv_type")
        value = request.args.get("value")
        return makeNewPvConfigurationValue(pv_name, pv_type, value, config_id)


@app.route("/values/<int:id>", methods=["GET", "PUT", "DELETE"])
def pvConfigurationsValuesId(id):
    """Endpoint to get, update or delete a pv configuration value by the id."""
    if request.method == "GET":
        return getPvConfigurationValues(id)
    elif request.method == "PUT":
        pv_name = request.args.get("pv_name", None)
        pv_type = request.args.get("pv_type", None)
        value = request.args.get("value", None)
        return updatePvConfigurationValue(id, pv_name, pv_type, value)
    elif request.method == "DELETE":
        return deletePvConfigurationValue(id)


# PvConfiguration DB access functions
def getAllPvConfigurations():
    """Return all pv configurations."""
    configs = session.query(PvConfiguration).all()
    return jsonify(PvConfiguration=[i.serialize for i in configs])


def makeNewPvConfiguration(name, config_type):
    """Insert new Pv configuration."""
    config = PvConfiguration(name=name, config_type=config_type)
    session.add(config)
    commit()
    return jsonify(PvConfiguration=config.serialize)


def getPvConfiguration(id):
    """Return pv configuration."""
    config = getPvConfigurationById(id)
    return jsonify(PvConfiguration=config.serialize)


def updatePvConfiguration(id, name, config_type):
    """Update pv configuration."""
    config = getPvConfigurationById(id)
    if name is not None:
        config.name = name
    if config_type is not None:
        config.config_type = config_type
    session.add(config)
    commit()
    return jsonify(PvConfiguration=config.serialize)


def deletePvConfiguration(id):
    """Delete PV configuration."""
    config = getPvConfigurationById(id)
    session.delete(config)
    commit()
    return jsonify(PvConfiguration=config.serialize)


def getAllPvConfigurationValues(config_id):
    """Get all values of a configuration."""
    # values = session.query(PvConfigurationValue).filter_by(
    #     pv_configuration_id=config_id)
    config = getPvConfigurationById(config_id)
    values = session.query(PvConfigurationValue).filter_by(
        pv_configuration=config)
    return jsonify(PvConfigurationValue=[i.serialize for i in values])


def makeNewPvConfigurationValue(pv_name, pv_type, value, config_id):
    """Insert new value to a pv configuration."""
    # Create new config value
    value = PvConfigurationValue(pv_name=pv_name, pv_type=pv_type, value=value)
    config = getPvConfigurationById(config_id)
    value.pv_configuration = config
    session.add(value)
    commit()
    return jsonify(PvConfigurationValue=value.serialize)


def getPvConfigurationValues(id):
    """Return Pv configuration value."""
    value = getPvConfigurationValueById(id)
    return jsonify(PvConfigurationValue=value.serialize)


def updatePvConfigurationValue(id, pv_name, pv_type, value):
    """Update a pv configuration value."""
    config_value = getPvConfigurationValueById(id)
    if pv_name is not None:
        config_value.pv_name = pv_name
    if pv_type is not None:
        config_value.pv_type = pv_type
    if value is not None:
        config_value.value = value
    session.add(config_value)
    commit()
    return jsonify(PvConfigurationValue=config_value.serialize)


def deletePvConfigurationValue(id):
    """Delete a pv configuration value."""
    config_value = getPvConfigurationValueById(id)
    session.delete(config_value)
    commit()
    return jsonify(PvConfigurationValue=config_value.serialize)


# Helpers
def getPvConfigurationById(id):
    """Retrieve PvConfiguration from DB."""
    try:
        config = session.query(PvConfiguration).filter_by(id=id).one()
    except NoResultFound:
        # Not Found
        raise InvalidUsage("PvConfiguration not found.", status_code=404)
    return config


def getPvConfigurationValueById(id):
    """Retrieve PvConfigurationValue from DB."""
    try:
        value = session.query(PvConfigurationValue).filter_by(id=id).one()
    except NoResultFound:
        # Not found
        raise InvalidUsage("PvConfigurationValue not found", status_code=404)
    return value


def commit():
    """Commit DB transactions. Rollback if anything goes wrong."""
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        # The 409 (Conflict) status code indicates that the request could not
        # be completed due to a conflict with the current state of the target
        # resource.  This code is used in situations where the user might be
        # able to resolve the conflict and resubmit the request. (RFC 7231)
        raise InvalidUsage("{}".format(e.orig), status_code=409)


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
