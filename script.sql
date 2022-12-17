
DROP TABLE IF EXISTS p2p;

USE p2p;

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `username` varchar(100) NOT NULL,
  `password` varchar(50) NOT NULL,
  `conn_ip` varchar(20) DEFAULT NULL,
  `conn_port` varchar(22) DEFAULT NULL,
  PRIMARY KEY (`username`)
);

DROP TABLE IF EXISTS `friend_list`;
CREATE TABLE `friend_list` (
  `username` varchar(255) NOT NULL,
  `user_friend` varchar(255) NOT NULL,
  PRIMARY KEY (`username`,`user_friend`),
  KEY `FK_friend` (`user_friend`),
  CONSTRAINT `FK_friend` FOREIGN KEY (`user_friend`) REFERENCES `user` (`username`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_user` FOREIGN KEY (`username`) REFERENCES `user` (`username`) ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO `user` VALUES ('a','123','192.168.1.10','65528'),('admi','123',NULL,NULL),('b','123','192.168.1.10','65526'),('c','123','192.168.1.10','64533'),('d','123','192.168.1.10','49397');