USE TOBACCO

DROP TABLE IF EXISTS [stores];

CREATE TABLE [stores](
	place_id varchar(50) primary key,
	flag_text bit NOT NULL default 0,
	flag_image bit NOT NULL default 0, --remove this from UI 
	flag_website bit NOT NULL default 0,
	last_updated datetime NOT NULL default GETDATE(), -- used when we suesd to have meta data but thats illegl 
	last_flagged datetime,
	flag_street bit NOT NULL default 0,
	flag_review_image bit NOT NULL default 0,
	flag_review bit NOT NULL default 0
)
