DROP DATABASE IF EXISTS sirius;

CREATE DATABASE sirius CHARACTER SET=utf8mb4;

USE sirius;

CREATE TABLE IF NOT EXISTS configuration (
    name VARCHAR(32) NOT NULL,
    classname VARCHAR(32) NOT NULL,
    
    PRIMARY KEY(name, classname)
);


CREATE TABLE IF NOT EXISTS configuration_values (
    name VARCHAR(32) NOT NULL,
    classname VARCHAR(32) NOT NULL,
    pvname VARCHAR(32) NOT NULL,
    typename VARCHAR(16) NOT NULL,
    value VARCHAR(255) NOT NULL,

    PRIMARY KEY(name, classname, pvname),

    FOREIGN KEY (name, classname) REFERENCES configuration(name, classname)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS parameter (
  name VARCHAR(64) NOT NULL,
  type ENUM('tune', 'chromaticity') NOT NULL,
  description TEXT NULL,

  PRIMARY KEY(name, type)
);

CREATE TABLE IF NOT EXISTS parameter_values (
  name VARCHAR(64) NOT NULL,
  type ENUM('tune', 'chromaticity') NOT NULL,
  `line` INT NOT NULL,
  `column` INT NOT NULL,
  value FLOAT NOT NULL,

  PRIMARY KEY(name, type, `line`, `column`),

  FOREIGN KEY (name, type) REFERENCES parameter(name, type)
  ON UPDATE CASCADE
  ON DELETE CASCADE
);

INSERT INTO parameter VALUES('standard_matrix', 'tune', NULL);
INSERT INTO parameter_values VALUES('standard_matrix', 'tune', 0, 0, 0.6);
INSERT INTO parameter_values VALUES('standard_matrix', 'tune', 0, 1, 1.0);
INSERT INTO parameter_values VALUES('standard_matrix', 'tune', 1, 0, 1.5);
INSERT INTO parameter_values VALUES('standard_matrix', 'tune', 1, 1, 0.5);

