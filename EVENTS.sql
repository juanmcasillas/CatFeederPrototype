BEGIN TRANSACTION;
CREATE TABLE "EVENTS" (
	`ID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`START`	INTEGER NOT NULL,
	`END`	INTEGER DEFAULT 0,
	`PETID`	INTEGER NOT NULL,
	`ALLOWED`	INTEGER NOT NULL DEFAULT 0,
	`RULE`	INTEGER NOT NULL,
	FOREIGN KEY(`PETID`) REFERENCES `PETS`,
	FOREIGN KEY(`RULE`) REFERENCES `RULES`
);
INSERT INTO `EVENTS` VALUES (18,'2017-09-10 20:21:22','2017-09-10 20:25:23',1,1,1);
INSERT INTO `EVENTS` VALUES (19,'2017-09-10 21:21:22','2017-09-10 21:26:23',1,1,1);
INSERT INTO `EVENTS` VALUES (20,'2017-09-10 22:22:22','2017-09-10 22:30:23',1,1,1);
INSERT INTO `EVENTS` VALUES (21,'2017-10-10 10:21:22','2017-10-10 10:36:23',2,1,1);
INSERT INTO `EVENTS` VALUES (22,'2017-10-10 11:21:22','2017-10-10 11:36:21',2,1,1);
INSERT INTO `EVENTS` VALUES (23,'2017-10-10 12:22:22','2017-10-10 12:37:23',2,1,1);
INSERT INTO `EVENTS` VALUES (24,'2017-10-10 14:22:22','2017-10-10 24:40:40',2,1,1);
INSERT INTO `EVENTS` VALUES (25,'2017-11-10 10:21:22','2017-11-10 10:21:40',1,0,1);
INSERT INTO `EVENTS` VALUES (26,'2017-11-10 11:21:22','2017-11-10 11:21:40',1,0,1);
INSERT INTO `EVENTS` VALUES (27,'2017-11-10 12:22:22','2017-11-10 12:22:40',1,0,1);
INSERT INTO `EVENTS` VALUES (28,'2017-11-10 14:22:22','2017-11-10 24:22:40',1,0,1);
COMMIT;