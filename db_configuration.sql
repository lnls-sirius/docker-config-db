USE config_db;

CREATE TABLE IF NOT EXISTS pv_configuration (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(32) NOT NULL,
    config_type VARCHAR(32) NOT NULL,

    PRIMARY KEY(id),
    UNIQUE(name, config_type)
);


CREATE TABLE IF NOT EXISTS pv_configuration_value (
    id INT NOT NULL AUTO_INCREMENT,
    pv_name VARCHAR(32) NOT NULL,
    pv_type VARCHAR(16) NOT NULL,
    value VARCHAR(255) NOT NULL,
    pv_configuration_id INTEGER NOT NULL,

    PRIMARY KEY(id),
    FOREIGN KEY (pv_configuration_id) REFERENCES pv_configuration(id),
    UNIQUE(pv_configuration_id, pv_name)
);
