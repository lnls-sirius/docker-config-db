conn = new Mongo();
db = conn.getDB("config_database");
db.pv_configuration.createIndex({name: 1, config_type: 1}, { unique: true});
db.pv_configuration.createIndex({name: 1, config_type: 1, "values.pv_name": 1}, {unique: true});
