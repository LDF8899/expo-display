
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
DROP TABLE IF EXISTS `achievement_market_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `achievement_market_config` (
  `id` tinyint NOT NULL DEFAULT '1',
  `welcome_title` varchar(255) NOT NULL DEFAULT '成果超市',
  `welcome_subtitle` varchar(255) NOT NULL DEFAULT '',
  `welcome_intro` text NOT NULL,
  `welcome_image_url` varchar(1024) NOT NULL DEFAULT '',
  `welcome_note` varchar(255) NOT NULL DEFAULT '',
  `updated_at` varchar(40) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `achievement_market_config` WRITE;
/*!40000 ALTER TABLE `achievement_market_config` DISABLE KEYS */;
INSERT INTO `achievement_market_config` VALUES (1,'成果超市','欢迎进入校园成果展示现场','选择一个主题展区，查看名师名匠、优秀校友、优秀学生、创新成果与荣誉资质。每个展示项目都可生成二维码，扫码后进入对应展示详情。','','现场扫码进入项目详情 · 后台审核通过后方可发布','2026-08-11T09:19:25.334432+00:00');
/*!40000 ALTER TABLE `achievement_market_config` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `achievement_market_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `achievement_market_items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `project_id` bigint NOT NULL,
  `page_id` bigint NOT NULL,
  `category_key` varchar(40) NOT NULL,
  `intro` varchar(512) NOT NULL DEFAULT '',
  `sort_order` int NOT NULL DEFAULT '0',
  `enabled` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` varchar(40) NOT NULL,
  `updated_at` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_achievement_market_page` (`page_id`),
  KEY `idx_achievement_market_project` (`project_id`,`enabled`,`sort_order`),
  KEY `idx_achievement_market_category` (`category_key`,`enabled`,`sort_order`),
  CONSTRAINT `fk_achievement_market_page` FOREIGN KEY (`page_id`) REFERENCES `pages` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_achievement_market_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `achievement_market_items` WRITE;
/*!40000 ALTER TABLE `achievement_market_items` DISABLE KEYS */;
INSERT INTO `achievement_market_items` VALUES (1,1,1,'innovation','聚焦技能培训、职业认定与乡村振兴服务，测试指标卡、图文组合与引用块。',30,1,'2026-07-13T02:59:45.752052+00:00','2026-07-13T02:59:45.752052+00:00'),(2,1,2,'innovation','从海外研学到职业标准输出，测试时间线、列表、图片和分隔线。',40,1,'2026-07-13T03:07:46.158420+00:00','2026-07-13T03:07:46.158420+00:00'),(3,1,3,'alumni','以人物卡片、荣誉标签和分段叙事展示优秀毕业生成长故事。',20,1,'2026-07-13T03:35:29.273403+00:00','2026-07-13T03:35:29.273403+00:00'),(4,1,4,'masters','用人物介绍、数据卡和成果列表展示名师名匠内容模板。',10,1,'2026-07-13T03:37:17.139551+00:00','2026-07-13T03:37:17.139551+00:00'),(11,1,5,'innovation','',0,1,'2026-08-11T09:58:25.559854+00:00','2026-08-11T09:58:25.559854+00:00');
/*!40000 ALTER TABLE `achievement_market_items` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `admin_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(64) NOT NULL DEFAULT '',
  `role` varchar(32) NOT NULL DEFAULT '',
  `action` varchar(80) NOT NULL,
  `target_type` varchar(80) NOT NULL DEFAULT '',
  `target_id` varchar(120) NOT NULL DEFAULT '',
  `target_label` varchar(255) NOT NULL DEFAULT '',
  `detail` text NOT NULL,
  `changes` varchar(2048) NOT NULL DEFAULT '',
  `ip` varchar(80) NOT NULL DEFAULT '',
  `created_at` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_admin_logs_created_at` (`created_at`),
  KEY `idx_admin_logs_username` (`username`),
  KEY `idx_admin_logs_action` (`action`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `admin_logs` WRITE;
/*!40000 ALTER TABLE `admin_logs` DISABLE KEYS */;
INSERT INTO `admin_logs` VALUES (1,'admin','admin','login','user','admin','admin','login','','127.0.0.1','2026-08-11T08:56:21.459329+00:00'),(2,'admin','admin','login','user','admin','admin','login','','127.0.0.1','2026-08-11T09:21:23.614662+00:00'),(3,'admin','admin','login','user','admin','admin','login','','127.0.0.1','2026-08-11T09:23:33.489113+00:00'),(4,'admin','admin','login','user','admin','admin','login','','127.0.0.1','2026-08-11T09:43:36.892006+00:00'),(5,'admin','admin','publish_achievement_market','achievement_market','0','成果超市','当前没有可发布的成果超市项目','','127.0.0.1','2026-08-11T09:43:37.043518+00:00'),(6,'admin','admin','login','user','admin','admin','login','','127.0.0.1','2026-08-11T09:55:57.083697+00:00'),(7,'admin','admin','login','user','admin','admin','login','','127.0.0.1','2026-08-11T09:57:32.578413+00:00'),(8,'admin','admin','delete_achievement_market_item','achievement_market_item','5','欢迎来到成果展示','delete item','','127.0.0.1','2026-08-11T09:57:50.476044+00:00'),(9,'admin','admin','save_achievement_market_item','achievement_market_item','11','欢迎来到成果展示','add/update item','','127.0.0.1','2026-08-11T09:58:25.678600+00:00'),(10,'admin','admin','login','user','admin','admin','login','','127.0.0.1','2026-08-11T10:10:56.738072+00:00'),(11,'admin','admin','create_achievement_market_item','achievement_market_item','12','????????','create item','','127.0.0.1','2026-08-11T10:10:56.992875+00:00'),(12,'admin','admin','login','user','admin','admin','login','','127.0.0.1','2026-08-11T10:11:21.318105+00:00'),(13,'admin','admin','login','user','admin','admin','login','','127.0.0.1','2026-08-11T10:11:37.620198+00:00'),(14,'admin','admin','create_achievement_market_item','achievement_market_item','13','Temp Market Item','create item','','127.0.0.1','2026-08-11T10:11:37.942895+00:00'),(15,'admin','admin','login','user','admin','admin','login','','127.0.0.1','2026-08-11T10:18:50.249918+00:00'),(16,'admin','admin','login','user','admin','admin','login','','127.0.0.1','2026-08-11T10:19:51.993176+00:00'),(17,'admin','admin','upload_asset','asset','b062f0e5b26743e180edaddf6e26cce5.jpg','e54deb52544a71ae0beb8a6ecc8ef993.jpg','image/jpeg -> /uploads/b062f0e5b26743e180edaddf6e26cce5.jpg (local)','','127.0.0.1','2026-08-11T10:21:42.373604+00:00'),(18,'admin','admin','upload_asset','asset','c60e0d1c70d34d78996632d15ce7aa15.jpg','download.jpg','image/jpeg -> /uploads/c60e0d1c70d34d78996632d15ce7aa15.jpg (local)','','127.0.0.1','2026-08-11T10:21:58.673593+00:00'),(19,'admin','admin','save_content_item','content_item','6','222','project 13','structured-content','127.0.0.1','2026-08-11T10:22:01.992277+00:00'),(20,'admin','admin','upload_asset','asset','d2276a75d5c74b0780caa25732e1534f.jpg','e54deb52544a71ae0beb8a6ecc8ef993.jpg','image/jpeg -> /uploads/d2276a75d5c74b0780caa25732e1534f.jpg (local)','','127.0.0.1','2026-08-11T10:22:58.127141+00:00'),(21,'admin','admin','upload_asset','asset','0f008612d4e64aba8c8f08410cb904f7.jpg','e54deb52544a71ae0beb8a6ecc8ef993.jpg','image/jpeg -> /uploads/0f008612d4e64aba8c8f08410cb904f7.jpg (local)','','127.0.0.1','2026-08-11T10:23:03.190007+00:00'),(22,'admin','admin','upload_asset','asset','12d841efd1a74d8785c5a91b3f737fc1.png','企业微信截图_17847985096941.png','image/png -> /uploads/12d841efd1a74d8785c5a91b3f737fc1.png (local)','','127.0.0.1','2026-08-11T10:24:19.629853+00:00'),(23,'admin','admin','upload_asset','asset','211d952b80ec471ca2cbafb9e877169f.png','企业微信截图_17847985096941.png','image/png -> /uploads/211d952b80ec471ca2cbafb9e877169f.png (local)','','127.0.0.1','2026-08-11T10:24:45.136684+00:00'),(24,'admin','admin','save_content_item','content_item','1','互动体验系统合集','project 11','structured-content','127.0.0.1','2026-08-11T10:24:54.708716+00:00'),(25,'admin','admin','save_page','page','overview','专题概况','project 11','content','127.0.0.1','2026-08-11T10:25:01.443306+00:00'),(26,'admin','admin','upload_asset','asset','c4fb063eefd0478eafc7a373e75b2d16.jpg','e54deb52544a71ae0beb8a6ecc8ef993.jpg','image/jpeg -> /uploads/c4fb063eefd0478eafc7a373e75b2d16.jpg (local)','','127.0.0.1','2026-08-11T10:25:42.122457+00:00'),(27,'admin','admin','upload_asset','asset','60f3798d1c7b47628c2f7004c28d978e.jpg','download.jpg','image/jpeg -> /uploads/60f3798d1c7b47628c2f7004c28d978e.jpg (local)','','127.0.0.1','2026-08-11T10:25:54.806683+00:00'),(28,'admin','admin','upload_asset','asset','8d45276947824cc4ac9a72a2bb398bf1.png','企业微信截图_17847985096941.png','image/png -> /uploads/8d45276947824cc4ac9a72a2bb398bf1.png (local)','','127.0.0.1','2026-08-11T10:26:17.129960+00:00'),(29,'admin','admin','save_content_item','content_item','7','2223','project 7','structured-content','127.0.0.1','2026-08-11T10:26:19.948089+00:00'),(30,'admin','admin','save_content_item','content_item','7','2223','project 7','structured-content','127.0.0.1','2026-08-11T10:26:41.796031+00:00'),(31,'admin','admin','save_page','page','overview','','project 7','content','127.0.0.1','2026-08-11T10:26:43.475666+00:00'),(32,'admin','admin','save_page','page','competitions','','project 7','content','127.0.0.1','2026-08-11T10:26:43.696709+00:00');
/*!40000 ALTER TABLE `admin_logs` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `admin_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_users` (
  `username` varchar(64) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `updated_at` varchar(40) NOT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `admin_users` WRITE;
/*!40000 ALTER TABLE `admin_users` DISABLE KEYS */;
INSERT INTO `admin_users` VALUES ('admin','pbkdf2_sha256$120000$eef292529907de51f240c2a4ed26e8d7$79a205239e0f64f1c757ac606ca0b8fbb3b894022232bf18ddcdaa2283ab4b50','2026-08-11T10:09:40.798212+00:00');
/*!40000 ALTER TABLE `admin_users` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `assets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assets` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `owner_username` varchar(64) NOT NULL DEFAULT '',
  `original_filename` varchar(255) NOT NULL DEFAULT '',
  `storage_key` varchar(1024) NOT NULL,
  `url` varchar(2048) NOT NULL,
  `mime_type` varchar(120) NOT NULL DEFAULT '',
  `size_bytes` bigint NOT NULL DEFAULT '0',
  `backend` varchar(40) NOT NULL DEFAULT 'local',
  `created_at` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_assets_owner_created` (`owner_username`,`created_at`),
  KEY `idx_assets_created_at` (`created_at`),
  CONSTRAINT `fk_assets_owner` FOREIGN KEY (`owner_username`) REFERENCES `users` (`username`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `assets` WRITE;
/*!40000 ALTER TABLE `assets` DISABLE KEYS */;
INSERT INTO `assets` VALUES (1,'admin','e54deb52544a71ae0beb8a6ecc8ef993.jpg','b062f0e5b26743e180edaddf6e26cce5.jpg','/uploads/b062f0e5b26743e180edaddf6e26cce5.jpg','image/jpeg',275235,'local','2026-08-11T10:21:42.275128+00:00'),(2,'admin','download.jpg','c60e0d1c70d34d78996632d15ce7aa15.jpg','/uploads/c60e0d1c70d34d78996632d15ce7aa15.jpg','image/jpeg',112864,'local','2026-08-11T10:21:58.582214+00:00'),(3,'admin','e54deb52544a71ae0beb8a6ecc8ef993.jpg','d2276a75d5c74b0780caa25732e1534f.jpg','/uploads/d2276a75d5c74b0780caa25732e1534f.jpg','image/jpeg',275235,'local','2026-08-11T10:22:58.062094+00:00'),(4,'admin','e54deb52544a71ae0beb8a6ecc8ef993.jpg','0f008612d4e64aba8c8f08410cb904f7.jpg','/uploads/0f008612d4e64aba8c8f08410cb904f7.jpg','image/jpeg',275235,'local','2026-08-11T10:23:03.066728+00:00'),(5,'admin','企业微信截图_17847985096941.png','12d841efd1a74d8785c5a91b3f737fc1.png','/uploads/12d841efd1a74d8785c5a91b3f737fc1.png','image/png',989897,'local','2026-08-11T10:24:19.490223+00:00'),(6,'admin','企业微信截图_17847985096941.png','211d952b80ec471ca2cbafb9e877169f.png','/uploads/211d952b80ec471ca2cbafb9e877169f.png','image/png',989897,'local','2026-08-11T10:24:44.982492+00:00'),(7,'admin','e54deb52544a71ae0beb8a6ecc8ef993.jpg','c4fb063eefd0478eafc7a373e75b2d16.jpg','/uploads/c4fb063eefd0478eafc7a373e75b2d16.jpg','image/jpeg',275235,'local','2026-08-11T10:25:42.021998+00:00'),(8,'admin','download.jpg','60f3798d1c7b47628c2f7004c28d978e.jpg','/uploads/60f3798d1c7b47628c2f7004c28d978e.jpg','image/jpeg',112864,'local','2026-08-11T10:25:54.690296+00:00'),(9,'admin','企业微信截图_17847985096941.png','8d45276947824cc4ac9a72a2bb398bf1.png','/uploads/8d45276947824cc4ac9a72a2bb398bf1.png','image/png',989897,'local','2026-08-11T10:26:17.020590+00:00');
/*!40000 ALTER TABLE `assets` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `content_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `content_assignments` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `project_id` bigint NOT NULL,
  `teacher_username` varchar(64) NOT NULL,
  `module_key` varchar(80) NOT NULL,
  `content_type` varchar(32) NOT NULL DEFAULT 'article',
  `title` varchar(255) NOT NULL,
  `description` varchar(1024) NOT NULL DEFAULT '',
  `status` varchar(32) NOT NULL DEFAULT 'assigned',
  `latest_record_id` bigint DEFAULT NULL,
  `content_item_id` bigint DEFAULT NULL,
  `created_by` varchar(64) NOT NULL DEFAULT '',
  `created_at` varchar(40) NOT NULL,
  `updated_at` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_content_assignments_project` (`project_id`,`module_key`,`status`),
  KEY `idx_content_assignments_teacher` (`teacher_username`,`status`),
  KEY `fk_content_assignments_record` (`latest_record_id`),
  KEY `fk_content_assignments_item` (`content_item_id`),
  CONSTRAINT `fk_content_assignments_item` FOREIGN KEY (`content_item_id`) REFERENCES `content_items` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_content_assignments_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_content_assignments_record` FOREIGN KEY (`latest_record_id`) REFERENCES `lowcode_records` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_content_assignments_teacher` FOREIGN KEY (`teacher_username`) REFERENCES `users` (`username`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `content_assignments` WRITE;
/*!40000 ALTER TABLE `content_assignments` DISABLE KEYS */;
/*!40000 ALTER TABLE `content_assignments` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `content_item_assets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `content_item_assets` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `content_item_id` bigint NOT NULL,
  `asset_id` bigint DEFAULT NULL,
  `role` varchar(40) NOT NULL DEFAULT 'gallery',
  `title` varchar(255) NOT NULL DEFAULT '',
  `caption` varchar(512) NOT NULL DEFAULT '',
  `url` varchar(2048) NOT NULL DEFAULT '',
  `sort_order` int NOT NULL DEFAULT '0',
  `created_at` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_content_item_assets_item` (`content_item_id`,`sort_order`),
  KEY `idx_content_item_assets_asset` (`asset_id`),
  CONSTRAINT `fk_content_item_assets_asset` FOREIGN KEY (`asset_id`) REFERENCES `assets` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_content_item_assets_item` FOREIGN KEY (`content_item_id`) REFERENCES `content_items` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `content_item_assets` WRITE;
/*!40000 ALTER TABLE `content_item_assets` DISABLE KEYS */;
INSERT INTO `content_item_assets` VALUES (2,2,NULL,'external_link','人工智能应用技术互动体验系统','人工智能应用技术互动体验系统','http://sxjsxy.szzfhs.com/',0,'2026-08-11T10:15:57.052146+00:00'),(3,2,NULL,'external_link','多模态大模型自然语言交互体验系统','多模态大模型自然语言交互体验系统','http://sxjsxy.szzfhs.com/#/AigcApply',1,'2026-08-11T10:15:57.052673+00:00'),(4,2,NULL,'external_link','生成式人工智能 AIGC 终端系统','生成式人工智能 AIGC 终端系统','http://110.41.133.77:8899/trainai2/#/media-design',2,'2026-08-11T10:15:57.053200+00:00'),(5,3,NULL,'external_link','毕节特色景点虚拟仿真文旅数字资源','毕节特色景点虚拟仿真文旅数字资源','http://bjsz.szzfhs.com/bjlvh5',0,'2026-08-11T10:15:57.060556+00:00'),(6,4,NULL,'external_link','文化旅游系典型案例库数字资源','文化旅游系典型案例库数字资源','http://bjsz.szzfhs.com/bjlvh5/#/pages/spotoverview/spotoverview',0,'2026-08-11T10:15:57.066868+00:00'),(7,5,NULL,'external_link','生成式人工智能 AIGC 终端系统','生成式人工智能 AIGC 终端系统','http://110.41.133.77:8899/trainai2/#/media-design',0,'2026-08-11T10:15:57.072063+00:00'),(8,6,NULL,'cover','','','/uploads/c60e0d1c70d34d78996632d15ce7aa15.jpg',0,'2026-08-11T10:22:01.900957+00:00'),(9,1,NULL,'external_link','互动体验系统合集','互动体验系统合集','http://sxjsxy.szzfhs.com/',0,'2026-08-11T10:24:54.599734+00:00'),(11,7,NULL,'cover','','','/uploads/8d45276947824cc4ac9a72a2bb398bf1.png',0,'2026-08-11T10:26:41.704793+00:00');
/*!40000 ALTER TABLE `content_item_assets` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `content_item_versions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `content_item_versions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `content_item_id` bigint DEFAULT NULL,
  `project_id` bigint NOT NULL,
  `operation` varchar(32) NOT NULL DEFAULT 'upsert',
  `status` varchar(32) NOT NULL DEFAULT 'pending',
  `snapshot_json` json NOT NULL,
  `submitted_by` varchar(64) NOT NULL DEFAULT '',
  `submitted_at` varchar(40) NOT NULL,
  `reviewed_by` varchar(64) NOT NULL DEFAULT '',
  `reviewed_at` varchar(40) NOT NULL DEFAULT '',
  `review_note` varchar(1024) NOT NULL DEFAULT '',
  `changes` varchar(2048) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `idx_content_item_versions_status` (`status`,`submitted_at`),
  KEY `idx_content_item_versions_project` (`project_id`),
  KEY `idx_content_item_versions_item` (`content_item_id`),
  CONSTRAINT `fk_content_item_versions_item` FOREIGN KEY (`content_item_id`) REFERENCES `content_items` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_content_item_versions_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `content_item_versions` WRITE;
/*!40000 ALTER TABLE `content_item_versions` DISABLE KEYS */;
INSERT INTO `content_item_versions` VALUES (1,1,11,'upsert','approved','{\"code\": \"EXT-DIGITAL-INTELLIGENCE-HUB\", \"title\": \"互动体验系统合集\", \"assets\": [{\"url\": \"http://sxjsxy.szzfhs.com/\", \"role\": \"external_link\", \"title\": \"互动体验系统合集\", \"caption\": \"互动体验系统合集\", \"sortOrder\": 0}], \"enabled\": true, \"summary\": \"汇聚人工智能、大模型交互和 AIGC 等互动体验系统入口。\", \"bodyJson\": [{\"text\": \"汇聚人工智能、大模型交互和 AIGC 等互动体验系统入口。\", \"type\": \"paragraph\"}], \"featured\": true, \"metaJson\": {\"入口类型\": \"外部互动体验系统\", \"维护方式\": \"后台结构化资料素材区\"}, \"subtitle\": \"\", \"moduleKey\": \"overview\", \"sortOrder\": 5, \"contentType\": \"article\", \"coverAssetId\": null}','admin','2026-08-11T10:15:57.046679+00:00','admin','2026-08-11T10:15:57.046679+00:00','','assets'),(2,2,11,'upsert','approved','{\"code\": \"EXT-DIGITAL-INTELLIGENCE-AI\", \"title\": \"人工智能互动体验入口\", \"assets\": [{\"url\": \"http://sxjsxy.szzfhs.com/\", \"role\": \"external_link\", \"title\": \"人工智能应用技术互动体验系统\", \"caption\": \"人工智能应用技术互动体验系统\", \"sortOrder\": 0}, {\"url\": \"http://sxjsxy.szzfhs.com/#/AigcApply\", \"role\": \"external_link\", \"title\": \"多模态大模型自然语言交互体验系统\", \"caption\": \"多模态大模型自然语言交互体验系统\", \"sortOrder\": 1}, {\"url\": \"http://110.41.133.77:8899/trainai2/#/media-design\", \"role\": \"external_link\", \"title\": \"生成式人工智能 AIGC 终端系统\", \"caption\": \"生成式人工智能 AIGC 终端系统\", \"sortOrder\": 2}], \"enabled\": true, \"summary\": \"面向数智技术专题的人工智能应用、大模型自然语言交互与生成式 AI 体验。\", \"bodyJson\": [{\"text\": \"面向数智技术专题的人工智能应用、大模型自然语言交互与生成式 AI 体验。\", \"type\": \"paragraph\"}], \"featured\": true, \"metaJson\": {\"入口类型\": \"外部互动体验系统\", \"维护方式\": \"后台结构化资料素材区\"}, \"subtitle\": \"\", \"moduleKey\": \"training\", \"sortOrder\": 5, \"contentType\": \"article\", \"coverAssetId\": null}','admin','2026-08-11T10:15:57.056911+00:00','admin','2026-08-11T10:15:57.056911+00:00','','assets'),(3,3,8,'upsert','approved','{\"code\": \"EXT-DIGITAL-TOURISM-SIM\", \"title\": \"文旅虚拟仿真体验入口\", \"assets\": [{\"url\": \"http://bjsz.szzfhs.com/bjlvh5\", \"role\": \"external_link\", \"title\": \"毕节特色景点虚拟仿真文旅数字资源\", \"caption\": \"毕节特色景点虚拟仿真文旅数字资源\", \"sortOrder\": 0}], \"enabled\": true, \"summary\": \"面向数字文旅实训场景，集中跳转毕节特色景点虚拟仿真资源。\", \"bodyJson\": [{\"text\": \"面向数字文旅实训场景，集中跳转毕节特色景点虚拟仿真资源。\", \"type\": \"paragraph\"}], \"featured\": true, \"metaJson\": {\"入口类型\": \"外部互动体验系统\", \"维护方式\": \"后台结构化资料素材区\"}, \"subtitle\": \"\", \"moduleKey\": \"training\", \"sortOrder\": 5, \"contentType\": \"article\", \"coverAssetId\": null}','admin','2026-08-11T10:15:57.061083+00:00','admin','2026-08-11T10:15:57.061083+00:00','','assets'),(4,4,8,'upsert','approved','{\"code\": \"EXT-DIGITAL-TOURISM-CASELIB\", \"title\": \"文化旅游系典型案例库\", \"assets\": [{\"url\": \"http://bjsz.szzfhs.com/bjlvh5/#/pages/spotoverview/spotoverview\", \"role\": \"external_link\", \"title\": \"文化旅游系典型案例库数字资源\", \"caption\": \"文化旅游系典型案例库数字资源\", \"sortOrder\": 0}], \"enabled\": true, \"summary\": \"面向数字文旅专题成果，跳转文化旅游系典型案例库数字资源。\", \"bodyJson\": [{\"text\": \"面向数字文旅专题成果，跳转文化旅游系典型案例库数字资源。\", \"type\": \"paragraph\"}], \"featured\": true, \"metaJson\": {\"入口类型\": \"外部互动体验系统\", \"维护方式\": \"后台结构化资料素材区\"}, \"subtitle\": \"\", \"moduleKey\": \"achievements\", \"sortOrder\": 5, \"contentType\": \"article\", \"coverAssetId\": null}','admin','2026-08-11T10:15:57.068941+00:00','admin','2026-08-11T10:15:57.068941+00:00','','assets'),(5,5,10,'upsert','approved','{\"code\": \"EXT-FINANCE-COMMERCE-AIGC\", \"title\": \"AIGC 电商视觉设计终端\", \"assets\": [{\"url\": \"http://110.41.133.77:8899/trainai2/#/media-design\", \"role\": \"external_link\", \"title\": \"生成式人工智能 AIGC 终端系统\", \"caption\": \"生成式人工智能 AIGC 终端系统\", \"sortOrder\": 0}], \"enabled\": true, \"summary\": \"面向财经商贸数字营销、视觉设计和电商运营实训，提供生成式 AI 终端入口。\", \"bodyJson\": [{\"text\": \"面向财经商贸数字营销、视觉设计和电商运营实训，提供生成式 AI 终端入口。\", \"type\": \"paragraph\"}], \"featured\": true, \"metaJson\": {\"入口类型\": \"外部互动体验系统\", \"维护方式\": \"后台结构化资料素材区\"}, \"subtitle\": \"\", \"moduleKey\": \"training\", \"sortOrder\": 5, \"contentType\": \"article\", \"coverAssetId\": null}','admin','2026-08-11T10:15:57.074113+00:00','admin','2026-08-11T10:15:57.074113+00:00','','assets'),(6,6,13,'upsert','approved','{\"code\": \"CI-OVERVIEW-13-05D267\", \"title\": \"222\", \"assets\": [{\"id\": 0, \"url\": \"/uploads/c60e0d1c70d34d78996632d15ce7aa15.jpg\", \"role\": \"cover\", \"title\": \"\", \"assetId\": null, \"caption\": \"\", \"mimeType\": \"\", \"sortOrder\": 0}], \"enabled\": true, \"summary\": \"222\", \"bodyJson\": [], \"featured\": false, \"metaJson\": {}, \"subtitle\": \"\", \"moduleKey\": \"overview\", \"sortOrder\": 0, \"contentType\": \"article\", \"coverAssetId\": null}','admin','2026-08-11T10:22:01.907748+00:00','admin','2026-08-11T10:22:01.907748+00:00','','assets'),(7,1,11,'upsert','approved','{\"code\": \"EXT-DIGITAL-INTELLIGENCE-HUB\", \"title\": \"互动体验系统合集\", \"assets\": [{\"id\": 1, \"url\": \"http://sxjsxy.szzfhs.com/\", \"role\": \"external_link\", \"title\": \"互动体验系统合集\", \"assetId\": null, \"caption\": \"互动体验系统合集\", \"mimeType\": \"\", \"sortOrder\": 0}], \"enabled\": true, \"summary\": \"汇聚人工智能、大模型交互和 AIGC 等互动体验系统入口。\", \"bodyJson\": [{\"html\": \"<p>汇聚人工智能、大模型交互和 AIGC 等互动体验系统入口。<img src=\\\"/uploads/211d952b80ec471ca2cbafb9e877169f.png\\\" style=\\\"width: 412.969px\\\" class=\\\"\\\"></p>\", \"type\": \"html\"}], \"featured\": true, \"metaJson\": {\"入口类型\": \"外部互动体验系统\", \"维护方式\": \"后台结构化资料素材区\"}, \"subtitle\": \"\", \"moduleKey\": \"overview\", \"sortOrder\": 5, \"contentType\": \"article\", \"coverAssetId\": null}','admin','2026-08-11T10:24:54.605904+00:00','admin','2026-08-11T10:24:54.605904+00:00','','assets'),(8,7,7,'upsert','approved','{\"code\": \"CI-COMPETITIONS-7-17EC69\", \"title\": \"2223\", \"assets\": [{\"id\": 0, \"url\": \"/uploads/8d45276947824cc4ac9a72a2bb398bf1.png\", \"role\": \"cover\", \"title\": \"\", \"assetId\": null, \"caption\": \"\", \"mimeType\": \"\", \"sortOrder\": 0}], \"enabled\": true, \"summary\": \"2223\", \"bodyJson\": [], \"featured\": false, \"metaJson\": {}, \"subtitle\": \"\", \"moduleKey\": \"competitions\", \"sortOrder\": 0, \"contentType\": \"article\", \"coverAssetId\": null}','admin','2026-08-11T10:26:19.843762+00:00','admin','2026-08-11T10:26:19.843762+00:00','','assets'),(9,7,7,'upsert','approved','{\"code\": \"CI-COMPETITIONS-7-17EC69\", \"title\": \"2223\", \"assets\": [{\"id\": 10, \"url\": \"/uploads/8d45276947824cc4ac9a72a2bb398bf1.png\", \"role\": \"cover\", \"title\": \"\", \"assetId\": null, \"caption\": \"\", \"mimeType\": \"\", \"sortOrder\": 0}], \"enabled\": true, \"summary\": \"2223\", \"bodyJson\": [{\"html\": \"<p style=\\\"text-align: center\\\"><img src=\\\"/uploads/8d45276947824cc4ac9a72a2bb398bf1.png\\\" alt=\\\"2223\\\" style=\\\"max-width: 100%; width: 475.969px\\\" class=\\\"\\\"></p><p>2223这是的生产监控监控力度</p>\", \"type\": \"html\"}], \"featured\": false, \"metaJson\": {}, \"subtitle\": \"\", \"moduleKey\": \"competitions\", \"sortOrder\": 0, \"contentType\": \"article\", \"coverAssetId\": null}','admin','2026-08-11T10:26:41.711531+00:00','admin','2026-08-11T10:26:41.711531+00:00','','assets');
/*!40000 ALTER TABLE `content_item_versions` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `content_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `content_items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `project_id` bigint NOT NULL,
  `page_id` bigint DEFAULT NULL,
  `code` varchar(160) NOT NULL,
  `module_key` varchar(80) NOT NULL,
  `content_type` varchar(32) NOT NULL DEFAULT 'article',
  `title` varchar(255) NOT NULL,
  `subtitle` varchar(512) NOT NULL DEFAULT '',
  `summary` varchar(1024) NOT NULL DEFAULT '',
  `body_json` json NOT NULL,
  `meta_json` json NOT NULL,
  `cover_asset_id` bigint DEFAULT NULL,
  `sort_order` int NOT NULL DEFAULT '0',
  `featured` tinyint(1) NOT NULL DEFAULT '0',
  `enabled` tinyint(1) NOT NULL DEFAULT '1',
  `review_status` varchar(32) NOT NULL DEFAULT 'approved',
  `pending_version_id` bigint DEFAULT NULL,
  `submitted_by` varchar(64) NOT NULL DEFAULT 'admin',
  `reviewed_by` varchar(64) NOT NULL DEFAULT 'admin',
  `review_note` varchar(1024) NOT NULL DEFAULT '',
  `created_at` varchar(40) NOT NULL,
  `updated_at` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_content_items_project_code` (`project_id`,`code`),
  KEY `idx_content_items_project_module` (`project_id`,`module_key`,`sort_order`),
  KEY `idx_content_items_project_status` (`project_id`,`review_status`),
  KEY `idx_content_items_type` (`content_type`),
  KEY `fk_content_items_page` (`page_id`),
  KEY `fk_content_items_cover` (`cover_asset_id`),
  CONSTRAINT `fk_content_items_cover` FOREIGN KEY (`cover_asset_id`) REFERENCES `assets` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_content_items_page` FOREIGN KEY (`page_id`) REFERENCES `pages` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_content_items_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `content_items` WRITE;
/*!40000 ALTER TABLE `content_items` DISABLE KEYS */;
INSERT INTO `content_items` VALUES (1,11,9,'EXT-DIGITAL-INTELLIGENCE-HUB','overview','article','互动体验系统合集','','汇聚人工智能、大模型交互和 AIGC 等互动体验系统入口。','[{\"html\": \"<p>汇聚人工智能、大模型交互和 AIGC 等互动体验系统入口。<img src=\\\"/uploads/211d952b80ec471ca2cbafb9e877169f.png\\\" style=\\\"width: 412.969px\\\" class=\\\"\\\"></p>\", \"type\": \"html\"}]','{\"入口类型\": \"外部互动体验系统\", \"维护方式\": \"后台结构化资料素材区\"}',NULL,5,1,1,'approved',NULL,'admin','admin','','2026-08-11T10:15:57.040905+00:00','2026-08-11T10:24:54.598191+00:00'),(2,11,NULL,'EXT-DIGITAL-INTELLIGENCE-AI','training','article','人工智能互动体验入口','','面向数智技术专题的人工智能应用、大模型自然语言交互与生成式 AI 体验。','[{\"text\": \"面向数智技术专题的人工智能应用、大模型自然语言交互与生成式 AI 体验。\", \"type\": \"paragraph\"}]','{\"入口类型\": \"外部互动体验系统\", \"维护方式\": \"后台结构化资料素材区\"}',NULL,5,1,1,'approved',NULL,'admin','admin','','2026-08-11T10:15:57.040905+00:00','2026-08-11T10:15:57.040905+00:00'),(3,8,NULL,'EXT-DIGITAL-TOURISM-SIM','training','article','文旅虚拟仿真体验入口','','面向数字文旅实训场景，集中跳转毕节特色景点虚拟仿真资源。','[{\"text\": \"面向数字文旅实训场景，集中跳转毕节特色景点虚拟仿真资源。\", \"type\": \"paragraph\"}]','{\"入口类型\": \"外部互动体验系统\", \"维护方式\": \"后台结构化资料素材区\"}',NULL,5,1,1,'approved',NULL,'admin','admin','','2026-08-11T10:15:57.040905+00:00','2026-08-11T10:15:57.040905+00:00'),(4,8,NULL,'EXT-DIGITAL-TOURISM-CASELIB','achievements','article','文化旅游系典型案例库','','面向数字文旅专题成果，跳转文化旅游系典型案例库数字资源。','[{\"text\": \"面向数字文旅专题成果，跳转文化旅游系典型案例库数字资源。\", \"type\": \"paragraph\"}]','{\"入口类型\": \"外部互动体验系统\", \"维护方式\": \"后台结构化资料素材区\"}',NULL,5,1,1,'approved',NULL,'admin','admin','','2026-08-11T10:15:57.040905+00:00','2026-08-11T10:15:57.040905+00:00'),(5,10,NULL,'EXT-FINANCE-COMMERCE-AIGC','training','article','AIGC 电商视觉设计终端','','面向财经商贸数字营销、视觉设计和电商运营实训，提供生成式 AI 终端入口。','[{\"text\": \"面向财经商贸数字营销、视觉设计和电商运营实训，提供生成式 AI 终端入口。\", \"type\": \"paragraph\"}]','{\"入口类型\": \"外部互动体验系统\", \"维护方式\": \"后台结构化资料素材区\"}',NULL,5,1,1,'approved',NULL,'admin','admin','','2026-08-11T10:15:57.040905+00:00','2026-08-11T10:15:57.040905+00:00'),(6,13,8,'CI-OVERVIEW-13-05D267','overview','article','222','','222','[]','{}',NULL,0,0,1,'approved',NULL,'admin','admin','','2026-08-11T10:22:01.899376+00:00','2026-08-11T10:22:01.899376+00:00'),(7,7,11,'CI-COMPETITIONS-7-17EC69','competitions','article','2223','','2223','[{\"html\": \"<p style=\\\"text-align: center\\\"><img src=\\\"/uploads/8d45276947824cc4ac9a72a2bb398bf1.png\\\" alt=\\\"2223\\\" style=\\\"max-width: 100%; width: 475.969px\\\" class=\\\"\\\"></p><p>2223这是的生产监控监控力度</p>\", \"type\": \"html\"}]','{}',NULL,0,0,1,'approved',NULL,'admin','admin','','2026-08-11T10:26:19.835980+00:00','2026-08-11T10:26:41.703731+00:00');
/*!40000 ALTER TABLE `content_items` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `deployed_pages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deployed_pages` (
  `project_id` bigint NOT NULL,
  `page_id` bigint NOT NULL,
  `updated_at` varchar(40) NOT NULL,
  PRIMARY KEY (`project_id`,`page_id`),
  KEY `fk_deployed_pages_page` (`page_id`),
  CONSTRAINT `fk_deployed_pages_page` FOREIGN KEY (`page_id`) REFERENCES `pages` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_deployed_pages_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `deployed_pages` WRITE;
/*!40000 ALTER TABLE `deployed_pages` DISABLE KEYS */;
INSERT INTO `deployed_pages` VALUES (1,1,'2026-08-11T10:11:37.851742+00:00'),(1,2,'2026-08-11T10:11:37.851742+00:00'),(1,3,'2026-08-11T10:11:37.851742+00:00'),(1,4,'2026-08-11T10:11:37.851742+00:00'),(1,5,'2026-08-11T10:11:37.851742+00:00');
/*!40000 ALTER TABLE `deployed_pages` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `lowcode_form_versions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lowcode_form_versions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `form_id` bigint NOT NULL,
  `version_no` int NOT NULL DEFAULT '1',
  `schema_json` json NOT NULL,
  `status` varchar(32) NOT NULL DEFAULT 'active',
  `created_by` varchar(64) NOT NULL DEFAULT 'system',
  `created_at` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_lowcode_form_versions_form_version` (`form_id`,`version_no`),
  KEY `idx_lowcode_form_versions_form_status` (`form_id`,`status`),
  CONSTRAINT `fk_lowcode_form_versions_form` FOREIGN KEY (`form_id`) REFERENCES `lowcode_forms` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `lowcode_form_versions` WRITE;
/*!40000 ALTER TABLE `lowcode_form_versions` DISABLE KEYS */;
/*!40000 ALTER TABLE `lowcode_form_versions` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `lowcode_forms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lowcode_forms` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `code` varchar(120) NOT NULL,
  `description` varchar(1024) NOT NULL DEFAULT '',
  `target_type` varchar(40) NOT NULL DEFAULT 'content_item',
  `target_portal_type` varchar(40) NOT NULL DEFAULT 'department',
  `target_content_type` varchar(32) NOT NULL DEFAULT 'article',
  `target_module_key` varchar(80) NOT NULL DEFAULT '',
  `enabled` tinyint(1) NOT NULL DEFAULT '1',
  `created_by` varchar(64) NOT NULL DEFAULT 'system',
  `created_at` varchar(40) NOT NULL,
  `updated_at` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_lowcode_forms_code` (`code`),
  KEY `idx_lowcode_forms_target` (`target_portal_type`,`target_module_key`,`enabled`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `lowcode_forms` WRITE;
/*!40000 ALTER TABLE `lowcode_forms` DISABLE KEYS */;
/*!40000 ALTER TABLE `lowcode_forms` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `lowcode_record_assets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lowcode_record_assets` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `record_id` bigint NOT NULL,
  `asset_id` bigint DEFAULT NULL,
  `role` varchar(40) NOT NULL DEFAULT 'gallery',
  `title` varchar(255) NOT NULL DEFAULT '',
  `caption` varchar(512) NOT NULL DEFAULT '',
  `url` varchar(2048) NOT NULL DEFAULT '',
  `sort_order` int NOT NULL DEFAULT '0',
  `created_at` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_lowcode_record_assets_record` (`record_id`,`sort_order`),
  KEY `fk_lowcode_record_assets_asset` (`asset_id`),
  CONSTRAINT `fk_lowcode_record_assets_asset` FOREIGN KEY (`asset_id`) REFERENCES `assets` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_lowcode_record_assets_record` FOREIGN KEY (`record_id`) REFERENCES `lowcode_records` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `lowcode_record_assets` WRITE;
/*!40000 ALTER TABLE `lowcode_record_assets` DISABLE KEYS */;
/*!40000 ALTER TABLE `lowcode_record_assets` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `lowcode_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lowcode_records` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `form_id` bigint NOT NULL,
  `form_version_id` bigint NOT NULL,
  `project_id` bigint NOT NULL,
  `content_item_id` bigint DEFAULT NULL,
  `status` varchar(32) NOT NULL DEFAULT 'pending',
  `data_json` json NOT NULL,
  `submitted_by` varchar(64) NOT NULL DEFAULT '',
  `submitted_at` varchar(40) NOT NULL,
  `reviewed_by` varchar(64) NOT NULL DEFAULT '',
  `reviewed_at` varchar(40) NOT NULL DEFAULT '',
  `review_note` varchar(1024) NOT NULL DEFAULT '',
  `created_at` varchar(40) NOT NULL,
  `updated_at` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_lowcode_records_project` (`project_id`,`submitted_at`),
  KEY `idx_lowcode_records_form` (`form_id`,`submitted_at`),
  KEY `idx_lowcode_records_content_item` (`content_item_id`),
  KEY `fk_lowcode_records_version` (`form_version_id`),
  CONSTRAINT `fk_lowcode_records_content_item` FOREIGN KEY (`content_item_id`) REFERENCES `content_items` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_lowcode_records_form` FOREIGN KEY (`form_id`) REFERENCES `lowcode_forms` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_lowcode_records_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_lowcode_records_version` FOREIGN KEY (`form_version_id`) REFERENCES `lowcode_form_versions` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `lowcode_records` WRITE;
/*!40000 ALTER TABLE `lowcode_records` DISABLE KEYS */;
/*!40000 ALTER TABLE `lowcode_records` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `page_versions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `page_versions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `page_id` bigint DEFAULT NULL,
  `project_id` bigint NOT NULL,
  `code` varchar(160) NOT NULL,
  `operation` varchar(32) NOT NULL DEFAULT 'upsert',
  `status` varchar(32) NOT NULL DEFAULT 'pending',
  `snapshot` json NOT NULL,
  `submitted_by` varchar(64) NOT NULL DEFAULT '',
  `submitted_at` varchar(40) NOT NULL,
  `reviewed_by` varchar(64) NOT NULL DEFAULT '',
  `reviewed_at` varchar(40) NOT NULL DEFAULT '',
  `review_note` varchar(1024) NOT NULL DEFAULT '',
  `changes` varchar(2048) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `idx_page_versions_status` (`status`,`submitted_at`),
  KEY `idx_page_versions_project` (`project_id`),
  KEY `idx_page_versions_page` (`page_id`),
  CONSTRAINT `fk_page_versions_page` FOREIGN KEY (`page_id`) REFERENCES `pages` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_page_versions_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `page_versions` WRITE;
/*!40000 ALTER TABLE `page_versions` DISABLE KEYS */;
INSERT INTO `page_versions` VALUES (1,1,1,'BJ-SERVICE','upsert','approved','{\"body\": \"<div class=\\\"lead-card\\\"><span>SOCIAL SERVICE</span><strong>服务地方产业与技能人才培养</strong><p>学校围绕毕节新发展理念示范区建设，聚焦现代能源、生态食品、先进装备制造、轻纺及健康医药等产业，持续开展职业技能培训、等级认定和乡村振兴服务。</p></div>\\n<div class=\\\"stat-grid\\\"><div class=\\\"stat\\\"><strong>45000+</strong><span>培训人次</span><p>联合政校企完成多类型技术技能培训。</p></div><div class=\\\"stat\\\"><strong>15000+</strong><span>认定人次</span><p>面向学生和社会人员开展职业技能等级认定。</p></div><div class=\\\"stat\\\"><strong>八大产业</strong><span>服务方向</span><p>对接地方工业产业和特色农业发展需求。</p></div></div>\\n<h2>重点服务方向</h2><ul><li>高技能人才、基层服务、煤矿安全技术、退役军人就业创业培训。</li><li>乡村振兴技能人才培养和非物质文化遗产传承人群研修研习。</li><li>职业技能等级认定与专项职业能力认定平台建设。</li></ul>\\n<div class=\\\"photo-strip\\\"><figure><img src=\\\"/uploads/bijie-samples/image1.jpeg\\\" alt=\\\"培训现场\\\"><figcaption>毕节市财政财务基础业务培训班</figcaption></figure><figure><img src=\\\"/uploads/bijie-samples/image16.jpeg\\\" alt=\\\"稻米示范推广培训\\\"><figcaption>优质稻米示范推广培训进入田间地头</figcaption></figure></div>\\n<blockquote>以学校技术资源和师资优势服务地方产业发展，助力毕节市人力资源开发和乡村全面振兴。</blockquote>\", \"code\": \"BJ-SERVICE\", \"title\": \"社会服务成果\", \"accent\": \"#49c5b6\", \"source\": \"毕节职业技术学院\", \"enabled\": true, \"category\": \"社会服务成果\", \"imageUrl\": \"/uploads/bijie-samples/image16.jpeg\", \"subtitle\": \"聚焦技能培训、职业认定与乡村振兴服务，测试指标卡、图文组合与引用块。\", \"contentType\": \"article\", \"publishedAt\": \"\"}','admin','2026-08-11T10:09:40.805095+00:00','admin','2026-08-11T10:09:40.805095+00:00','','legacy import'),(2,2,1,'BJ-INTL','upsert','approved','{\"body\": \"<div class=\\\"lead-card\\\"><span>GLOBAL COOPERATION</span><strong>从“引进来”到“走出去”的国际合作</strong><p>学校主动服务“一带一路”倡议和中国-东盟、中非教育合作，在海外交流、标准输出、多边合作、技能竞赛、人文往来等方面形成阶段性成果。</p></div>\\n<div class=\\\"timeline\\\"><div><span>2024</span><p>组织师生赴泰国格乐大学开展短期研学，拓宽学生国际视野，增进中泰人文交流。</p></div><div><span>2025</span><p>牵头制定菲律宾《农业经理人》国家职业技能标准，并参与中国-东盟数字资源共建共享合作。</p></div><div><span>近三年</span><p>累计接待国（境）外来访团组 4 个，举办国际文化交流活动 4 场，签订校际合作备忘录 2 份。</p></div></div>\\n<h2>成果看点</h2><ul><li>获批埃塞俄比亚国家职业标准开发项目认证。</li><li>课程资源被俄罗斯喀山联邦大学、埃塞俄比亚 Dire Dawa University 采用。</li><li>师生在金砖国家技能发展与技术创新大赛等国际赛事中获得多项奖项。</li></ul>\\n<div class=\\\"photo-strip\\\"><figure><img src=\\\"/uploads/bijie-samples/image23.jpeg\\\" alt=\\\"泰国研学合影\\\"><figcaption>师生赴泰国格乐大学开展短期研学</figcaption></figure><figure><img src=\\\"/uploads/bijie-samples/image31.jpeg\\\" alt=\\\"国际人文交流活动\\\"><figcaption>“桥见”贵州毕节职院人文交流活动</figcaption></figure></div>\\n<hr><p>这一页用于测试时间线、图文组合、列表与分隔线在大屏详情页中的可读性。</p>\", \"code\": \"BJ-INTL\", \"title\": \"国际交流合作成果\", \"accent\": \"#f8c35a\", \"source\": \"毕节职业技术学院\", \"enabled\": true, \"category\": \"国际交流合作\", \"imageUrl\": \"/uploads/bijie-samples/image23.jpeg\", \"subtitle\": \"从海外研学到职业标准输出，测试时间线、列表、图片和分隔线。\", \"contentType\": \"article\", \"publishedAt\": \"\"}','admin','2026-08-11T10:09:40.805095+00:00','admin','2026-08-11T10:09:40.805095+00:00','','legacy import'),(3,3,1,'BJ-GRAD','upsert','approved','{\"body\": \"<div class=\\\"profile-card\\\"><img src=\\\"/uploads/bijie-samples/image38.jpeg\\\" alt=\\\"张娅婷事迹照片\\\"><div><span>优秀毕业生</span><h3>张娅婷</h3><p>贵州省 2024 届优秀毕业生，学前教育专业。她在校园学习、学生工作、志愿服务和西部计划实践中持续成长。</p></div></div>\\n<div class=\\\"badge-list\\\"><span>中共党员</span><span>教育科学系</span><span>学前教育</span><span>国家奖学金</span><span>省级优秀毕业生</span></div>\\n<h2>一路追光，筑梦前行</h2><p>在校期间，她担任系学生会团总支副书记、学生会主席、班级团支部书记与班长，荣获全国乡村振兴“笃行计划优秀实践个人”、励志奖学金、省三好学生等荣誉。</p>\\n<h3>敢担当</h3><p>2021 年至 2023 年，她承担学生组织工作，并于 2023 年赴马来西亚英迪国际大学短期访学，按期高质量完成学业。</p>\\n<h3>能吃苦</h3><p>连续两年参加“三下乡”社会实践，组织关爱留守儿童、服务空巢老人和民族文化传承活动，在实践中锤炼专业能力和社会责任。</p>\\n<h3>有理想</h3><p>2024 年 8 月，她投身贵州省毕节市七星关区碧阳街道办事处西部计划志愿服务，参与档案整理、热线回应和志愿服务等工作。</p>\\n<div class=\\\"template-note\\\"><strong>教师评语</strong><p>希望你用行动去诠释教育的真谛，展现青春的力量。</p></div>\", \"code\": \"BJ-GRAD\", \"title\": \"优秀毕业生张娅婷\", \"accent\": \"#ff8f5a\", \"source\": \"教育科学系\", \"enabled\": true, \"category\": \"育人成果\", \"imageUrl\": \"/uploads/bijie-samples/image37.png\", \"subtitle\": \"以人物卡片、荣誉标签和分段叙事展示优秀毕业生成长故事。\", \"contentType\": \"article\", \"publishedAt\": \"\"}','admin','2026-08-11T10:09:40.805095+00:00','admin','2026-08-11T10:09:40.805095+00:00','','legacy import'),(4,4,1,'BJ-TEACHER','upsert','approved','{\"body\": \"<div class=\\\"profile-card\\\"><img src=\\\"/uploads/bijie-samples/image39.jpeg\\\" alt=\\\"谭佳 portrait\\\"><div><span>校内名师</span><h3>谭佳</h3><p>旅游管理系副教授，聚焦旅游技能人才培养、数智赋能课程建设等教学教改方向。</p></div></div>\\n<div class=\\\"stat-grid\\\"><div class=\\\"stat\\\"><strong>10+</strong><span>省部级、市厅级项目</span><p>主持并推进多项教学教改与社会服务项目。</p></div><div class=\\\"stat\\\"><strong>10000+</strong><span>课程覆盖人次</span><p>开发《乡村旅游导览实务》等培训课程。</p></div><div class=\\\"stat\\\"><strong>30+</strong><span>团队课题</span><p>围绕生态旅游、红色讲解、研学旅游开发等方向开展研究。</p></div></div>\\n<h2>教学与产业服务成果</h2><ul><li>获全国教师教学能力大赛三等奖、省赛一等奖。</li><li>实践成果入选文旅部优秀成果并在全国推广。</li><li>教学案例入选文旅部旅游职业教育“五金”数智化建设典型案例。</li></ul>\\n<div class=\\\"photo-strip\\\"><figure><img src=\\\"/uploads/bijie-samples/image32.jpeg\\\" alt=\\\"论坛发言\\\"><figcaption>在论坛活动中进行主旨发言</figcaption></figure><figure><img src=\\\"/uploads/bijie-samples/image30.jpeg\\\" alt=\\\"校园成果展示\\\"><figcaption>职业教育成果面向行业与社会展示</figcaption></figure></div>\\n<blockquote>通过老带新、师带徒，优化人才结构，赋能贵州文旅产业高质量发展。</blockquote>\", \"code\": \"BJ-TEACHER\", \"title\": \"校内名师谭佳\", \"accent\": \"#8bd17c\", \"source\": \"旅游管理系\", \"enabled\": true, \"category\": \"名师名匠\", \"imageUrl\": \"/uploads/bijie-samples/image32.jpeg\", \"subtitle\": \"用人物介绍、数据卡和成果列表展示名师名匠内容模板。\", \"contentType\": \"article\", \"publishedAt\": \"\"}','admin','2026-08-11T10:09:40.805095+00:00','admin','2026-08-11T10:09:40.805095+00:00','','legacy import'),(5,5,1,'DEMO-10100043','upsert','approved','{\"body\": \"这里可以放项目介绍、展品亮点、团队说明和现场引导文案。后台可以随时替换这些文字和图片。\", \"code\": \"DEMO-10100043\", \"title\": \"欢迎来到成果展示\", \"accent\": \"#0f766e\", \"source\": \"学校展示\", \"enabled\": true, \"category\": \"校园新闻\", \"imageUrl\": \"/static/sample.svg\", \"subtitle\": \"深圳先进技术研究院展会互动展示\", \"contentType\": \"article\", \"publishedAt\": \"\"}','admin','2026-08-11T10:09:40.805095+00:00','admin','2026-08-11T10:09:40.805095+00:00','','legacy import'),(8,10,11,'overview','upsert','approved','{\"body\": \"<p>汇聚人工智能、大模型交互和 AIGC 等互动体验系统入口。</p><p>汇聚人工智能、大模型交互和 AIGC 等互动体验系统入口。</p><figure class=\\\"image\\\"><img src=\\\"/uploads/12d841efd1a74d8785c5a91b3f737fc1.png\\\" alt=\\\"\\\"></figure>\", \"code\": \"overview\", \"title\": \"专题概况\", \"accent\": \"#0f766e\", \"source\": \"学校展示\", \"enabled\": true, \"category\": \"校园新闻\", \"imageUrl\": \"\", \"subtitle\": \"\", \"contentType\": \"article\", \"publishedAt\": \"\"}','admin','2026-08-11T10:25:01.357882+00:00','admin','2026-08-11T10:25:01.357882+00:00','',''),(9,12,7,'overview','upsert','approved','{\"body\": \"<p></p><figure class=\\\"image\\\"><img src=\\\"/uploads/c4fb063eefd0478eafc7a373e75b2d16.jpg\\\" alt=\\\"\\\"></figure>\", \"code\": \"overview\", \"title\": \"\", \"accent\": \"#0f766e\", \"source\": \"学校展示\", \"enabled\": true, \"category\": \"校园新闻\", \"imageUrl\": \"\", \"subtitle\": \"\", \"contentType\": \"article\", \"publishedAt\": \"\"}','admin','2026-08-11T10:26:43.384526+00:00','admin','2026-08-11T10:26:43.384526+00:00','',''),(10,13,7,'competitions','upsert','approved','{\"body\": \"<figure class=\\\"image\\\"><img src=\\\"/uploads/60f3798d1c7b47628c2f7004c28d978e.jpg\\\" alt=\\\"\\\"></figure>\", \"code\": \"competitions\", \"title\": \"\", \"accent\": \"#0f766e\", \"source\": \"学校展示\", \"enabled\": true, \"category\": \"校园新闻\", \"imageUrl\": \"\", \"subtitle\": \"\", \"contentType\": \"article\", \"publishedAt\": \"\"}','admin','2026-08-11T10:26:43.560076+00:00','admin','2026-08-11T10:26:43.560076+00:00','','');
/*!40000 ALTER TABLE `page_versions` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `pages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pages` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `project_id` bigint NOT NULL,
  `code` varchar(160) NOT NULL,
  `category` varchar(120) NOT NULL DEFAULT '校园新闻',
  `source` varchar(160) NOT NULL DEFAULT '学校展示',
  `published_at` varchar(80) NOT NULL DEFAULT '',
  `title` varchar(255) NOT NULL,
  `subtitle` varchar(512) NOT NULL DEFAULT '',
  `body` mediumtext NOT NULL,
  `image_url` varchar(1024) NOT NULL DEFAULT '',
  `content_type` varchar(32) NOT NULL DEFAULT 'article',
  `accent` varchar(32) NOT NULL DEFAULT '#0f766e',
  `enabled` tinyint(1) NOT NULL DEFAULT '1',
  `review_status` varchar(32) NOT NULL DEFAULT 'approved',
  `pending_version_id` bigint DEFAULT NULL,
  `submitted_by` varchar(64) NOT NULL DEFAULT 'admin',
  `reviewed_by` varchar(64) NOT NULL DEFAULT 'admin',
  `review_note` varchar(1024) NOT NULL DEFAULT '',
  `updated_at` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_pages_project_code` (`project_id`,`code`),
  KEY `idx_pages_project_status` (`project_id`,`review_status`),
  KEY `idx_pages_code` (`code`),
  KEY `fk_pages_submitted_by` (`submitted_by`),
  CONSTRAINT `fk_pages_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_pages_submitted_by` FOREIGN KEY (`submitted_by`) REFERENCES `users` (`username`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `pages` WRITE;
/*!40000 ALTER TABLE `pages` DISABLE KEYS */;
INSERT INTO `pages` VALUES (1,1,'BJ-SERVICE','社会服务成果','毕节职业技术学院','','社会服务成果','聚焦技能培训、职业认定与乡村振兴服务，测试指标卡、图文组合与引用块。','<div class=\"lead-card\"><span>SOCIAL SERVICE</span><strong>服务地方产业与技能人才培养</strong><p>学校围绕毕节新发展理念示范区建设，聚焦现代能源、生态食品、先进装备制造、轻纺及健康医药等产业，持续开展职业技能培训、等级认定和乡村振兴服务。</p></div>\n<div class=\"stat-grid\"><div class=\"stat\"><strong>45000+</strong><span>培训人次</span><p>联合政校企完成多类型技术技能培训。</p></div><div class=\"stat\"><strong>15000+</strong><span>认定人次</span><p>面向学生和社会人员开展职业技能等级认定。</p></div><div class=\"stat\"><strong>八大产业</strong><span>服务方向</span><p>对接地方工业产业和特色农业发展需求。</p></div></div>\n<h2>重点服务方向</h2><ul><li>高技能人才、基层服务、煤矿安全技术、退役军人就业创业培训。</li><li>乡村振兴技能人才培养和非物质文化遗产传承人群研修研习。</li><li>职业技能等级认定与专项职业能力认定平台建设。</li></ul>\n<div class=\"photo-strip\"><figure><img src=\"/uploads/bijie-samples/image1.jpeg\" alt=\"培训现场\"><figcaption>毕节市财政财务基础业务培训班</figcaption></figure><figure><img src=\"/uploads/bijie-samples/image16.jpeg\" alt=\"稻米示范推广培训\"><figcaption>优质稻米示范推广培训进入田间地头</figcaption></figure></div>\n<blockquote>以学校技术资源和师资优势服务地方产业发展，助力毕节市人力资源开发和乡村全面振兴。</blockquote>','/uploads/bijie-samples/image16.jpeg','article','#49c5b6',1,'approved',NULL,'admin','admin','','2026-07-13T02:59:45.752052+00:00'),(2,1,'BJ-INTL','国际交流合作','毕节职业技术学院','','国际交流合作成果','从海外研学到职业标准输出，测试时间线、列表、图片和分隔线。','<div class=\"lead-card\"><span>GLOBAL COOPERATION</span><strong>从“引进来”到“走出去”的国际合作</strong><p>学校主动服务“一带一路”倡议和中国-东盟、中非教育合作，在海外交流、标准输出、多边合作、技能竞赛、人文往来等方面形成阶段性成果。</p></div>\n<div class=\"timeline\"><div><span>2024</span><p>组织师生赴泰国格乐大学开展短期研学，拓宽学生国际视野，增进中泰人文交流。</p></div><div><span>2025</span><p>牵头制定菲律宾《农业经理人》国家职业技能标准，并参与中国-东盟数字资源共建共享合作。</p></div><div><span>近三年</span><p>累计接待国（境）外来访团组 4 个，举办国际文化交流活动 4 场，签订校际合作备忘录 2 份。</p></div></div>\n<h2>成果看点</h2><ul><li>获批埃塞俄比亚国家职业标准开发项目认证。</li><li>课程资源被俄罗斯喀山联邦大学、埃塞俄比亚 Dire Dawa University 采用。</li><li>师生在金砖国家技能发展与技术创新大赛等国际赛事中获得多项奖项。</li></ul>\n<div class=\"photo-strip\"><figure><img src=\"/uploads/bijie-samples/image23.jpeg\" alt=\"泰国研学合影\"><figcaption>师生赴泰国格乐大学开展短期研学</figcaption></figure><figure><img src=\"/uploads/bijie-samples/image31.jpeg\" alt=\"国际人文交流活动\"><figcaption>“桥见”贵州毕节职院人文交流活动</figcaption></figure></div>\n<hr><p>这一页用于测试时间线、图文组合、列表与分隔线在大屏详情页中的可读性。</p>','/uploads/bijie-samples/image23.jpeg','article','#f8c35a',1,'approved',NULL,'admin','admin','','2026-07-13T03:07:46.158420+00:00'),(3,1,'BJ-GRAD','育人成果','教育科学系','','优秀毕业生张娅婷','以人物卡片、荣誉标签和分段叙事展示优秀毕业生成长故事。','<div class=\"profile-card\"><img src=\"/uploads/bijie-samples/image38.jpeg\" alt=\"张娅婷事迹照片\"><div><span>优秀毕业生</span><h3>张娅婷</h3><p>贵州省 2024 届优秀毕业生，学前教育专业。她在校园学习、学生工作、志愿服务和西部计划实践中持续成长。</p></div></div>\n<div class=\"badge-list\"><span>中共党员</span><span>教育科学系</span><span>学前教育</span><span>国家奖学金</span><span>省级优秀毕业生</span></div>\n<h2>一路追光，筑梦前行</h2><p>在校期间，她担任系学生会团总支副书记、学生会主席、班级团支部书记与班长，荣获全国乡村振兴“笃行计划优秀实践个人”、励志奖学金、省三好学生等荣誉。</p>\n<h3>敢担当</h3><p>2021 年至 2023 年，她承担学生组织工作，并于 2023 年赴马来西亚英迪国际大学短期访学，按期高质量完成学业。</p>\n<h3>能吃苦</h3><p>连续两年参加“三下乡”社会实践，组织关爱留守儿童、服务空巢老人和民族文化传承活动，在实践中锤炼专业能力和社会责任。</p>\n<h3>有理想</h3><p>2024 年 8 月，她投身贵州省毕节市七星关区碧阳街道办事处西部计划志愿服务，参与档案整理、热线回应和志愿服务等工作。</p>\n<div class=\"template-note\"><strong>教师评语</strong><p>希望你用行动去诠释教育的真谛，展现青春的力量。</p></div>','/uploads/bijie-samples/image37.png','article','#ff8f5a',1,'approved',NULL,'admin','admin','','2026-07-13T03:35:29.273403+00:00'),(4,1,'BJ-TEACHER','名师名匠','旅游管理系','','校内名师谭佳','用人物介绍、数据卡和成果列表展示名师名匠内容模板。','<div class=\"profile-card\"><img src=\"/uploads/bijie-samples/image39.jpeg\" alt=\"谭佳 portrait\"><div><span>校内名师</span><h3>谭佳</h3><p>旅游管理系副教授，聚焦旅游技能人才培养、数智赋能课程建设等教学教改方向。</p></div></div>\n<div class=\"stat-grid\"><div class=\"stat\"><strong>10+</strong><span>省部级、市厅级项目</span><p>主持并推进多项教学教改与社会服务项目。</p></div><div class=\"stat\"><strong>10000+</strong><span>课程覆盖人次</span><p>开发《乡村旅游导览实务》等培训课程。</p></div><div class=\"stat\"><strong>30+</strong><span>团队课题</span><p>围绕生态旅游、红色讲解、研学旅游开发等方向开展研究。</p></div></div>\n<h2>教学与产业服务成果</h2><ul><li>获全国教师教学能力大赛三等奖、省赛一等奖。</li><li>实践成果入选文旅部优秀成果并在全国推广。</li><li>教学案例入选文旅部旅游职业教育“五金”数智化建设典型案例。</li></ul>\n<div class=\"photo-strip\"><figure><img src=\"/uploads/bijie-samples/image32.jpeg\" alt=\"论坛发言\"><figcaption>在论坛活动中进行主旨发言</figcaption></figure><figure><img src=\"/uploads/bijie-samples/image30.jpeg\" alt=\"校园成果展示\"><figcaption>职业教育成果面向行业与社会展示</figcaption></figure></div>\n<blockquote>通过老带新、师带徒，优化人才结构，赋能贵州文旅产业高质量发展。</blockquote>','/uploads/bijie-samples/image32.jpeg','article','#8bd17c',1,'approved',NULL,'admin','admin','','2026-07-13T03:37:17.139551+00:00'),(5,1,'DEMO-10100043','校园新闻','学校展示','','欢迎来到成果展示','深圳先进技术研究院展会互动展示','这里可以放项目介绍、展品亮点、团队说明和现场引导文案。后台可以随时替换这些文字和图片。','/static/sample.svg','article','#0f766e',1,'approved',NULL,'admin','admin','','2026-07-16T04:00:22.063+00:00'),(8,13,'CI-OVERVIEW-13-05D267','专题概况','结构化资料','2026-08-11','222','222','<figure><img src=\"/uploads/c60e0d1c70d34d78996632d15ce7aa15.jpg\" alt=\"222\"><figcaption>222</figcaption></figure>','/uploads/c60e0d1c70d34d78996632d15ce7aa15.jpg','article','#f59a13',1,'approved',NULL,'admin','admin','','2026-08-11T10:22:01.904613+00:00'),(9,11,'EXT-DIGITAL-INTELLIGENCE-HUB','专题概况','结构化资料','2026-08-11','互动体验系统合集','汇聚人工智能、大模型交互和 AIGC 等互动体验系统入口。','<p>汇聚人工智能、大模型交互和 AIGC 等互动体验系统入口。<img src=\"/uploads/211d952b80ec471ca2cbafb9e877169f.png\" style=\"width: 412.969px\" class=\"\"></p><p class=\"external-link-entry\"><strong>互动体验系统合集</strong>：<a href=\"http://sxjsxy.szzfhs.com/\" target=\"_blank\" rel=\"noopener\">互动体验系统合集</a></p>','','article','#f59a13',1,'approved',NULL,'admin','admin','','2026-08-11T10:24:54.602834+00:00'),(10,11,'overview','校园新闻','学校展示','','专题概况','','<p>汇聚人工智能、大模型交互和 AIGC 等互动体验系统入口。</p><p>汇聚人工智能、大模型交互和 AIGC 等互动体验系统入口。</p><figure class=\"image\"><img src=\"/uploads/12d841efd1a74d8785c5a91b3f737fc1.png\" alt=\"\"></figure>','','article','#0f766e',1,'approved',NULL,'admin','admin','','2026-08-11T10:25:01.356311+00:00'),(11,7,'CI-COMPETITIONS-7-17EC69','技能大赛','结构化资料','2026-08-11','2223','2223','<p style=\"text-align: center\"><img src=\"/uploads/8d45276947824cc4ac9a72a2bb398bf1.png\" alt=\"2223\" style=\"max-width: 100%; width: 475.969px\" class=\"\"></p><p>2223这是的生产监控监控力度</p><figure><img src=\"/uploads/8d45276947824cc4ac9a72a2bb398bf1.png\" alt=\"2223\"><figcaption>2223</figcaption></figure>','/uploads/8d45276947824cc4ac9a72a2bb398bf1.png','article','#f59a13',1,'approved',NULL,'admin','admin','','2026-08-11T10:26:41.708926+00:00'),(12,7,'overview','校园新闻','学校展示','','','','<p></p><figure class=\"image\"><img src=\"/uploads/c4fb063eefd0478eafc7a373e75b2d16.jpg\" alt=\"\"></figure>','','article','#0f766e',1,'approved',NULL,'admin','admin','','2026-08-11T10:26:43.382958+00:00'),(13,7,'competitions','校园新闻','学校展示','','','','<figure class=\"image\"><img src=\"/uploads/60f3798d1c7b47628c2f7004c28d978e.jpg\" alt=\"\"></figure>','','article','#0f766e',1,'approved',NULL,'admin','admin','','2026-08-11T10:26:43.558542+00:00');
/*!40000 ALTER TABLE `pages` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `project_versions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_versions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `project_id` bigint NOT NULL,
  `status` varchar(32) NOT NULL DEFAULT 'pending',
  `snapshot` json NOT NULL,
  `submitted_by` varchar(64) NOT NULL DEFAULT '',
  `submitted_at` varchar(40) NOT NULL,
  `reviewed_by` varchar(64) NOT NULL DEFAULT '',
  `reviewed_at` varchar(40) NOT NULL DEFAULT '',
  `review_note` varchar(1024) NOT NULL DEFAULT '',
  `changes` varchar(2048) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `idx_project_versions_status` (`status`,`submitted_at`),
  KEY `idx_project_versions_project` (`project_id`),
  CONSTRAINT `fk_project_versions_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `project_versions` WRITE;
/*!40000 ALTER TABLE `project_versions` DISABLE KEYS */;
INSERT INTO `project_versions` VALUES (1,1,'approved','{\"name\": \"毕节职业技术学院\", \"accent\": \"#49c5b6\", \"idleCopy\": \"\", \"idleTitle\": \"毕节职业技术学院\", \"idleKicker\": \"学校简介\", \"portalType\": \"school\", \"welcomeTitle\": \"欢迎参观 {title}\", \"displayConfig\": {\"slides\": [{\"body\": \"围绕地方产业和乡村振兴需求，展示培训、认定和技术服务成果。\", \"meta\": \"SAMPLE 01\", \"label\": \"社会服务\", \"title\": \"服务地方发展\", \"visual\": \"gate\", \"imageUrl\": \"/uploads/bijie-samples/image1.jpeg\"}, {\"body\": \"展示海外交流、标准输出、多边合作和国际赛事成果。\", \"meta\": \"SAMPLE 02\", \"label\": \"国际交流\", \"title\": \"国际合作成果\", \"visual\": \"library\", \"imageUrl\": \"/uploads/bijie-samples/image23.jpeg\"}, {\"body\": \"用人物卡片和荣誉标签呈现优秀毕业生成长故事。\", \"meta\": \"SAMPLE 03\", \"label\": \"育人成果\", \"title\": \"优秀毕业生\", \"visual\": \"students\", \"imageUrl\": \"/uploads/bijie-samples/image37.png\"}], \"accent2\": \"#49c5b6\", \"scanCopy\": \"进入官网查看更多\", \"sideCopy\": \"\", \"badgeText\": \"\", \"scanTitle\": \"扫描学校官网二维码\", \"sideTitle\": \"\", \"brandColor\": \"#28539c\", \"schoolMeta\": \"社会服务 · 国际交流 · 育人成果 · 名师名匠\", \"schoolName\": \"\", \"summaryCopy\": \"社会服务、国际交流、优秀毕业生、校内名师四类内容\", \"summaryTags\": [\"富文本\", \"资料转展示页\", \"大屏预览\", \"二维码触发\"], \"logoImageUrl\": \"/uploads/acc2be26d71f4981b3c1f125390266a8.png\", \"qualityRules\": {\"minBodyChars\": 80, \"requireMedia\": true, \"requireModule\": true, \"requireSummary\": true, \"requireTypeAssets\": true}, \"scanImageUrl\": \"/uploads/fad5544323334f97a45f6afcf1eac08c.jpg\", \"summaryLabel\": \"BIJIE VOCATIONAL COLLEGE\", \"summaryTitle\": \"\", \"brandDeepColor\": \"#174275\", \"portalHomeCopy\": \"以专题门户为主线，串联专业建设、实训基地、产教融合、教学成果与专题资源。\", \"portalHomeTitle\": \"学校门户\", \"portalHomeFooter\": \"触摸卡片进入二级页面 · 长按返回首页\", \"portalHomeKicker\": \"School Portal\", \"moduleQualityRules\": {}, \"portalHomeCardChips\": [], \"portalHomeCardLabel\": \"创新育人专题\", \"portalHomeCardHidden\": false, \"portalHomeCardSummary\": \"\", \"portalHomeRouteLabels\": [\"学校门户\", \"专题门户\", \"板块资料\", \"专题展区\"], \"portalHomeSectionCopy\": \"以专题牵引院系共建，集中呈现跨系专业群、实训资源、产教融合与文化成果。\", \"portalHomeSectionTitle\": \"创新育人矩阵\", \"portalHomeCardSortOrder\": 0, \"portalHomeSectionKicker\": \"Integrated Showcase\"}, \"ownerUsername\": \"admin\", \"welcomeKicker\": \"Welcome\", \"defaultImageUrl\": \"/uploads/4fcaa6e34b5f40c7a7e2b58947b9de1c.jpg\", \"welcomeSubtitle\": \"即将进入展示页面\"}','admin','2026-08-11T10:09:40.805095+00:00','admin','2026-08-11T10:09:40.805095+00:00','','legacy import');
/*!40000 ALTER TABLE `project_versions` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projects` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(180) NOT NULL,
  `portal_type` varchar(32) NOT NULL DEFAULT 'department',
  `portal_slug` varchar(160) NOT NULL DEFAULT '',
  `idle_kicker` varchar(120) NOT NULL DEFAULT '学校简介',
  `idle_title` varchar(255) NOT NULL DEFAULT '欢迎来到毕节职业技术学院',
  `idle_copy` text NOT NULL,
  `welcome_kicker` varchar(120) NOT NULL DEFAULT 'Welcome',
  `welcome_title` varchar(255) NOT NULL DEFAULT '欢迎参观 {title}',
  `welcome_subtitle` varchar(255) NOT NULL DEFAULT '即将进入展示页面',
  `default_image_url` varchar(1024) NOT NULL DEFAULT '/static/expo-stage.png',
  `accent` varchar(32) NOT NULL DEFAULT '#f59a13',
  `display_config` json NOT NULL,
  `deployed` tinyint(1) NOT NULL DEFAULT '0',
  `content_deployed` tinyint(1) NOT NULL DEFAULT '0',
  `deployed_at` varchar(40) NOT NULL DEFAULT '',
  `content_deployed_at` varchar(40) NOT NULL DEFAULT '',
  `owner_username` varchar(64) NOT NULL DEFAULT 'admin',
  `config_status` varchar(32) NOT NULL DEFAULT 'approved',
  `pending_config_version_id` bigint DEFAULT NULL,
  `updated_at` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_projects_owner` (`owner_username`),
  KEY `idx_projects_portal` (`portal_type`,`portal_slug`),
  KEY `idx_projects_deployed` (`deployed`),
  KEY `idx_projects_content_deployed` (`content_deployed`),
  KEY `idx_projects_config_status` (`config_status`),
  CONSTRAINT `fk_projects_owner` FOREIGN KEY (`owner_username`) REFERENCES `users` (`username`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `projects` WRITE;
/*!40000 ALTER TABLE `projects` DISABLE KEYS */;
INSERT INTO `projects` VALUES (1,'毕节职业技术学院','school','','学校简介','毕节职业技术学院','','Welcome','欢迎参观 {title}','即将进入展示页面','/uploads/4fcaa6e34b5f40c7a7e2b58947b9de1c.jpg','#49c5b6','{\"slides\": [{\"body\": \"围绕地方产业和乡村振兴需求，展示培训、认定和技术服务成果。\", \"meta\": \"SAMPLE 01\", \"label\": \"社会服务\", \"title\": \"服务地方发展\", \"visual\": \"gate\", \"imageUrl\": \"/uploads/bijie-samples/image1.jpeg\"}, {\"body\": \"展示海外交流、标准输出、多边合作和国际赛事成果。\", \"meta\": \"SAMPLE 02\", \"label\": \"国际交流\", \"title\": \"国际合作成果\", \"visual\": \"library\", \"imageUrl\": \"/uploads/bijie-samples/image23.jpeg\"}, {\"body\": \"用人物卡片和荣誉标签呈现优秀毕业生成长故事。\", \"meta\": \"SAMPLE 03\", \"label\": \"育人成果\", \"title\": \"优秀毕业生\", \"visual\": \"students\", \"imageUrl\": \"/uploads/bijie-samples/image37.png\"}], \"accent2\": \"#49c5b6\", \"scanCopy\": \"进入官网查看更多\", \"sideCopy\": \"\", \"badgeText\": \"\", \"scanTitle\": \"扫描学校官网二维码\", \"sideTitle\": \"\", \"brandColor\": \"#28539c\", \"schoolMeta\": \"社会服务 · 国际交流 · 育人成果 · 名师名匠\", \"schoolName\": \"\", \"summaryCopy\": \"社会服务、国际交流、优秀毕业生、校内名师四类内容\", \"summaryTags\": [\"富文本\", \"资料转展示页\", \"大屏预览\", \"二维码触发\"], \"logoImageUrl\": \"/uploads/acc2be26d71f4981b3c1f125390266a8.png\", \"scanImageUrl\": \"/uploads/fad5544323334f97a45f6afcf1eac08c.jpg\", \"summaryLabel\": \"BIJIE VOCATIONAL COLLEGE\", \"summaryTitle\": \"\", \"brandDeepColor\": \"#174275\"}',1,1,'2026-07-14T02:15:14.820954+00:00','2026-08-11T10:11:37.851742+00:00','admin','approved',NULL,'2026-07-14T02:15:14.820954+00:00'),(2,'工矿建筑系','department','mining-construction','专题门户','工矿建筑系','智慧矿山、智能制造与现代建造。','Welcome','欢迎参观 {title}','即将进入展示页面','/uploads/blueprint/departments/mining-construction/images/img01.webp','#f59a13','{\"slides\": [{\"body\": \"用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。\", \"meta\": \"WELCOME 01\", \"label\": \"校园入口与主楼\", \"title\": \"学校形象\", \"visual\": \"gate\", \"imageUrl\": \"\"}, {\"body\": \"观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。\", \"meta\": \"WELCOME 02\", \"label\": \"扫码内容导览\", \"title\": \"成果导览\", \"visual\": \"library\", \"imageUrl\": \"\"}, {\"body\": \"自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。\", \"meta\": \"WELCOME 03\", \"label\": \"现场节奏\", \"title\": \"现场节奏\", \"visual\": \"students\", \"imageUrl\": \"\"}], \"accent2\": \"#47b7ff\", \"scanCopy\": \"大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。\", \"sideCopy\": \"\", \"badgeText\": \"欢迎到校\", \"scanTitle\": \"扫描展项二维码\", \"sideTitle\": \"\", \"brandColor\": \"#28539c\", \"schoolMeta\": \"欢迎来到校园 · 同心特色校园文化\", \"schoolName\": \"毕节职业技术学院\", \"summaryCopy\": \"新版欢迎页采用舞台式首屏：左侧大图沉浸、右侧轮播导览、顶部显示实时通道状态，更适合展会现场远距离观看。\", \"summaryTags\": [\"远距可读\", \"实时扫码\", \"项目部署\"], \"logoImageUrl\": \"\", \"qualityRules\": {\"minBodyChars\": 80, \"requireMedia\": true, \"requireModule\": true, \"requireSummary\": true, \"requireTypeAssets\": true}, \"scanImageUrl\": \"\", \"summaryLabel\": \"WELCOME OVERVIEW\", \"summaryTitle\": \"从学校形象到展项内容，形成完整参观动线。\", \"brandDeepColor\": \"#20468b\", \"portalHomeCopy\": \"以专题门户为主线，串联专业建设、实训基地、产教融合、教学成果与专题资源。\", \"portalHomeTitle\": \"学校门户\", \"portalHomeFooter\": \"触摸卡片进入二级页面 · 长按返回首页\", \"portalHomeKicker\": \"School Portal\", \"moduleQualityRules\": {}, \"portalHomeCardChips\": [], \"portalHomeCardLabel\": \"创新育人专题\", \"portalHomeCardHidden\": false, \"portalHomeCardSummary\": \"\", \"portalHomeRouteLabels\": [\"学校门户\", \"专题门户\", \"板块资料\", \"专题展区\"], \"portalHomeSectionCopy\": \"以专题牵引院系共建，集中呈现跨系专业群、实训资源、产教融合与文化成果。\", \"portalHomeSectionTitle\": \"创新育人矩阵\", \"portalHomeCardSortOrder\": 0, \"portalHomeSectionKicker\": \"Integrated Showcase\"}',0,0,'','','admin','approved',NULL,'2026-08-11T10:15:56.998821+00:00'),(3,'财政经济系','department','finance','专题门户','财政经济系','数字商贸、智慧物流与财务实践。','Welcome','欢迎参观 {title}','即将进入展示页面','/uploads/blueprint/departments/finance/images/img01.webp','#f59a13','{\"slides\": [{\"body\": \"用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。\", \"meta\": \"WELCOME 01\", \"label\": \"校园入口与主楼\", \"title\": \"学校形象\", \"visual\": \"gate\", \"imageUrl\": \"\"}, {\"body\": \"观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。\", \"meta\": \"WELCOME 02\", \"label\": \"扫码内容导览\", \"title\": \"成果导览\", \"visual\": \"library\", \"imageUrl\": \"\"}, {\"body\": \"自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。\", \"meta\": \"WELCOME 03\", \"label\": \"现场节奏\", \"title\": \"现场节奏\", \"visual\": \"students\", \"imageUrl\": \"\"}], \"accent2\": \"#47b7ff\", \"scanCopy\": \"大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。\", \"sideCopy\": \"\", \"badgeText\": \"欢迎到校\", \"scanTitle\": \"扫描展项二维码\", \"sideTitle\": \"\", \"brandColor\": \"#28539c\", \"schoolMeta\": \"欢迎来到校园 · 同心特色校园文化\", \"schoolName\": \"毕节职业技术学院\", \"summaryCopy\": \"新版欢迎页采用舞台式首屏：左侧大图沉浸、右侧轮播导览、顶部显示实时通道状态，更适合展会现场远距离观看。\", \"summaryTags\": [\"远距可读\", \"实时扫码\", \"项目部署\"], \"logoImageUrl\": \"\", \"qualityRules\": {\"minBodyChars\": 80, \"requireMedia\": true, \"requireModule\": true, \"requireSummary\": true, \"requireTypeAssets\": true}, \"scanImageUrl\": \"\", \"summaryLabel\": \"WELCOME OVERVIEW\", \"summaryTitle\": \"从学校形象到展项内容，形成完整参观动线。\", \"brandDeepColor\": \"#20468b\", \"portalHomeCopy\": \"以专题门户为主线，串联专业建设、实训基地、产教融合、教学成果与专题资源。\", \"portalHomeTitle\": \"学校门户\", \"portalHomeFooter\": \"触摸卡片进入二级页面 · 长按返回首页\", \"portalHomeKicker\": \"School Portal\", \"moduleQualityRules\": {}, \"portalHomeCardChips\": [], \"portalHomeCardLabel\": \"创新育人专题\", \"portalHomeCardHidden\": false, \"portalHomeCardSummary\": \"\", \"portalHomeRouteLabels\": [\"学校门户\", \"专题门户\", \"板块资料\", \"专题展区\"], \"portalHomeSectionCopy\": \"以专题牵引院系共建，集中呈现跨系专业群、实训资源、产教融合与文化成果。\", \"portalHomeSectionTitle\": \"创新育人矩阵\", \"portalHomeCardSortOrder\": 0, \"portalHomeSectionKicker\": \"Integrated Showcase\"}',0,0,'','','admin','approved',NULL,'2026-08-11T10:15:57.000372+00:00'),(4,'电子信息工程系','department','information','专题门户','电子信息工程系','人工智能、网络安全与数字技术。','Welcome','欢迎参观 {title}','即将进入展示页面','/uploads/blueprint/departments/information/images/img01.webp','#f59a13','{\"slides\": [{\"body\": \"用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。\", \"meta\": \"WELCOME 01\", \"label\": \"校园入口与主楼\", \"title\": \"学校形象\", \"visual\": \"gate\", \"imageUrl\": \"\"}, {\"body\": \"观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。\", \"meta\": \"WELCOME 02\", \"label\": \"扫码内容导览\", \"title\": \"成果导览\", \"visual\": \"library\", \"imageUrl\": \"\"}, {\"body\": \"自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。\", \"meta\": \"WELCOME 03\", \"label\": \"现场节奏\", \"title\": \"现场节奏\", \"visual\": \"students\", \"imageUrl\": \"\"}], \"accent2\": \"#47b7ff\", \"scanCopy\": \"大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。\", \"sideCopy\": \"\", \"badgeText\": \"欢迎到校\", \"scanTitle\": \"扫描展项二维码\", \"sideTitle\": \"\", \"brandColor\": \"#28539c\", \"schoolMeta\": \"欢迎来到校园 · 同心特色校园文化\", \"schoolName\": \"毕节职业技术学院\", \"summaryCopy\": \"新版欢迎页采用舞台式首屏：左侧大图沉浸、右侧轮播导览、顶部显示实时通道状态，更适合展会现场远距离观看。\", \"summaryTags\": [\"远距可读\", \"实时扫码\", \"项目部署\"], \"logoImageUrl\": \"\", \"qualityRules\": {\"minBodyChars\": 80, \"requireMedia\": true, \"requireModule\": true, \"requireSummary\": true, \"requireTypeAssets\": true}, \"scanImageUrl\": \"\", \"summaryLabel\": \"WELCOME OVERVIEW\", \"summaryTitle\": \"从学校形象到展项内容，形成完整参观动线。\", \"brandDeepColor\": \"#20468b\", \"portalHomeCopy\": \"以专题门户为主线，串联专业建设、实训基地、产教融合、教学成果与专题资源。\", \"portalHomeTitle\": \"学校门户\", \"portalHomeFooter\": \"触摸卡片进入二级页面 · 长按返回首页\", \"portalHomeKicker\": \"School Portal\", \"moduleQualityRules\": {}, \"portalHomeCardChips\": [], \"portalHomeCardLabel\": \"创新育人专题\", \"portalHomeCardHidden\": false, \"portalHomeCardSummary\": \"\", \"portalHomeRouteLabels\": [\"学校门户\", \"专题门户\", \"板块资料\", \"专题展区\"], \"portalHomeSectionCopy\": \"以专题牵引院系共建，集中呈现跨系专业群、实训资源、产教融合与文化成果。\", \"portalHomeSectionTitle\": \"创新育人矩阵\", \"portalHomeCardSortOrder\": 0, \"portalHomeSectionKicker\": \"Integrated Showcase\"}',0,0,'','','admin','approved',NULL,'2026-08-11T10:15:57.002063+00:00'),(5,'医学护理系','department','medical-nursing','专题门户','医学护理系','临床护理、康养服务与急救教育。','Welcome','欢迎参观 {title}','即将进入展示页面','/uploads/blueprint/departments/medical-nursing/images/img01.webp','#f59a13','{\"slides\": [{\"body\": \"用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。\", \"meta\": \"WELCOME 01\", \"label\": \"校园入口与主楼\", \"title\": \"学校形象\", \"visual\": \"gate\", \"imageUrl\": \"\"}, {\"body\": \"观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。\", \"meta\": \"WELCOME 02\", \"label\": \"扫码内容导览\", \"title\": \"成果导览\", \"visual\": \"library\", \"imageUrl\": \"\"}, {\"body\": \"自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。\", \"meta\": \"WELCOME 03\", \"label\": \"现场节奏\", \"title\": \"现场节奏\", \"visual\": \"students\", \"imageUrl\": \"\"}], \"accent2\": \"#47b7ff\", \"scanCopy\": \"大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。\", \"sideCopy\": \"\", \"badgeText\": \"欢迎到校\", \"scanTitle\": \"扫描展项二维码\", \"sideTitle\": \"\", \"brandColor\": \"#28539c\", \"schoolMeta\": \"欢迎来到校园 · 同心特色校园文化\", \"schoolName\": \"毕节职业技术学院\", \"summaryCopy\": \"新版欢迎页采用舞台式首屏：左侧大图沉浸、右侧轮播导览、顶部显示实时通道状态，更适合展会现场远距离观看。\", \"summaryTags\": [\"远距可读\", \"实时扫码\", \"项目部署\"], \"logoImageUrl\": \"\", \"qualityRules\": {\"minBodyChars\": 80, \"requireMedia\": true, \"requireModule\": true, \"requireSummary\": true, \"requireTypeAssets\": true}, \"scanImageUrl\": \"\", \"summaryLabel\": \"WELCOME OVERVIEW\", \"summaryTitle\": \"从学校形象到展项内容，形成完整参观动线。\", \"brandDeepColor\": \"#20468b\", \"portalHomeCopy\": \"以专题门户为主线，串联专业建设、实训基地、产教融合、教学成果与专题资源。\", \"portalHomeTitle\": \"学校门户\", \"portalHomeFooter\": \"触摸卡片进入二级页面 · 长按返回首页\", \"portalHomeKicker\": \"School Portal\", \"moduleQualityRules\": {}, \"portalHomeCardChips\": [], \"portalHomeCardLabel\": \"创新育人专题\", \"portalHomeCardHidden\": false, \"portalHomeCardSummary\": \"\", \"portalHomeRouteLabels\": [\"学校门户\", \"专题门户\", \"板块资料\", \"专题展区\"], \"portalHomeSectionCopy\": \"以专题牵引院系共建，集中呈现跨系专业群、实训资源、产教融合与文化成果。\", \"portalHomeSectionTitle\": \"创新育人矩阵\", \"portalHomeCardSortOrder\": 0, \"portalHomeSectionKicker\": \"Integrated Showcase\"}',0,0,'','','admin','approved',NULL,'2026-08-11T10:15:57.003632+00:00'),(6,'旅游管理系','department','tourism','专题门户','旅游管理系','数字文旅、酒店运营与烹饪技艺。','Welcome','欢迎参观 {title}','即将进入展示页面','/uploads/blueprint/departments/tourism/images/img01.webp','#f59a13','{\"slides\": [{\"body\": \"用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。\", \"meta\": \"WELCOME 01\", \"label\": \"校园入口与主楼\", \"title\": \"学校形象\", \"visual\": \"gate\", \"imageUrl\": \"\"}, {\"body\": \"观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。\", \"meta\": \"WELCOME 02\", \"label\": \"扫码内容导览\", \"title\": \"成果导览\", \"visual\": \"library\", \"imageUrl\": \"\"}, {\"body\": \"自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。\", \"meta\": \"WELCOME 03\", \"label\": \"现场节奏\", \"title\": \"现场节奏\", \"visual\": \"students\", \"imageUrl\": \"\"}], \"accent2\": \"#47b7ff\", \"scanCopy\": \"大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。\", \"sideCopy\": \"\", \"badgeText\": \"欢迎到校\", \"scanTitle\": \"扫描展项二维码\", \"sideTitle\": \"\", \"brandColor\": \"#28539c\", \"schoolMeta\": \"欢迎来到校园 · 同心特色校园文化\", \"schoolName\": \"毕节职业技术学院\", \"summaryCopy\": \"新版欢迎页采用舞台式首屏：左侧大图沉浸、右侧轮播导览、顶部显示实时通道状态，更适合展会现场远距离观看。\", \"summaryTags\": [\"远距可读\", \"实时扫码\", \"项目部署\"], \"logoImageUrl\": \"\", \"qualityRules\": {\"minBodyChars\": 80, \"requireMedia\": true, \"requireModule\": true, \"requireSummary\": true, \"requireTypeAssets\": true}, \"scanImageUrl\": \"\", \"summaryLabel\": \"WELCOME OVERVIEW\", \"summaryTitle\": \"从学校形象到展项内容，形成完整参观动线。\", \"brandDeepColor\": \"#20468b\", \"portalHomeCopy\": \"以专题门户为主线，串联专业建设、实训基地、产教融合、教学成果与专题资源。\", \"portalHomeTitle\": \"学校门户\", \"portalHomeFooter\": \"触摸卡片进入二级页面 · 长按返回首页\", \"portalHomeKicker\": \"School Portal\", \"moduleQualityRules\": {}, \"portalHomeCardChips\": [], \"portalHomeCardLabel\": \"创新育人专题\", \"portalHomeCardHidden\": false, \"portalHomeCardSummary\": \"\", \"portalHomeRouteLabels\": [\"学校门户\", \"专题门户\", \"板块资料\", \"专题展区\"], \"portalHomeSectionCopy\": \"以专题牵引院系共建，集中呈现跨系专业群、实训资源、产教融合与文化成果。\", \"portalHomeSectionTitle\": \"创新育人矩阵\", \"portalHomeCardSortOrder\": 0, \"portalHomeSectionKicker\": \"Integrated Showcase\"}',0,0,'','','admin','approved',NULL,'2026-08-11T10:15:57.005197+00:00'),(7,'现代农业','topic','modern-agriculture','专题门户','现代农业','山地特色农业、乡村振兴与数字化生产服务。','Welcome','欢迎参观 {title}','即将进入展示页面','/uploads/4fcaa6e34b5f40c7a7e2b58947b9de1c.jpg','#f59a13','{\"slides\": [{\"body\": \"用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。\", \"meta\": \"WELCOME 01\", \"label\": \"校园入口与主楼\", \"title\": \"学校形象\", \"visual\": \"gate\", \"imageUrl\": \"\"}, {\"body\": \"观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。\", \"meta\": \"WELCOME 02\", \"label\": \"扫码内容导览\", \"title\": \"成果导览\", \"visual\": \"library\", \"imageUrl\": \"\"}, {\"body\": \"自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。\", \"meta\": \"WELCOME 03\", \"label\": \"现场节奏\", \"title\": \"现场节奏\", \"visual\": \"students\", \"imageUrl\": \"\"}], \"accent2\": \"#47b7ff\", \"scanCopy\": \"大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。\", \"sideCopy\": \"\", \"badgeText\": \"欢迎到校\", \"scanTitle\": \"扫描展项二维码\", \"sideTitle\": \"\", \"brandColor\": \"#28539c\", \"schoolMeta\": \"欢迎来到校园 · 同心特色校园文化\", \"schoolName\": \"毕节职业技术学院\", \"summaryCopy\": \"新版欢迎页采用舞台式首屏：左侧大图沉浸、右侧轮播导览、顶部显示实时通道状态，更适合展会现场远距离观看。\", \"summaryTags\": [\"远距可读\", \"实时扫码\", \"项目部署\"], \"logoImageUrl\": \"\", \"qualityRules\": {\"minBodyChars\": 80, \"requireMedia\": true, \"requireModule\": true, \"requireSummary\": true, \"requireTypeAssets\": true}, \"scanImageUrl\": \"\", \"summaryLabel\": \"WELCOME OVERVIEW\", \"summaryTitle\": \"从学校形象到展项内容，形成完整参观动线。\", \"brandDeepColor\": \"#20468b\", \"portalHomeCopy\": \"以专题门户为主线，串联专业建设、实训基地、产教融合、教学成果与专题资源。\", \"portalHomeTitle\": \"学校门户\", \"portalHomeFooter\": \"触摸卡片进入二级页面 · 长按返回首页\", \"portalHomeKicker\": \"School Portal\", \"moduleQualityRules\": {}, \"portalHomeCardChips\": [], \"portalHomeCardLabel\": \"创新育人专题\", \"portalHomeCardHidden\": false, \"portalHomeCardSummary\": \"\", \"portalHomeRouteLabels\": [\"学校门户\", \"专题门户\", \"板块资料\", \"专题展区\"], \"portalHomeSectionCopy\": \"以专题牵引院系共建，集中呈现跨系专业群、实训资源、产教融合与文化成果。\", \"portalHomeSectionTitle\": \"创新育人矩阵\", \"portalHomeCardSortOrder\": 0, \"portalHomeSectionKicker\": \"Integrated Showcase\"}',0,0,'','','admin','approved',NULL,'2026-08-11T10:15:57.008867+00:00'),(8,'数字文旅','topic','digital-tourism','专题门户','数字文旅','数字文旅、酒店运营、烹饪技艺与服务场景。','Welcome','欢迎参观 {title}','即将进入展示页面','/uploads/blueprint/topics/digital-tourism/images/img01.webp','#f59a13','{\"slides\": [{\"body\": \"用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。\", \"meta\": \"WELCOME 01\", \"label\": \"校园入口与主楼\", \"title\": \"学校形象\", \"visual\": \"gate\", \"imageUrl\": \"\"}, {\"body\": \"观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。\", \"meta\": \"WELCOME 02\", \"label\": \"扫码内容导览\", \"title\": \"成果导览\", \"visual\": \"library\", \"imageUrl\": \"\"}, {\"body\": \"自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。\", \"meta\": \"WELCOME 03\", \"label\": \"现场节奏\", \"title\": \"现场节奏\", \"visual\": \"students\", \"imageUrl\": \"\"}], \"accent2\": \"#47b7ff\", \"scanCopy\": \"大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。\", \"sideCopy\": \"\", \"badgeText\": \"欢迎到校\", \"scanTitle\": \"扫描展项二维码\", \"sideTitle\": \"\", \"brandColor\": \"#28539c\", \"schoolMeta\": \"欢迎来到校园 · 同心特色校园文化\", \"schoolName\": \"毕节职业技术学院\", \"summaryCopy\": \"新版欢迎页采用舞台式首屏：左侧大图沉浸、右侧轮播导览、顶部显示实时通道状态，更适合展会现场远距离观看。\", \"summaryTags\": [\"远距可读\", \"实时扫码\", \"项目部署\"], \"logoImageUrl\": \"\", \"qualityRules\": {\"minBodyChars\": 80, \"requireMedia\": true, \"requireModule\": true, \"requireSummary\": true, \"requireTypeAssets\": true}, \"scanImageUrl\": \"\", \"summaryLabel\": \"WELCOME OVERVIEW\", \"summaryTitle\": \"从学校形象到展项内容，形成完整参观动线。\", \"brandDeepColor\": \"#20468b\", \"portalHomeCopy\": \"以专题门户为主线，串联专业建设、实训基地、产教融合、教学成果与专题资源。\", \"portalHomeTitle\": \"学校门户\", \"portalHomeFooter\": \"触摸卡片进入二级页面 · 长按返回首页\", \"portalHomeKicker\": \"School Portal\", \"moduleQualityRules\": {}, \"portalHomeCardChips\": [], \"portalHomeCardLabel\": \"创新育人专题\", \"portalHomeCardHidden\": false, \"portalHomeCardSummary\": \"\", \"portalHomeRouteLabels\": [\"学校门户\", \"专题门户\", \"板块资料\", \"专题展区\"], \"portalHomeSectionCopy\": \"以专题牵引院系共建，集中呈现跨系专业群、实训资源、产教融合与文化成果。\", \"portalHomeSectionTitle\": \"创新育人矩阵\", \"portalHomeCardSortOrder\": 0, \"portalHomeSectionKicker\": \"Integrated Showcase\"}',0,0,'','','admin','approved',NULL,'2026-08-11T10:15:57.010409+00:00'),(9,'智慧康养','topic','smart-healthcare','专题门户','智慧康养','护理康养、急救教育、健康管理与服务运营。','Welcome','欢迎参观 {title}','即将进入展示页面','/uploads/blueprint/departments/medical-nursing/images/img01.webp','#f59a13','{\"slides\": [{\"body\": \"用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。\", \"meta\": \"WELCOME 01\", \"label\": \"校园入口与主楼\", \"title\": \"学校形象\", \"visual\": \"gate\", \"imageUrl\": \"\"}, {\"body\": \"观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。\", \"meta\": \"WELCOME 02\", \"label\": \"扫码内容导览\", \"title\": \"成果导览\", \"visual\": \"library\", \"imageUrl\": \"\"}, {\"body\": \"自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。\", \"meta\": \"WELCOME 03\", \"label\": \"现场节奏\", \"title\": \"现场节奏\", \"visual\": \"students\", \"imageUrl\": \"\"}], \"accent2\": \"#47b7ff\", \"scanCopy\": \"大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。\", \"sideCopy\": \"\", \"badgeText\": \"欢迎到校\", \"scanTitle\": \"扫描展项二维码\", \"sideTitle\": \"\", \"brandColor\": \"#28539c\", \"schoolMeta\": \"欢迎来到校园 · 同心特色校园文化\", \"schoolName\": \"毕节职业技术学院\", \"summaryCopy\": \"新版欢迎页采用舞台式首屏：左侧大图沉浸、右侧轮播导览、顶部显示实时通道状态，更适合展会现场远距离观看。\", \"summaryTags\": [\"远距可读\", \"实时扫码\", \"项目部署\"], \"logoImageUrl\": \"\", \"qualityRules\": {\"minBodyChars\": 80, \"requireMedia\": true, \"requireModule\": true, \"requireSummary\": true, \"requireTypeAssets\": true}, \"scanImageUrl\": \"\", \"summaryLabel\": \"WELCOME OVERVIEW\", \"summaryTitle\": \"从学校形象到展项内容，形成完整参观动线。\", \"brandDeepColor\": \"#20468b\", \"portalHomeCopy\": \"以专题门户为主线，串联专业建设、实训基地、产教融合、教学成果与专题资源。\", \"portalHomeTitle\": \"学校门户\", \"portalHomeFooter\": \"触摸卡片进入二级页面 · 长按返回首页\", \"portalHomeKicker\": \"School Portal\", \"moduleQualityRules\": {}, \"portalHomeCardChips\": [], \"portalHomeCardLabel\": \"创新育人专题\", \"portalHomeCardHidden\": false, \"portalHomeCardSummary\": \"\", \"portalHomeRouteLabels\": [\"学校门户\", \"专题门户\", \"板块资料\", \"专题展区\"], \"portalHomeSectionCopy\": \"以专题牵引院系共建，集中呈现跨系专业群、实训资源、产教融合与文化成果。\", \"portalHomeSectionTitle\": \"创新育人矩阵\", \"portalHomeCardSortOrder\": 0, \"portalHomeSectionKicker\": \"Integrated Showcase\"}',0,0,'','','admin','approved',NULL,'2026-08-11T10:15:57.014066+00:00'),(10,'财经商贸','topic','finance-commerce','专题门户','财经商贸','数字商贸、电商物流与产教融合。','Welcome','欢迎参观 {title}','即将进入展示页面','/uploads/blueprint/topics/finance-commerce/images/img01.webp','#f59a13','{\"slides\": [{\"body\": \"用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。\", \"meta\": \"WELCOME 01\", \"label\": \"校园入口与主楼\", \"title\": \"学校形象\", \"visual\": \"gate\", \"imageUrl\": \"\"}, {\"body\": \"观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。\", \"meta\": \"WELCOME 02\", \"label\": \"扫码内容导览\", \"title\": \"成果导览\", \"visual\": \"library\", \"imageUrl\": \"\"}, {\"body\": \"自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。\", \"meta\": \"WELCOME 03\", \"label\": \"现场节奏\", \"title\": \"现场节奏\", \"visual\": \"students\", \"imageUrl\": \"\"}], \"accent2\": \"#47b7ff\", \"scanCopy\": \"大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。\", \"sideCopy\": \"\", \"badgeText\": \"欢迎到校\", \"scanTitle\": \"扫描展项二维码\", \"sideTitle\": \"\", \"brandColor\": \"#28539c\", \"schoolMeta\": \"欢迎来到校园 · 同心特色校园文化\", \"schoolName\": \"毕节职业技术学院\", \"summaryCopy\": \"新版欢迎页采用舞台式首屏：左侧大图沉浸、右侧轮播导览、顶部显示实时通道状态，更适合展会现场远距离观看。\", \"summaryTags\": [\"远距可读\", \"实时扫码\", \"项目部署\"], \"logoImageUrl\": \"\", \"qualityRules\": {\"minBodyChars\": 80, \"requireMedia\": true, \"requireModule\": true, \"requireSummary\": true, \"requireTypeAssets\": true}, \"scanImageUrl\": \"\", \"summaryLabel\": \"WELCOME OVERVIEW\", \"summaryTitle\": \"从学校形象到展项内容，形成完整参观动线。\", \"brandDeepColor\": \"#20468b\", \"portalHomeCopy\": \"以专题门户为主线，串联专业建设、实训基地、产教融合、教学成果与专题资源。\", \"portalHomeTitle\": \"学校门户\", \"portalHomeFooter\": \"触摸卡片进入二级页面 · 长按返回首页\", \"portalHomeKicker\": \"School Portal\", \"moduleQualityRules\": {}, \"portalHomeCardChips\": [], \"portalHomeCardLabel\": \"创新育人专题\", \"portalHomeCardHidden\": false, \"portalHomeCardSummary\": \"\", \"portalHomeRouteLabels\": [\"学校门户\", \"专题门户\", \"板块资料\", \"专题展区\"], \"portalHomeSectionCopy\": \"以专题牵引院系共建，集中呈现跨系专业群、实训资源、产教融合与文化成果。\", \"portalHomeSectionTitle\": \"创新育人矩阵\", \"portalHomeCardSortOrder\": 0, \"portalHomeSectionKicker\": \"Integrated Showcase\"}',0,0,'','','admin','approved',NULL,'2026-08-11T10:15:57.015635+00:00'),(11,'数智技术','topic','digital-intelligence','专题门户','数智技术','人工智能、网络安全、数据应用与跨专业赋能。','Welcome','欢迎参观 {title}','即将进入展示页面','/uploads/blueprint/departments/information/images/img01.webp','#f59a13','{\"slides\": [{\"body\": \"用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。\", \"meta\": \"WELCOME 01\", \"label\": \"校园入口与主楼\", \"title\": \"学校形象\", \"visual\": \"gate\", \"imageUrl\": \"\"}, {\"body\": \"观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。\", \"meta\": \"WELCOME 02\", \"label\": \"扫码内容导览\", \"title\": \"成果导览\", \"visual\": \"library\", \"imageUrl\": \"\"}, {\"body\": \"自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。\", \"meta\": \"WELCOME 03\", \"label\": \"现场节奏\", \"title\": \"现场节奏\", \"visual\": \"students\", \"imageUrl\": \"\"}], \"accent2\": \"#47b7ff\", \"scanCopy\": \"大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。\", \"sideCopy\": \"\", \"badgeText\": \"欢迎到校\", \"scanTitle\": \"扫描展项二维码\", \"sideTitle\": \"\", \"brandColor\": \"#28539c\", \"schoolMeta\": \"欢迎来到校园 · 同心特色校园文化\", \"schoolName\": \"毕节职业技术学院\", \"summaryCopy\": \"新版欢迎页采用舞台式首屏：左侧大图沉浸、右侧轮播导览、顶部显示实时通道状态，更适合展会现场远距离观看。\", \"summaryTags\": [\"远距可读\", \"实时扫码\", \"项目部署\"], \"logoImageUrl\": \"\", \"qualityRules\": {\"minBodyChars\": 80, \"requireMedia\": true, \"requireModule\": true, \"requireSummary\": true, \"requireTypeAssets\": true}, \"scanImageUrl\": \"\", \"summaryLabel\": \"WELCOME OVERVIEW\", \"summaryTitle\": \"从学校形象到展项内容，形成完整参观动线。\", \"brandDeepColor\": \"#20468b\", \"portalHomeCopy\": \"以专题门户为主线，串联专业建设、实训基地、产教融合、教学成果与专题资源。\", \"portalHomeTitle\": \"学校门户\", \"portalHomeFooter\": \"触摸卡片进入二级页面 · 长按返回首页\", \"portalHomeKicker\": \"School Portal\", \"moduleQualityRules\": {}, \"portalHomeCardChips\": [], \"portalHomeCardLabel\": \"创新育人专题\", \"portalHomeCardHidden\": false, \"portalHomeCardSummary\": \"\", \"portalHomeRouteLabels\": [\"学校门户\", \"专题门户\", \"板块资料\", \"专题展区\"], \"portalHomeSectionCopy\": \"以专题牵引院系共建，集中呈现跨系专业群、实训资源、产教融合与文化成果。\", \"portalHomeSectionTitle\": \"创新育人矩阵\", \"portalHomeCardSortOrder\": 0, \"portalHomeSectionKicker\": \"Integrated Showcase\"}',0,0,'','','admin','approved',NULL,'2026-08-11T10:15:57.017798+00:00'),(12,'智慧能源','topic','smart-energy','专题门户','智慧能源','绿色能源、智能开采与化工安全。','Welcome','欢迎参观 {title}','即将进入展示页面','/uploads/blueprint/topics/smart-energy/images/img01.webp','#f59a13','{\"slides\": [{\"body\": \"用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。\", \"meta\": \"WELCOME 01\", \"label\": \"校园入口与主楼\", \"title\": \"学校形象\", \"visual\": \"gate\", \"imageUrl\": \"\"}, {\"body\": \"观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。\", \"meta\": \"WELCOME 02\", \"label\": \"扫码内容导览\", \"title\": \"成果导览\", \"visual\": \"library\", \"imageUrl\": \"\"}, {\"body\": \"自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。\", \"meta\": \"WELCOME 03\", \"label\": \"现场节奏\", \"title\": \"现场节奏\", \"visual\": \"students\", \"imageUrl\": \"\"}], \"accent2\": \"#47b7ff\", \"scanCopy\": \"大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。\", \"sideCopy\": \"\", \"badgeText\": \"欢迎到校\", \"scanTitle\": \"扫描展项二维码\", \"sideTitle\": \"\", \"brandColor\": \"#28539c\", \"schoolMeta\": \"欢迎来到校园 · 同心特色校园文化\", \"schoolName\": \"毕节职业技术学院\", \"summaryCopy\": \"新版欢迎页采用舞台式首屏：左侧大图沉浸、右侧轮播导览、顶部显示实时通道状态，更适合展会现场远距离观看。\", \"summaryTags\": [\"远距可读\", \"实时扫码\", \"项目部署\"], \"logoImageUrl\": \"\", \"qualityRules\": {\"minBodyChars\": 80, \"requireMedia\": true, \"requireModule\": true, \"requireSummary\": true, \"requireTypeAssets\": true}, \"scanImageUrl\": \"\", \"summaryLabel\": \"WELCOME OVERVIEW\", \"summaryTitle\": \"从学校形象到展项内容，形成完整参观动线。\", \"brandDeepColor\": \"#20468b\", \"portalHomeCopy\": \"以专题门户为主线，串联专业建设、实训基地、产教融合、教学成果与专题资源。\", \"portalHomeTitle\": \"学校门户\", \"portalHomeFooter\": \"触摸卡片进入二级页面 · 长按返回首页\", \"portalHomeKicker\": \"School Portal\", \"moduleQualityRules\": {}, \"portalHomeCardChips\": [], \"portalHomeCardLabel\": \"创新育人专题\", \"portalHomeCardHidden\": false, \"portalHomeCardSummary\": \"\", \"portalHomeRouteLabels\": [\"学校门户\", \"专题门户\", \"板块资料\", \"专题展区\"], \"portalHomeSectionCopy\": \"以专题牵引院系共建，集中呈现跨系专业群、实训资源、产教融合与文化成果。\", \"portalHomeSectionTitle\": \"创新育人矩阵\", \"portalHomeCardSortOrder\": 0, \"portalHomeSectionKicker\": \"Integrated Showcase\"}',0,0,'','','admin','approved',NULL,'2026-08-11T10:15:57.019877+00:00'),(13,'智能制造','topic','smart-manufacturing','专题门户','智能制造','智能装备、新能源汽车与无人机应用。','Welcome','欢迎参观 {title}','即将进入展示页面','/uploads/blueprint/topics/smart-manufacturing/images/img01.webp','#f59a13','{\"slides\": [{\"body\": \"用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。\", \"meta\": \"WELCOME 01\", \"label\": \"校园入口与主楼\", \"title\": \"学校形象\", \"visual\": \"gate\", \"imageUrl\": \"\"}, {\"body\": \"观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。\", \"meta\": \"WELCOME 02\", \"label\": \"扫码内容导览\", \"title\": \"成果导览\", \"visual\": \"library\", \"imageUrl\": \"\"}, {\"body\": \"自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。\", \"meta\": \"WELCOME 03\", \"label\": \"现场节奏\", \"title\": \"现场节奏\", \"visual\": \"students\", \"imageUrl\": \"\"}], \"accent2\": \"#47b7ff\", \"scanCopy\": \"大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。\", \"sideCopy\": \"\", \"badgeText\": \"欢迎到校\", \"scanTitle\": \"扫描展项二维码\", \"sideTitle\": \"\", \"brandColor\": \"#28539c\", \"schoolMeta\": \"欢迎来到校园 · 同心特色校园文化\", \"schoolName\": \"毕节职业技术学院\", \"summaryCopy\": \"新版欢迎页采用舞台式首屏：左侧大图沉浸、右侧轮播导览、顶部显示实时通道状态，更适合展会现场远距离观看。\", \"summaryTags\": [\"远距可读\", \"实时扫码\", \"项目部署\"], \"logoImageUrl\": \"\", \"qualityRules\": {\"minBodyChars\": 80, \"requireMedia\": true, \"requireModule\": true, \"requireSummary\": true, \"requireTypeAssets\": true}, \"scanImageUrl\": \"\", \"summaryLabel\": \"WELCOME OVERVIEW\", \"summaryTitle\": \"从学校形象到展项内容，形成完整参观动线。\", \"brandDeepColor\": \"#20468b\", \"portalHomeCopy\": \"以专题门户为主线，串联专业建设、实训基地、产教融合、教学成果与专题资源。\", \"portalHomeTitle\": \"学校门户\", \"portalHomeFooter\": \"触摸卡片进入二级页面 · 长按返回首页\", \"portalHomeKicker\": \"School Portal\", \"moduleQualityRules\": {}, \"portalHomeCardChips\": [], \"portalHomeCardLabel\": \"创新育人专题\", \"portalHomeCardHidden\": false, \"portalHomeCardSummary\": \"\", \"portalHomeRouteLabels\": [\"学校门户\", \"专题门户\", \"板块资料\", \"专题展区\"], \"portalHomeSectionCopy\": \"以专题牵引院系共建，集中呈现跨系专业群、实训资源、产教融合与文化成果。\", \"portalHomeSectionTitle\": \"创新育人矩阵\", \"portalHomeCardSortOrder\": 0, \"portalHomeSectionKicker\": \"Integrated Showcase\"}',0,0,'','','admin','approved',NULL,'2026-08-11T10:15:57.021428+00:00'),(14,'同心校园文化','topic','campus-culture','专题门户','同心校园文化','同心育人、校园文化、学生成长与服务地方。','Welcome','欢迎参观 {title}','即将进入展示页面','/uploads/4fcaa6e34b5f40c7a7e2b58947b9de1c.jpg','#f59a13','{\"slides\": [{\"body\": \"用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。\", \"meta\": \"WELCOME 01\", \"label\": \"校园入口与主楼\", \"title\": \"学校形象\", \"visual\": \"gate\", \"imageUrl\": \"\"}, {\"body\": \"观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。\", \"meta\": \"WELCOME 02\", \"label\": \"扫码内容导览\", \"title\": \"成果导览\", \"visual\": \"library\", \"imageUrl\": \"\"}, {\"body\": \"自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。\", \"meta\": \"WELCOME 03\", \"label\": \"现场节奏\", \"title\": \"现场节奏\", \"visual\": \"students\", \"imageUrl\": \"\"}], \"accent2\": \"#47b7ff\", \"scanCopy\": \"大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。\", \"sideCopy\": \"\", \"badgeText\": \"欢迎到校\", \"scanTitle\": \"扫描展项二维码\", \"sideTitle\": \"\", \"brandColor\": \"#28539c\", \"schoolMeta\": \"欢迎来到校园 · 同心特色校园文化\", \"schoolName\": \"毕节职业技术学院\", \"summaryCopy\": \"新版欢迎页采用舞台式首屏：左侧大图沉浸、右侧轮播导览、顶部显示实时通道状态，更适合展会现场远距离观看。\", \"summaryTags\": [\"远距可读\", \"实时扫码\", \"项目部署\"], \"logoImageUrl\": \"\", \"qualityRules\": {\"minBodyChars\": 80, \"requireMedia\": true, \"requireModule\": true, \"requireSummary\": true, \"requireTypeAssets\": true}, \"scanImageUrl\": \"\", \"summaryLabel\": \"WELCOME OVERVIEW\", \"summaryTitle\": \"从学校形象到展项内容，形成完整参观动线。\", \"brandDeepColor\": \"#20468b\", \"portalHomeCopy\": \"以专题门户为主线，串联专业建设、实训基地、产教融合、教学成果与专题资源。\", \"portalHomeTitle\": \"学校门户\", \"portalHomeFooter\": \"触摸卡片进入二级页面 · 长按返回首页\", \"portalHomeKicker\": \"School Portal\", \"moduleQualityRules\": {}, \"portalHomeCardChips\": [], \"portalHomeCardLabel\": \"创新育人专题\", \"portalHomeCardHidden\": false, \"portalHomeCardSummary\": \"\", \"portalHomeRouteLabels\": [\"学校门户\", \"专题门户\", \"板块资料\", \"专题展区\"], \"portalHomeSectionCopy\": \"以专题牵引院系共建，集中呈现跨系专业群、实训资源、产教融合与文化成果。\", \"portalHomeSectionTitle\": \"创新育人矩阵\", \"portalHomeCardSortOrder\": 0, \"portalHomeSectionKicker\": \"Integrated Showcase\"}',0,0,'','','admin','approved',NULL,'2026-08-11T10:15:57.026117+00:00');
/*!40000 ALTER TABLE `projects` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `scans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scans` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(160) NOT NULL,
  `raw_url` varchar(2048) NOT NULL,
  `project_id` bigint NOT NULL DEFAULT '0',
  `result` varchar(40) NOT NULL DEFAULT 'ok',
  `detail` text NOT NULL,
  `created_at` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_scans_created_at` (`created_at`),
  KEY `idx_scans_project` (`project_id`),
  KEY `idx_scans_code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `scans` WRITE;
/*!40000 ALTER TABLE `scans` DISABLE KEYS */;
INSERT INTO `scans` VALUES (1,'BJ-TEACHER','http://127.0.0.1:8000/display?project=1&code=BJ-TEACHER&source=achievement-market',1,'ok','','2026-08-11T09:54:55.593735+00:00'),(2,'BJ-GRAD','http://127.0.0.1:8000/display?project=1&code=BJ-GRAD&source=achievement-market',1,'ok','','2026-08-11T09:57:34.141026+00:00'),(3,'AM-STUDENT-20260811-396B0B','http://127.0.0.1:8000/display?project=1&code=AM-STUDENT-20260811-396B0B&source=achievement-market',1,'ok','','2026-08-11T10:10:57.076524+00:00'),(4,'AM-STUDENT-20260811-CD1E61','http://127.0.0.1:8000/display?project=1&code=AM-STUDENT-20260811-CD1E61&source=achievement-market',1,'ok','','2026-08-11T10:11:38.067510+00:00');
/*!40000 ALTER TABLE `scans` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `username` varchar(64) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `display_name` varchar(120) NOT NULL DEFAULT '',
  `role` varchar(32) NOT NULL DEFAULT 'teacher',
  `department` varchar(120) NOT NULL DEFAULT '',
  `enabled` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` varchar(40) NOT NULL,
  `updated_at` varchar(40) NOT NULL,
  PRIMARY KEY (`username`),
  KEY `idx_users_role_enabled` (`role`,`enabled`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('admin','pbkdf2_sha256$120000$2ee80431c25a8e5b6d6f57219bb1e674$4424eb2e32525258eedc1fca81a203a91fb3d0f8956182c706e6ff1e1726caa6','Administrator','admin','',1,'2026-08-11T08:48:42.745201+00:00','2026-08-11T10:09:40.799933+00:00');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

