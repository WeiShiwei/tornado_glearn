PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
	id INTEGER NOT NULL, 
	name VARCHAR(255),  
	email_addr VARCHAR(255),  
	created_date DATETIME, 
	modified_date DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO "users" VALUES(1,'gldjc','weishiwei920@163.com',NULL,NULL);
INSERT INTO "users" VALUES(2,'gldzb','tornado_classify@163.com',NULL,NULL);
COMMIT;

BEGIN TRANSACTION;
CREATE TABLE crf_stemmed (
  id INTEGER NOT NULL,
  word VARCHAR(255), 
  stem VARCHAR(255), 
  created_at DATETIME,
  updated_at DATETIME,
  PRIMARY KEY (id)
);
INSERT INTO "crf_stemmed" VALUES (0, 'φ', 'Φ', '2014-03-25 09:24:26.623033', '2014-03-25 09:24:26.623033');
INSERT INTO "crf_stemmed" VALUES (1, 'Ф', 'Φ', '2014-03-25 09:24:26.623033', '2014-03-25 09:24:26.623033');
INSERT INTO "crf_stemmed" VALUES (2, 'III', 'Ⅲ', '2014-03-25 09:24:26.623033', '2014-03-25 09:24:26.623033');
INSERT INTO "crf_stemmed" VALUES (5, '×', '*', '2015-01-05 09:24:26.623033', '2015-01-05 09:24:26.623033');
COMMIT;


BEGIN TRANSACTION;
CREATE TABLE crf_pattern(
  id INTEGER NOT NULL,
  first_type_code VARCHAR(255),
  second_type_code VARCHAR(255),
  pattern VARCHAR(255),
  regrex VARCHAR(255),
  substitute VARCHAR(255),
  created_at DATETIME,
  updated_at DATETIME,
  PRIMARY KEY (id)
);
INSERT INTO "crf_pattern" VALUES (0, '25','11','<XS>*<BCJM>+<XS>*<BCJM>','(\d+)\*([\d\.]+)\+(\d+)\*([\d\.]+)','{"XS":"\1+\3","BCJM":"\2"}','2014-03-25 09:24:26.623033', '2014-03-25 09:24:26.623033');
INSERT INTO "crf_pattern" VALUES (1, '25','11','<XS>*<BCJM>+<XS>','(\d+)\*([\d\.]+)\+(\d+)','{"XS":"\1+\3","BCJM":"\2"}','2014-03-25 09:24:26.623033', '2014-03-25 09:24:26.623033');
INSERT INTO "crf_pattern" VALUES (2, '25','11','<BCJM>*(<XS>+<XS>)','([\d\.]+)\*\((\d+)\+(\d+)\)','{"XS":"\2+\3","BCJM":"\1"}','2014-03-25 09:24:26.623033', '2014-03-25 09:24:26.623033');
INSERT INTO "crf_pattern" VALUES (3, '25','11','(<XS>+<XS>)*<BCJM>','\((\d+)\+(\d+)\)\*([\d\.]+)','{"XS":"\1+\2","BCJM":"\3"}','2014-03-25 09:24:26.623033', '2014-03-25 09:24:26.623033');
COMMIT;

-- BEGIN TRANSACTION;
-- CREATE TABLE crf_compositive_attribute(
--   id INTEGER NOT NULL,
--   first_type_code VARCHAR(255),
--   second_type_code VARCHAR(255),
--   compositive_attribute VARCHAR(255),
--   created_at DATETIME,
--   updated_at DATETIME,
--   PRIMARY KEY (id)
-- );
-- INSERT INTO "crf_pattern" VALUES (0, '25','11','<XS>*<BCJM>+<XS>*<BCJM>','(\d+)\*([\d\.]+)\+(\d+)\*([\d\.]+)','{"XS":"\1+\3","BCJM":"\2"}','2014-03-25 09:24:26.623033', '2014-03-25 09:24:26.623033');
-- INSERT INTO "crf_pattern" VALUES (1, '25','11','<XS>*<BCJM>+<XS>','(\d+)\*([\d\.]+)\+(\d+)','{"XS":"\1+\3","BCJM":"\2"}','2014-03-25 09:24:26.623033', '2014-03-25 09:24:26.623033');
-- INSERT INTO "crf_pattern" VALUES (2, '25','11','<BCJM>*(<XS>+<XS>)','([\d\.]+)\*\((\d+)\+(\d+)\)','{"XS":"\2+\3","BCJM":"\1"}','2014-03-25 09:24:26.623033', '2014-03-25 09:24:26.623033');
-- INSERT INTO "crf_pattern" VALUES (3, '25','11','(<XS>+<XS>)*<BCJM>','\((\d+)\+(\d+)\)\*([\d\.]+)','{"XS":"\1+\2","BCJM":"\3"}','2014-03-25 09:24:26.623033', '2014-03-25 09:24:26.623033');
-- COMMIT;