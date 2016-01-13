DROP TABLE IF EXISTS 'weather';

CREATE TABLE 'weather'(
	game_id varchar(40 ), 
	location varchar(40 ),
	date date
	local_time varchar(10 ),
	temp varchar(10 ),
	heat_index varchar(10 ),
	dew_point varchar(10 ),
	humidity varchar(10 ),
	pressure varchar(10 ),
	visibility varchar(10 ),
	wind_dir varchar(10 ),
	wind_speed varchar(10 ),
	gust_speed varchar(10 ),
	precip varchar(10 ),
	events varchar(40 ),
	conditions varchar(40 )
 ) ENGINE=InnoDB;
