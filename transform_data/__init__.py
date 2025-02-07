from transform_data.join_to_rdb import insert_join_user
from transform_data.trip_to_rds import insert_trip_log
from transform_data.experience_to_rds import insert_exp_info

func_pair = {
    'user' : insert_join_user,
    'trip' : insert_trip_log,
    'experience' : insert_exp_info    
    }

def load_insert_function(table_name):
    return func_pair[table_name]