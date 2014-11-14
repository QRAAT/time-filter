#!/bin/bash
mysql -u root -p --local-infile -e "USE qraat; DELETE FROM est; LOAD DATA LOCAL INFILE 'est.txt' INTO TABLE est IGNORE 1 LINES; UPDATE processing_cursor SET value = 0"
