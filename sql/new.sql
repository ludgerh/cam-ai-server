-- MySQL dump 10.19  Distrib 10.3.31-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: C-SERVER-NEW
-- ------------------------------------------------------
-- Server version	10.3.31-MariaDB-0+deb10u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=117 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add camera',7,'add_camera'),(26,'Can change camera',7,'change_camera'),(27,'Can delete camera',7,'delete_camera'),(28,'Can view camera',7,'view_camera'),(29,'Can add tag',8,'add_tag'),(30,'Can change tag',8,'change_tag'),(31,'Can delete tag',8,'delete_tag'),(32,'Can view tag',8,'view_tag'),(33,'Can add tfmodel',9,'add_tfmodel'),(34,'Can change tfmodel',9,'change_tfmodel'),(35,'Can delete tfmodel',9,'delete_tfmodel'),(36,'Can view tfmodel',9,'view_tfmodel'),(37,'Can add trainframe',10,'add_trainframe'),(38,'Can change trainframe',10,'change_trainframe'),(39,'Can delete trainframe',10,'delete_trainframe'),(40,'Can view trainframe',10,'view_trainframe'),(41,'Can add setting',11,'add_setting'),(42,'Can change setting',11,'change_setting'),(43,'Can delete setting',11,'delete_setting'),(44,'Can view setting',11,'view_setting'),(45,'Can add epoch',12,'add_epoch'),(46,'Can change epoch',12,'change_epoch'),(47,'Can delete epoch',12,'delete_epoch'),(48,'Can view epoch',12,'view_epoch'),(49,'Can add fit',13,'add_fit'),(50,'Can change fit',13,'change_fit'),(51,'Can delete fit',13,'delete_fit'),(52,'Can view fit',13,'view_fit'),(53,'Can add userinfo',14,'add_userinfo'),(54,'Can change userinfo',14,'change_userinfo'),(55,'Can delete userinfo',14,'delete_userinfo'),(56,'Can view userinfo',14,'view_userinfo'),(57,'Can add event',15,'add_event'),(58,'Can change event',15,'change_event'),(59,'Can delete event',15,'delete_event'),(60,'Can view event',15,'view_event'),(61,'Can add event_frame',16,'add_event_frame'),(62,'Can change event_frame',16,'change_event_frame'),(63,'Can delete event_frame',16,'delete_event_frame'),(64,'Can view event_frame',16,'view_event_frame'),(65,'Can add cam',17,'add_cam'),(66,'Can change cam',17,'change_cam'),(67,'Can delete cam',17,'delete_cam'),(68,'Can view cam',17,'view_cam'),(69,'Can add view',18,'add_view'),(70,'Can change view',18,'change_view'),(71,'Can delete view',18,'delete_view'),(72,'Can view view',18,'view_view'),(73,'Can add detctor',19,'add_detctor'),(74,'Can change detctor',19,'change_detctor'),(75,'Can delete detctor',19,'delete_detctor'),(76,'Can view detctor',19,'view_detctor'),(77,'Can add detector',19,'add_detector'),(78,'Can change detector',19,'change_detector'),(79,'Can delete detector',19,'delete_detector'),(80,'Can view detector',19,'view_detector'),(81,'Can add eventer',20,'add_eventer'),(82,'Can change eventer',20,'change_eventer'),(83,'Can delete eventer',20,'delete_eventer'),(84,'Can view eventer',20,'view_eventer'),(85,'Can add school',9,'add_school'),(86,'Can change school',9,'change_school'),(87,'Can delete school',9,'delete_school'),(88,'Can view school',9,'view_school'),(89,'Can add mask',21,'add_mask'),(90,'Can change mask',21,'change_mask'),(91,'Can delete mask',21,'delete_mask'),(92,'Can view mask',21,'view_mask'),(93,'Can add evt_condition',22,'add_evt_condition'),(94,'Can change evt_condition',22,'change_evt_condition'),(95,'Can delete evt_condition',22,'delete_evt_condition'),(96,'Can view evt_condition',22,'view_evt_condition'),(97,'Can add access_control',23,'add_access_control'),(98,'Can change access_control',23,'change_access_control'),(99,'Can delete access_control',23,'delete_access_control'),(100,'Can view access_control',23,'view_access_control'),(101,'Can add videoclip',24,'add_videoclip'),(102,'Can change videoclip',24,'change_videoclip'),(103,'Can delete videoclip',24,'delete_videoclip'),(104,'Can view videoclip',24,'view_videoclip'),(105,'Can add repeater',25,'add_repeater'),(106,'Can change repeater',25,'change_repeater'),(107,'Can delete repeater',25,'delete_repeater'),(108,'Can view repeater',25,'view_repeater'),(109,'Can add view_log',26,'add_view_log'),(110,'Can change view_log',26,'change_view_log'),(111,'Can delete view_log',26,'delete_view_log'),(112,'Can view view_log',26,'view_view_log'),(113,'Can add stream',27,'add_stream'),(114,'Can change stream',27,'change_stream'),(115,'Can delete stream',27,'delete_stream'),(116,'Can view stream',27,'view_stream');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$216000$JuIj4N8HmyzG$w7Ia6ktbwczmDcEFyePe+6CTaOOwCUxOOB2Gx65LDkc=','2021-08-11 09:49:43.094072',1,'admin','admin','admin','admin@cam-ai.de',1,1,'2020-09-09 13:33:00.000000');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_access_control`
--

DROP TABLE IF EXISTS `c_client_access_control`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_access_control` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `vtype` varchar(1) NOT NULL,
  `vid` int(11) NOT NULL,
  `u_g` varchar(1) NOT NULL,
  `u_g_nr` int(11) NOT NULL,
  `r_w` varchar(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_access_control`
--

LOCK TABLES `c_client_access_control` WRITE;
/*!40000 ALTER TABLE `c_client_access_control` DISABLE KEYS */;
INSERT INTO `c_client_access_control` VALUES (1,'S',0,'U',0,'W'),(2,'X',0,'U',0,'W');
/*!40000 ALTER TABLE `c_client_access_control` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_cam`
--

DROP TABLE IF EXISTS `c_client_cam`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_cam` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fpsactual` double NOT NULL,
  `lastused` datetime(6) NOT NULL,
  `made` datetime(6) NOT NULL,
  `name` varchar(100) NOT NULL,
  `url_img` varchar(256) NOT NULL,
  `url_vid` varchar(256) NOT NULL,
  `xres` int(11) NOT NULL,
  `yres` int(11) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `fpslimit` double NOT NULL,
  `feed_type` int(11) NOT NULL,
  `outbuffers` varchar(255) NOT NULL,
  `apply_mask` tinyint(1) NOT NULL,
  `repeater` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_cam`
--

LOCK TABLES `c_client_cam` WRITE;
/*!40000 ALTER TABLE `c_client_cam` DISABLE KEYS */;
INSERT INTO `c_client_cam` VALUES (1,3.953488372093023,'2021-08-11 09:49:27.974996','2020-09-23 18:40:29.000000','Reolink','http://192.168.126.35/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=whatever&user=CAM_AI&password=easy123','rtmp://192.168.126.35/bcs/channel0_main.bcs?channel=0&stream=1&user=CAM_AI&password=easy123',2560,1440,0,5,2,'[[\"V\",1],[\"D\",1],[\"E\",1]]',0,0),(2,5.5,'2021-07-14 14:42:23.415322','2020-10-02 11:24:22.000000','somewhere','','http://cam1.infolink.ru/mjpg/video.mjpg',1280,800,1,5,2,'[[\"V\",2],[\"D\",2],[\"E\",2]]',0,0);
/*!40000 ALTER TABLE `c_client_cam` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_detector`
--

DROP TABLE IF EXISTS `c_client_detector`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_detector` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `made` datetime(6) NOT NULL,
  `lastused` datetime(6) NOT NULL,
  `xres` int(11) NOT NULL,
  `yres` int(11) NOT NULL,
  `fpslimit` double NOT NULL,
  `fpsactual` double NOT NULL,
  `active` tinyint(1) NOT NULL,
  `outbuffers` varchar(255) NOT NULL,
  `backgr_delay` int(11) NOT NULL,
  `dilation` int(11) NOT NULL,
  `erosion` int(11) NOT NULL,
  `max_size` int(11) NOT NULL,
  `threshold` int(11) NOT NULL,
  `max_rect` int(11) NOT NULL,
  `eventer` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_detector`
--

LOCK TABLES `c_client_detector` WRITE;
/*!40000 ALTER TABLE `c_client_detector` DISABLE KEYS */;
INSERT INTO `c_client_detector` VALUES (1,'RaspiCAM','2020-10-02 18:49:05.000000','2020-10-09 07:06:32.878206',2560,1440,0,3.9756017824803833,0,'[[\"V\",3]]',3,20,1,100,25,10,1),(2,'Moneno','2020-10-02 18:49:05.000000','2020-10-30 15:29:23.454706',1280,800,0,4.952188281161706,1,'[[\"V\",4]]',1,30,1,100,40,20,2);
/*!40000 ALTER TABLE `c_client_detector` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_epoch`
--

DROP TABLE IF EXISTS `c_client_epoch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_epoch` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fit_id` int(11) NOT NULL,
  `loss` double NOT NULL,
  `cmetrics` double NOT NULL,
  `val_loss` double NOT NULL,
  `val_cmetrics` double NOT NULL,
  `hit100` double NOT NULL,
  `val_hit100` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `c_client_epoch_fit_id_14d2f630` (`fit_id`),
  CONSTRAINT `c_client_epoch_fit_id_14d2f630_fk_c_client_fit_id` FOREIGN KEY (`fit_id`) REFERENCES `c_client_fit` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=159 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_epoch`
--

LOCK TABLES `c_client_epoch` WRITE;
/*!40000 ALTER TABLE `c_client_epoch` DISABLE KEYS */;
/*!40000 ALTER TABLE `c_client_epoch` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_event`
--

DROP TABLE IF EXISTS `c_client_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `start` datetime(6) NOT NULL,
  `end` datetime(6) NOT NULL,
  `xmin` int(11) NOT NULL,
  `xmax` int(11) NOT NULL,
  `ymin` int(11) NOT NULL,
  `ymax` int(11) NOT NULL,
  `numframes` int(11) NOT NULL,
  `school_id` int(11) NOT NULL,
  `locktime` datetime(6) DEFAULT NULL,
  `userlock_id` int(11) DEFAULT NULL,
  `done` tinyint(1) NOT NULL,
  `videoclip` varchar(256) NOT NULL,
  `double` tinyint(1) NOT NULL,
  `p_string` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `c_client_event_tfmodel_id_36215e7d_fk_c_client_tfmodel_id` (`school_id`),
  KEY `c_client_event_userlock_id_94202566_fk_auth_user_id` (`userlock_id`),
  CONSTRAINT `c_client_event_school_id_f06e98b6_fk_c_client_school_id` FOREIGN KEY (`school_id`) REFERENCES `c_client_school` (`id`),
  CONSTRAINT `c_client_event_userlock_id_94202566_fk_auth_user_id` FOREIGN KEY (`userlock_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=56837 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_event`
--

LOCK TABLES `c_client_event` WRITE;
/*!40000 ALTER TABLE `c_client_event` DISABLE KEYS */;
/*!40000 ALTER TABLE `c_client_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_event_frame`
--

DROP TABLE IF EXISTS `c_client_event_frame`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_event_frame` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time` datetime(6) NOT NULL,
  `status` smallint(6) NOT NULL,
  `name` varchar(100) NOT NULL,
  `x1` int(11) NOT NULL,
  `x2` int(11) NOT NULL,
  `y1` int(11) NOT NULL,
  `y2` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `trainframe` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `c_client_event_frame_event_id_56ca45ef_fk_c_client_event_id` (`event_id`),
  CONSTRAINT `c_client_event_frame_event_id_56ca45ef_fk_c_client_event_id` FOREIGN KEY (`event_id`) REFERENCES `c_client_event` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9044 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_event_frame`
--

LOCK TABLES `c_client_event_frame` WRITE;
/*!40000 ALTER TABLE `c_client_event_frame` DISABLE KEYS */;
/*!40000 ALTER TABLE `c_client_event_frame` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_eventer`
--

DROP TABLE IF EXISTS `c_client_eventer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_eventer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `made` datetime(6) NOT NULL,
  `lastused` datetime(6) NOT NULL,
  `xres` int(11) NOT NULL,
  `yres` int(11) NOT NULL,
  `fpslimit` double NOT NULL,
  `fpsactual` double NOT NULL,
  `active` tinyint(1) NOT NULL,
  `outbuffers` varchar(255) NOT NULL,
  `school` int(11) NOT NULL,
  `margin` int(11) NOT NULL,
  `event_time_gap` int(11) NOT NULL,
  `alarm_email` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_eventer`
--

LOCK TABLES `c_client_eventer` WRITE;
/*!40000 ALTER TABLE `c_client_eventer` DISABLE KEYS */;
INSERT INTO `c_client_eventer` VALUES (1,'RaspiCAM','2020-10-09 12:54:28.000000','1899-12-31 23:07:00.000000',2560,1440,0,3.98510889656209,0,'[[\"V\",5]]',1,50,10,''),(2,'Moneno','2020-10-09 12:54:28.000000','2020-10-30 15:29:23.460995',1280,800,0,5.006189214451475,1,'[[\"V\",6]]',1,30,2,'');
/*!40000 ALTER TABLE `c_client_eventer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_evt_condition`
--

DROP TABLE IF EXISTS `c_client_evt_condition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_evt_condition` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reaction` int(11) NOT NULL,
  `and_or` int(11) NOT NULL,
  `c_type` int(11) NOT NULL,
  `x` int(11) NOT NULL,
  `y` double NOT NULL,
  `eventer_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `c_client_evt_conditi_eventer_id_a6858eb4_fk_c_client_` (`eventer_id`),
  CONSTRAINT `c_client_evt_conditi_eventer_id_a6858eb4_fk_c_client_` FOREIGN KEY (`eventer_id`) REFERENCES `c_client_eventer` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=221 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_evt_condition`
--

LOCK TABLES `c_client_evt_condition` WRITE;
/*!40000 ALTER TABLE `c_client_evt_condition` DISABLE KEYS */;
/*!40000 ALTER TABLE `c_client_evt_condition` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_fit`
--

DROP TABLE IF EXISTS `c_client_fit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_fit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `made` datetime(6) NOT NULL,
  `minutes` double NOT NULL,
  `school` int(11) NOT NULL,
  `epochs` int(11) NOT NULL,
  `nr_tr` int(11) NOT NULL,
  `nr_va` int(11) NOT NULL,
  `loss` double NOT NULL,
  `cmetrics` double NOT NULL,
  `val_loss` double NOT NULL,
  `val_cmetrics` double NOT NULL,
  `cputemp` double NOT NULL,
  `cpufan1` double NOT NULL,
  `cpufan2` double NOT NULL,
  `gputemp` double NOT NULL,
  `gpufan` double NOT NULL,
  `description` longtext NOT NULL,
  `hit100` double NOT NULL,
  `val_hit100` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=166 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_fit`
--

LOCK TABLES `c_client_fit` WRITE;
/*!40000 ALTER TABLE `c_client_fit` DISABLE KEYS */;
/*!40000 ALTER TABLE `c_client_fit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_mask`
--

DROP TABLE IF EXISTS `c_client_mask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_mask` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `definition` varchar(500) NOT NULL,
  `cam_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `c_client_mask_cam_id_7023d74b_fk_c_client_cam_id` (`cam_id`),
  CONSTRAINT `c_client_mask_cam_id_7023d74b_fk_c_client_cam_id` FOREIGN KEY (`cam_id`) REFERENCES `c_client_cam` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=313 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_mask`
--

LOCK TABLES `c_client_mask` WRITE;
/*!40000 ALTER TABLE `c_client_mask` DISABLE KEYS */;
/*!40000 ALTER TABLE `c_client_mask` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_repeater`
--

DROP TABLE IF EXISTS `c_client_repeater`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_repeater` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_repeater`
--

LOCK TABLES `c_client_repeater` WRITE;
/*!40000 ALTER TABLE `c_client_repeater` DISABLE KEYS */;
/*!40000 ALTER TABLE `c_client_repeater` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_school`
--

DROP TABLE IF EXISTS `c_client_school`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_school` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `size` int(11) NOT NULL,
  `dir` varchar(256) NOT NULL,
  `trigger` int(11) NOT NULL,
  `lastfile` datetime(6) NOT NULL,
  `active` int(11) NOT NULL,
  `last_id_mf` int(11) NOT NULL,
  `last_id_of` int(11) NOT NULL,
  `do_filter` tinyint(1) NOT NULL,
  `load_model_nr` smallint(6) NOT NULL,
  `train_on_all` tinyint(1) NOT NULL,
  `used_by_others` tinyint(1) NOT NULL,
  `l_rate_max` varchar(20) NOT NULL,
  `l_rate_min` varchar(20) NOT NULL,
  `e_school` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_school`
--

LOCK TABLES `c_client_school` WRITE;
/*!40000 ALTER TABLE `c_client_school` DISABLE KEYS */;
INSERT INTO `c_client_school` VALUES (1,'Standard',0,'~/sftp/c_model_1/',500,'2021-03-12 12:50:04.337680',1,513,513,0,3,0,1,'-1','1e-6',4);
/*!40000 ALTER TABLE `c_client_school` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_setting`
--

DROP TABLE IF EXISTS `c_client_setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_setting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `setting` varchar(100) NOT NULL,
  `index` smallint(6) NOT NULL,
  `value` varchar(100) NOT NULL,
  `comment` varchar(256) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_setting`
--

LOCK TABLES `c_client_setting` WRITE;
/*!40000 ALTER TABLE `c_client_setting` DISABLE KEYS */;
INSERT INTO `c_client_setting` VALUES (1,'tr_epochs',0,'1','Training'),(4,'last_model',0,'1','Nothing yet...'),(5,'schoolframespath',0,'~/sftp/school/','...'),(6,'maxtemp',0,'100','Max CPU Temp'),(7,'last_school',0,'2','Nothing yet...'),(8,'tr_xdim',0,'331','...'),(9,'tr_ydim',0,'331','...'),(10,'tpu',0,'Nein','Coral presence'),(11,'gpu',0,'Nein','Geforce presence'),(12,'gpu_sim',0,'0.1','-1 is off'),(13,'logdir',0,'log/','...'),(14,'loglevel',0,'INFO','...'),(15,'basemodelpath',0,'0','...'),(16,'recordingspath',0,'0','Place for videos'),(17,'recordingsurl',0,'http://localhost/vclips/','Url for videos'),(18,'smtp_account',0,'alarm@cam-ai.de','...'),(19,'smtp_password',0,'Grmbl!123_Wmpf','...'),(20,'smtp_email',0,'alarm@cam-ai.de','...'),(21,'smtp_server',0,'smtp.strato.com','...'),(22,'smtp_port',0,'465','...'),(23,'smtp_name',0,'CAM-AI Emailer','...'),(24,'client_url',0,'http://localhost:8000/c_client/','...'),(25,'tfw_savestats',0,'0','seconds'),(26,'tfw_maxblock',0,'8','...'),(27,'tfw_timeout',0,'1','seconds to wait'),(28,'gpu_sim_loading',0,'0','...'),(29,'tfw_wsurl',0,'','For getting predictions'),(30,'tfw_wsname',0,'','For getting predictions'),(31,'tfw_wspass',0,'','For getting predictions');
/*!40000 ALTER TABLE `c_client_setting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_stream`
--

DROP TABLE IF EXISTS `c_client_stream`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_stream` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `made` datetime(6) NOT NULL,
  `lastused` datetime(6) NOT NULL,
  `cam_xres` int(11) NOT NULL,
  `cam_yres` int(11) NOT NULL,
  `cam_fpslimit` double NOT NULL,
  `cam_fpsactual` double NOT NULL,
  `cam_active` tinyint(1) NOT NULL,
  `cam_feed_type` int(11) NOT NULL,
  `cam_url` varchar(256) NOT NULL,
  `cam_apply_mask` tinyint(1) NOT NULL,
  `cam_repeater` int(11) NOT NULL,
  `det_active` tinyint(1) NOT NULL,
  `det_backgr_delay` int(11) NOT NULL,
  `det_dilation` int(11) NOT NULL,
  `det_erosion` int(11) NOT NULL,
  `det_fpsactual` double NOT NULL,
  `det_max_rect` int(11) NOT NULL,
  `det_max_size` int(11) NOT NULL,
  `det_threshold` int(11) NOT NULL,
  `evt_active` tinyint(1) NOT NULL,
  `evt_alarm_email` varchar(255) NOT NULL,
  `evt_event_time_gap` int(11) NOT NULL,
  `evt_fpsactual` double NOT NULL,
  `evt_margin` int(11) NOT NULL,
  `evt_school` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_stream`
--

LOCK TABLES `c_client_stream` WRITE;
/*!40000 ALTER TABLE `c_client_stream` DISABLE KEYS */;
/*!40000 ALTER TABLE `c_client_stream` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_tag`
--

DROP TABLE IF EXISTS `c_client_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` varchar(100) NOT NULL,
  `school` smallint(6) NOT NULL,
  `replaces` smallint(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_tag`
--

LOCK TABLES `c_client_tag` WRITE;
/*!40000 ALTER TABLE `c_client_tag` DISABLE KEYS */;
INSERT INTO `c_client_tag` VALUES (0,'night','Night',1,-1),(1,'human','Human(s)',1,-1),(2,'cat','Cat(s)',1,-1),(3,'dog','Dog(s)',1,-1),(4,'bird','Bird(s)',1,-1),(5,'insect','Insect(s)',1,-1),(6,'car','Car(s)',1,-1),(7,'truck','Truck(s)',1,-1),(8,'motorcycle','Motorcycle(s)',1,-1),(9,'bicycle','Bicycle(s)',1,-1),(10,'squirrel','Squirrel(s)',3,8);
/*!40000 ALTER TABLE `c_client_tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_trainframe`
--

DROP TABLE IF EXISTS `c_client_trainframe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_trainframe` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `made` datetime(6) NOT NULL,
  `school` smallint(6) NOT NULL,
  `name` varchar(256) NOT NULL,
  `code` varchar(2) NOT NULL,
  `c0` smallint(6) NOT NULL,
  `c1` smallint(6) NOT NULL,
  `c2` smallint(6) NOT NULL,
  `c3` smallint(6) NOT NULL,
  `c4` smallint(6) NOT NULL,
  `c5` smallint(6) NOT NULL,
  `c6` smallint(6) NOT NULL,
  `c7` smallint(6) NOT NULL,
  `c8` smallint(6) NOT NULL,
  `c9` smallint(6) NOT NULL,
  `checked` smallint(6) NOT NULL,
  `made_by_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `c_client_trainframe_made_by_id_d6899032_fk_auth_user_id` (`made_by_id`),
  CONSTRAINT `c_client_trainframe_made_by_id_d6899032_fk_auth_user_id` FOREIGN KEY (`made_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1146 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_trainframe`
--

LOCK TABLES `c_client_trainframe` WRITE;
/*!40000 ALTER TABLE `c_client_trainframe` DISABLE KEYS */;
/*!40000 ALTER TABLE `c_client_trainframe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_userinfo`
--

DROP TABLE IF EXISTS `c_client_userinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_userinfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `counter` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `school_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `c_client_userinfo_user_id_d4de57f8_fk_auth_user_id` (`user_id`),
  KEY `c_client_userinfo_school_id_9153b332_fk_c_client_school_id` (`school_id`),
  CONSTRAINT `c_client_userinfo_school_id_9153b332_fk_c_client_school_id` FOREIGN KEY (`school_id`) REFERENCES `c_client_school` (`id`),
  CONSTRAINT `c_client_userinfo_user_id_d4de57f8_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_userinfo`
--

LOCK TABLES `c_client_userinfo` WRITE;
/*!40000 ALTER TABLE `c_client_userinfo` DISABLE KEYS */;
INSERT INTO `c_client_userinfo` VALUES (1,68,1,1);
/*!40000 ALTER TABLE `c_client_userinfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_view`
--

DROP TABLE IF EXISTS `c_client_view`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_view` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `made` datetime(6) NOT NULL,
  `lastused` datetime(6) NOT NULL,
  `xres` int(11) NOT NULL,
  `yres` int(11) NOT NULL,
  `fpslimit` double NOT NULL,
  `fpsactual` double NOT NULL,
  `active` tinyint(1) NOT NULL,
  `outbuffers` varchar(255) NOT NULL,
  `source_type` varchar(1) NOT NULL,
  `source_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_view`
--

LOCK TABLES `c_client_view` WRITE;
/*!40000 ALTER TABLE `c_client_view` DISABLE KEYS */;
INSERT INTO `c_client_view` VALUES (1,'RaspiCAM','2020-09-26 14:52:21.000000','2020-10-09 07:06:32.869012',2560,1440,0,1.8789295995505821,0,'[]','C',2),(2,'Moneno','2020-09-26 14:52:21.000000','2020-10-30 15:29:23.445574',1280,800,0,2.4186659907849837,1,'[]','C',5),(3,'RaspiCAM','2020-09-26 14:52:21.000000','2020-10-09 07:06:34.741830',2560,1440,0,0.8913455185198383,0,'[]','D',2),(4,'Moneno','2020-09-26 14:52:21.000000','2020-10-30 15:29:23.583835',1280,800,0,2.5983668046681263,1,'[]','D',5),(5,'RaspiCAM','2020-09-26 14:52:21.000000','2020-10-07 19:43:58.000000',2560,1440,0,0.95,0,'[]','E',2),(6,'Moneno','2020-09-26 14:52:21.000000','2020-10-30 15:29:23.470844',1280,800,0,2.3827438827230023,1,'[]','E',5);
/*!40000 ALTER TABLE `c_client_view` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `c_client_view_log`
--

DROP TABLE IF EXISTS `c_client_view_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `c_client_view_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `v_type` varchar(1) NOT NULL,
  `v_id` int(11) NOT NULL,
  `start` datetime(6) NOT NULL,
  `stop` datetime(6) NOT NULL,
  `user` int(11) NOT NULL,
  `active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4125 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_client_view_log`
--

LOCK TABLES `c_client_view_log` WRITE;
/*!40000 ALTER TABLE `c_client_view_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `c_client_view_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=83 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(23,'c_client','access_control'),(17,'c_client','cam'),(7,'c_client','camera'),(19,'c_client','detector'),(12,'c_client','epoch'),(15,'c_client','event'),(20,'c_client','eventer'),(16,'c_client','event_frame'),(22,'c_client','evt_condition'),(13,'c_client','fit'),(21,'c_client','mask'),(25,'c_client','repeater'),(9,'c_client','school'),(11,'c_client','setting'),(27,'c_client','stream'),(8,'c_client','tag'),(10,'c_client','trainframe'),(14,'c_client','userinfo'),(24,'c_client','videoclip'),(18,'c_client','view'),(26,'c_client','view_log'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=140 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2020-08-09 16:09:34.278901'),(2,'auth','0001_initial','2020-08-09 16:09:34.395222'),(3,'admin','0001_initial','2020-08-09 16:09:34.668082'),(4,'admin','0002_logentry_remove_auto_add','2020-08-09 16:09:34.762647'),(5,'admin','0003_logentry_add_action_flag_choices','2020-08-09 16:09:34.772824'),(6,'contenttypes','0002_remove_content_type_name','2020-08-09 16:09:34.830118'),(7,'auth','0002_alter_permission_name_max_length','2020-08-09 16:09:34.868446'),(8,'auth','0003_alter_user_email_max_length','2020-08-09 16:09:34.879971'),(9,'auth','0004_alter_user_username_opts','2020-08-09 16:09:34.888848'),(10,'auth','0005_alter_user_last_login_null','2020-08-09 16:09:34.922303'),(11,'auth','0006_require_contenttypes_0002','2020-08-09 16:09:34.925730'),(12,'auth','0007_alter_validators_add_error_messages','2020-08-09 16:09:34.935945'),(13,'auth','0008_alter_user_username_max_length','2020-08-09 16:09:34.972240'),(14,'auth','0009_alter_user_last_name_max_length','2020-08-09 16:09:35.012967'),(15,'auth','0010_alter_group_name_max_length','2020-08-09 16:09:35.023384'),(16,'auth','0011_update_proxy_permissions','2020-08-09 16:09:35.033116'),(17,'auth','0012_alter_user_first_name_max_length','2020-08-09 16:09:35.070145'),(18,'c_client','0001_initial','2020-08-09 16:09:35.084612'),(19,'sessions','0001_initial','2020-08-09 16:09:35.101878'),(20,'c_client','0002_auto_20200814_1108','2020-08-14 09:10:40.398115'),(21,'c_client','0003_tag','2020-08-21 12:32:34.008205'),(22,'c_client','0004_tfmodel','2020-08-21 13:13:05.403403'),(23,'c_client','0005_trainframe','2020-08-25 12:40:35.135444'),(24,'c_client','0006_auto_20200825_1448','2020-08-25 12:48:26.631177'),(25,'c_client','0007_setting','2020-08-25 15:16:59.357082'),(26,'c_client','0008_epoch_fit','2020-09-07 19:18:52.862723'),(27,'c_client','0009_auto_20200907_2127','2020-09-07 19:27:21.596335'),(28,'c_client','0010_auto_20200909_1118','2020-09-09 09:19:54.377933'),(29,'c_client','0011_remove_tfmodel_lastclean','2020-09-09 10:51:50.020516'),(30,'c_client','0012_auto_20200909_1303','2020-09-09 11:03:26.317104'),(31,'c_client','0013_auto_20200909_1304','2020-09-09 11:04:40.652167'),(32,'c_client','0014_auto_20200909_1305','2020-09-09 11:05:12.090990'),(33,'c_client','0015_auto_20200909_1308','2020-09-09 11:08:11.177310'),(34,'c_client','0016_auto_20200909_1313','2020-09-09 11:13:21.349235'),(35,'c_client','0017_auto_20200909_1313','2020-09-09 11:13:45.999198'),(36,'c_client','0018_auto_20200909_1313','2020-09-09 11:13:58.768282'),(37,'c_client','0019_auto_20200909_1314','2020-09-09 11:14:10.100205'),(38,'c_client','0020_auto_20200909_1314','2020-09-09 11:14:49.557843'),(39,'c_client','0021_auto_20200909_1315','2020-09-09 11:15:12.054084'),(40,'c_client','0022_auto_20200912_1100','2020-09-12 09:00:25.934170'),(41,'c_client','0023_event','2020-09-12 10:36:40.407920'),(42,'c_client','0024_auto_20200912_1242','2020-09-12 10:43:07.371864'),(43,'c_client','0025_event_frame_trainframe','2020-09-21 12:56:58.222874'),(44,'c_client','0025_event_frame_train','2020-09-21 13:23:48.287224'),(45,'c_client','0026_remove_event_frame_train','2020-09-21 13:24:11.806599'),(46,'c_client','0027_event_frame_trainframe','2020-09-21 13:24:56.320720'),(47,'c_client','0028_auto_20200921_1639','2020-09-21 14:40:01.747388'),(48,'c_client','0029_auto_20200921_1652','2020-09-21 14:53:02.142110'),(49,'c_client','0030_cam','2020-09-23 15:46:54.199257'),(50,'c_client','0031_auto_20200923_1952','2020-09-23 17:52:33.965668'),(51,'c_client','0032_auto_20200923_2019','2020-09-23 18:19:33.896412'),(52,'c_client','0033_auto_20200923_2020','2020-09-23 18:20:52.971200'),(53,'c_client','0034_auto_20200923_2022','2020-09-23 18:22:08.682561'),(54,'c_client','0035_auto_20200923_2058','2020-09-23 18:58:44.909539'),(55,'c_client','0036_cam_feed_type','2020-09-23 19:40:44.118268'),(56,'c_client','0037_view','2020-09-26 14:44:35.758200'),(57,'c_client','0038_auto_20200930_1430','2020-09-30 12:31:12.031386'),(58,'c_client','0039_auto_20200930_1431','2020-09-30 12:31:28.020754'),(59,'c_client','0040_auto_20200930_1457','2020-09-30 12:57:51.043258'),(60,'c_client','0041_cam_view_out','2020-09-30 13:01:41.610089'),(61,'c_client','0042_remove_cam_view_out','2020-09-30 13:07:31.687374'),(62,'c_client','0043_cam_view_out','2020-09-30 13:10:05.616280'),(63,'c_client','0044_remove_cam_view_out','2020-09-30 13:30:10.104023'),(64,'c_client','0045_auto_20200930_1531','2020-09-30 13:32:00.801960'),(65,'c_client','0046_auto_20200930_1535','2020-09-30 13:35:51.155023'),(66,'c_client','0047_auto_20200930_1538','2020-09-30 13:38:25.661162'),(67,'c_client','0048_auto_20200930_1538','2020-09-30 13:38:39.575293'),(68,'c_client','0049_delete_camera','2020-09-30 17:20:58.933610'),(69,'c_client','0050_auto_20201002_1837','2020-10-02 16:38:12.967159'),(70,'c_client','0051_auto_20201002_1907','2020-10-02 17:07:55.874034'),(71,'c_client','0052_auto_20201002_1910','2020-10-02 17:10:16.584536'),(72,'c_client','0053_view_source_type','2020-10-02 17:38:02.737435'),(73,'c_client','0054_detctor','2020-10-02 18:36:43.268128'),(74,'c_client','0055_auto_20201002_2037','2020-10-02 18:37:13.242614'),(75,'c_client','0056_eventer','2020-10-09 12:40:23.529076'),(76,'c_client','0057_detector_eventer','2020-10-09 13:15:00.671532'),(77,'c_client','0058_auto_20201009_2123','2020-10-09 19:23:52.729076'),(78,'c_client','0059_auto_20201009_2128','2020-10-09 19:28:23.210486'),(79,'c_client','0060_auto_20201010_1024','2020-10-10 08:25:02.457701'),(80,'c_client','0061_auto_20201010_1046','2020-10-10 08:47:02.628077'),(81,'c_client','0062_auto_20201010_1052','2020-10-10 08:52:10.664520'),(82,'c_client','0063_auto_20201010_1128','2020-10-10 09:28:48.639944'),(83,'c_client','0064_auto_20201010_1808','2020-10-10 16:09:50.054400'),(84,'c_client','0065_userinfo_school','2020-10-10 16:15:59.289141'),(85,'c_client','0066_auto_20201022_1409','2020-10-22 12:10:06.610997'),(86,'c_client','0067_auto_20201022_1448','2020-10-22 12:48:16.073594'),(87,'c_client','0068_auto_20201022_1503','2020-10-22 13:03:19.838900'),(88,'c_client','0069_auto_20201022_2112','2020-10-22 19:12:24.044915'),(89,'c_client','0070_view_source_id','2020-10-25 16:35:19.263844'),(90,'c_client','0071_cam_fps_div','2020-10-31 08:53:42.637519'),(91,'c_client','0072_auto_20201116_1205','2020-11-16 11:07:54.452064'),(92,'c_client','0073_auto_20201116_1207','2020-11-16 11:07:54.498029'),(93,'c_client','0074_mask_cam','2020-11-16 11:19:40.126236'),(94,'c_client','0075_view_apply_mask','2020-11-29 15:00:31.505467'),(95,'c_client','0076_auto_20201129_1601','2020-11-29 15:01:53.855096'),(96,'c_client','0077_auto_20201202_1301','2020-12-02 12:02:08.557800'),(97,'c_client','0078_auto_20201203_1647','2020-12-03 15:49:21.950145'),(98,'c_client','0079_evt_condition_reaction','2020-12-03 16:09:51.339728'),(99,'c_client','0080_auto_20201225_2123','2020-12-25 20:24:16.354910'),(100,'c_client','0081_auto_20201225_2146','2020-12-25 20:46:20.922465'),(101,'c_client','0082_auto_20201229_1759','2020-12-29 16:59:24.537217'),(102,'c_client','0083_access_control','2020-12-30 12:56:07.396723'),(103,'c_client','0084_trainframe_made_by','2020-12-31 11:06:43.067838'),(104,'c_client','0085_remove_event_end2','2021-01-05 12:46:19.173877'),(105,'c_client','0086_auto_20210107_1222','2021-01-07 11:22:33.304555'),(106,'c_client','0087_event_done','2021-01-17 12:00:02.051891'),(107,'c_client','0088_auto_20210119_0941','2021-01-19 08:41:57.326086'),(108,'c_client','0089_videoclip_num_views','2021-01-20 14:47:07.059746'),(109,'c_client','0090_auto_20210123_1948','2021-01-23 18:49:07.634646'),(110,'c_client','0091_auto_20210123_1948','2021-01-23 18:49:07.651371'),(111,'c_client','0092_event_double','2021-01-28 19:32:04.519182'),(112,'c_client','0093_eventer_alarm_email','2021-01-29 15:45:13.890310'),(113,'c_client','0094_auto_20210130_1315','2021-01-30 12:15:47.267898'),(114,'c_client','0095_event_p_string','2021-02-07 11:51:18.874657'),(115,'c_client','0096_remove_cam_fps_div','2021-02-11 09:57:47.397126'),(116,'c_client','0097_auto_20210311_1949','2021-03-11 18:49:42.399034'),(117,'c_client','0098_auto_20210311_2101','2021-03-11 20:01:29.194048'),(118,'c_client','0099_auto_20210311_2103','2021-03-11 20:03:28.859922'),(119,'c_client','0100_remove_school_lastclean','2021-03-11 20:06:41.238891'),(120,'c_client','0101_remove_school_type','2021-03-11 22:17:05.406184'),(121,'c_client','0102_tag_school','2021-03-12 13:12:19.748781'),(122,'c_client','0103_tag_replaces','2021-03-12 13:26:49.966311'),(123,'c_client','0104_repeater','2021-03-18 15:53:49.181538'),(124,'c_client','0105_repeater_active','2021-03-18 18:40:48.841707'),(125,'c_client','0106_auto_20210319_1119','2021-03-19 10:20:06.590688'),(126,'c_client','0107_auto_20210319_1834','2021-03-19 17:34:28.583464'),(127,'c_client','0108_auto_20210323_1706','2021-03-23 16:07:07.517456'),(128,'c_client','0109_view_log','2021-04-06 15:35:13.781047'),(129,'c_client','0110_school_e_school','2021-05-18 13:54:37.600951'),(130,'c_client','0111_stream','2021-06-24 18:28:08.699642'),(131,'c_client','0112_auto_20210624_2035','2021-06-24 18:36:07.289917'),(132,'c_client','0113_auto_20210624_2036','2021-06-24 18:36:07.299211'),(133,'c_client','0114_auto_20210624_2036','2021-06-24 18:36:59.324618'),(134,'c_client','0115_auto_20210624_2038','2021-06-24 18:39:02.894756'),(135,'c_client','0116_auto_20210624_2041','2021-06-24 18:41:31.984641'),(136,'c_client','0117_auto_20210624_2045','2021-06-24 18:48:15.618131'),(137,'c_client','0118_auto_20210624_2048','2021-06-24 18:48:15.628816'),(138,'c_client','0119_auto_20210624_2053','2021-06-24 18:53:09.340389'),(139,'c_client','0120_auto_20210624_2058','2021-06-24 18:58:27.686267');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'C-SERVER-NEW'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-10-11 15:29:12
