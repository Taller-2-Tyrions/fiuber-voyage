-- */ Insert Travels Table */
INSERT INTO travels (user_id,creation_date,init_location,end_location,price,init_time,end_time,active,driver_id,score,comment)
values
(1,now(),'-34.60787228308041, -58.37030622765176','-34.616841258491085, -58.368443516730245',1,now(),current_timestamp + (10 * interval '1 minute'),false,9001,5,NULL)
