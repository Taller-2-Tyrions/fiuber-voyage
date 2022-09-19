-- */ Create Travels Table */
BEGIN;

CREATE TABLE IF NOT EXISTS travels(
	id serial NOT NULL,
	user_id int NOT NULL,
	creation_date timestamp NOT NULL,
	init_location varchar(64) NOT NULL,
	end_location varchar(64) NOT NULL,
	price int NOT NULL,
	init_time timestamp NOT NULL,
	end_time timestamp NOT NULL,
	active boolean NOT NULL,
	driver_id int NOT NULL,
	score int NULL,
	comment varchar(255) NULL,
	primary key(id)
);

COMMIT;
