USE `qraat;
INSERT INTO `project` VALUES (8,1,'Time filter','Evaluation of time filter based on \"how well it works.\"  These are for deploymentID=105 for a few hours on August 7. Run ``rmg_position --dep-id=105 --t-delta=5 --t-start=1407448826 --t-end=1407466793 --thresh=0.2``.',1,0);
INSERT INTO `tx` VALUES (115,'A transmitter','666',2,8,999.99,0);
INSERT INTO `target` VALUES (40,'Jim','A rat.',8,0,'exp',2,2,2);
INSERT INTO `deployment` VALUES (10000,'hyper','SCORE_ERROR = lambda(x) : (-0.6324 / (x + 7.7640)) + 0.1255',1416607939.000000,NULL,115,40,8,1,0),(10001,'none','No time filter.',1416607939.000000,NULL,115,40,8,1,0),(10002,'const_low','SCORE_ERROR = 0.02',1416607939.000000,NULL,115,40,8,1,0),(10003,'noband','Absolutely no filtering.',1416863368.000000,NULL,115,40,8,0,0),(10004,'const_high','SCORE_ERROR = 0.1255',1416863368.000000,NULL,115,40,8,1,0);
