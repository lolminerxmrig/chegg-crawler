CREATE DATABASE `chegg`;

CREATE TABLE `day` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `sub_category_id` bigint DEFAULT NULL,
  `day_number` int DEFAULT NULL,
  `month` varchar(45) DEFAULT NULL,
  `year` varchar(45) DEFAULT NULL,
  `url` varchar(1000) DEFAULT NULL,
  `is_crawled` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`)
)





CREATE TABLE `main_category` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `url` varchar(1000) DEFAULT NULL,
  `is_crawled` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`)
)




CREATE TABLE `question` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `url` varchar(2000) DEFAULT NULL,
  `day_id` bigint DEFAULT NULL,
  `question` mediumtext,
  `answer_html` longtext,
  `is_processed` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`)
)




CREATE TABLE `sub_category` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `main_category_id` bigint DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `url` varchar(1000) DEFAULT NULL,
  `is_crawled` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`)
)


