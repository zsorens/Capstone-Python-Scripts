USE TOBACCO
--
DROP VIEW IF EXISTS v_active;

CREATE VIEW [v_active] AS(
SELECT  status, REPLACE((CAST(street_num as varchar) + ' ' + street_dir  +' '+ street_name+ ' ' +street_type), '  ', ' ')  'combined_address'
, zipcode  FROM raw_permit 
WHERE status = 'Active')

--SELECT * from [v_active]