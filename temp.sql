-- MySQL dump 10.13  Distrib 5.5.55, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: sirius
-- ------------------------------------------------------
-- Server version	5.5.55-0ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `parameter`
--

DROP TABLE IF EXISTS `parameter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `parameter` (
  `name` varchar(64) NOT NULL,
  `type` enum('tune','chromaticity') NOT NULL,
  `description` text,
  PRIMARY KEY (`name`,`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parameter`
--

LOCK TABLES `parameter` WRITE;
/*!40000 ALTER TABLE `parameter` DISABLE KEYS */;
INSERT INTO `parameter` VALUES ('standard_matrix','tune','Standard matrix for tune optimization');
/*!40000 ALTER TABLE `parameter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parameter_values`
--

DROP TABLE IF EXISTS `parameter_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `parameter_values` (
  `name` varchar(64) NOT NULL,
  `type` enum('tune','chromaticity') NOT NULL,
  `line` int(11) NOT NULL,
  `column` int(11) NOT NULL,
  `value` float NOT NULL,
  PRIMARY KEY (`name`,`type`,`line`,`column`),
  CONSTRAINT `parameter_values_ibfk_1` FOREIGN KEY (`name`, `type`) REFERENCES `parameter` (`name`, `type`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parameter_values`
--

LOCK TABLES `parameter_values` WRITE;
/*!40000 ALTER TABLE `parameter_values` DISABLE KEYS */;
INSERT INTO `parameter_values` VALUES ('standard_matrix','tune',0,0,1),('standard_matrix','tune',0,1,0.5),('standard_matrix','tune',1,0,1),('standard_matrix','tune',1,1,0.5);
/*!40000 ALTER TABLE `parameter_values` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `section_configuration`
--

DROP TABLE IF EXISTS `section_configuration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `section_configuration` (
  `name` varchar(64) NOT NULL,
  `section` enum('BO','SI') NOT NULL,
  PRIMARY KEY (`name`,`section`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `section_configuration_values`
--

DROP TABLE IF EXISTS `section_configuration_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `section_configuration_values` (
  `name` varchar(64) NOT NULL,
  `section` enum('BO','SI') NOT NULL,
  `pvname` varchar(32) NOT NULL,
  `value` float NOT NULL,
  PRIMARY KEY (`name`,`section`,`pvname`),
  CONSTRAINT `section_configuration_values_ibfk_1` FOREIGN KEY (`name`, `section`) REFERENCES `section_configuration` (`name`, `section`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-05-22 13:14:51
