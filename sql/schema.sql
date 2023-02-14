/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `agency`
--

DROP TABLE IF EXISTS `agency`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `agency` (
  `agency_id` varchar(10) COLLATE utf8mb3_unicode_ci NOT NULL,
  `agency_name` varchar(100) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `agency_type` varchar(1) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `active911_id` varchar(50) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `nws_alerts` tinyint(1) NOT NULL DEFAULT 0,
  `active` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`agency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cities`
--

DROP TABLE IF EXISTS `cities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cities` (
  `name` varchar(25) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `abbr` varchar(3) COLLATE utf8mb3_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comments` (
  `uid` bigint(20) NOT NULL AUTO_INCREMENT,
  `agency` varchar(10) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `callid` varchar(50) COLLATE utf8mb3_unicode_ci NOT NULL,
  `comment` longtext COLLATE utf8mb3_unicode_ci NOT NULL,
  `updated` datetime NOT NULL,
  `processed` tinyint(1) NOT NULL,
  PRIMARY KEY (`uid`),
  UNIQUE KEY `UNIQUE` (`agency`,`callid`),
  KEY `INDX1` (`agency`,`callid`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `incidents`
--

DROP TABLE IF EXISTS `incidents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `incidents` (
  `uid` bigint(20) NOT NULL AUTO_INCREMENT,
  `callid` varchar(50) COLLATE utf8mb3_unicode_ci NOT NULL,
  `incidentid` varchar(50) COLLATE utf8mb3_unicode_ci NOT NULL,
  `nature` varchar(50) COLLATE utf8mb3_unicode_ci NOT NULL,
  `agency` varchar(10) COLLATE utf8mb3_unicode_ci NOT NULL,
  `unit` varchar(50) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `city` varchar(25) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `zone` varchar(10) COLLATE utf8mb3_unicode_ci NOT NULL,
  `address` varchar(100) COLLATE utf8mb3_unicode_ci NOT NULL,
  `gps_x` float(10,6) NOT NULL,
  `gps_y` float(10,6) NOT NULL,
  `reported` datetime NOT NULL,
  `alert_sent` tinyint(1) NOT NULL,
  PRIMARY KEY (`uid`),
  UNIQUE KEY `UNIQUE` (`agency`,`callid`),
  KEY `INDX1` (`agency`,`callid`),
  KEY `INDX2` (`agency`,`incidentid`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `nature`
--

DROP TABLE IF EXISTS `nature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nature` (
  `abbr` varchar(15) COLLATE utf8mb3_unicode_ci NOT NULL,
  `desc` varchar(30) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`abbr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `units`
--

DROP TABLE IF EXISTS `units`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `units` (
  `unit` varchar(10) COLLATE utf8mb3_unicode_ci NOT NULL,
  `agency` varchar(10) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `cross_staff_flag` tinyint(1) DEFAULT 0,
  `cross_staff_units` varchar(100) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `always_on_flag` tinyint(1) DEFAULT 0,
  `spillman_usr` varchar(45) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `spillman_pwd` varchar(45) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`unit`),
  KEY `INDX1` (`agency`,`unit`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;