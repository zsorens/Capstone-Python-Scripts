USE TOBACCO;

DROP TABLE IF EXISTS [raw_permit];

CREATE TABLE [raw_permit](
id int IDENTITY(1,1) primary key,
status varchar(16),
name varchar(64),
record_type varchar(64),
assigned_staff varchar(128),
assigned_date date,
record_number varchar(32),
unit varchar(16),
start_fraction char(3),
zipcode char(5),
closed_date date,
street_num int,
street_dir varchar(2), --direction
street_type varchar(4), -- lile lane (LN) OR Road (RD)
street_name varchar(64),
notes varchar(256),
opened_date date,
)

-- note on import, one zip code at 40228 did not worrk, said it was a truncate error