use TOBACCO
if not exists(select * from sys.database_principals where name = 'developer')
CREATE USER developer WITH password = 'CapstonePotato!'

ALTER ROLE db_datawriter ADD MEMBER developer
ALTER ROLE db_datareader ADD MEMBER developer
ALTER ROLE db_ddladmin ADD MEMBER developer
ALTER ROLE bulkadmin ADD MEMBER developer