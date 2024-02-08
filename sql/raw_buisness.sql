USE TOBACCO;

DROP TABLE IF EXISTS [raw_buisness];

CREATE TABLE [raw_buisness](
id int primary key,
name varchar(256),
address1 varchar(128),
address2 varchar(128),
unit_type varchar(128),
unit varchar(32),
city varchar(32),
state char(2),
zipcode char(10),
phone char(14),
nature varchar(256)

)

