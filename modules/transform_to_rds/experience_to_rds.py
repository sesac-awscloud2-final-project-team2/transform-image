'''
experience으로 저장된 experience 데이터를 불러와서 rdb로 저장
'''
import json
from modules.rds_manager import RDSManager

from modules.__config__ import DB_ID, DB_SECRET_NAME
from modules.__config__ import EXP_COLS, PLACE_COLS, PHOTO_COLS

from modules.utils import get_current_datetime

def insert_place_info(exp_dict):
    place_dict = exp_dict['place']
    table_name = 'travel_places'

    rds_manager = RDSManager(DB_ID, DB_SECRET_NAME, is_proxy=True)
    
    filter_col = 'place_name'
    with rds_manager:
        place_ids = rds_manager.select_filter(table_name, filter_col, place_dict[filter_col], 'place_id')
        if len(place_ids) > 0:
            return place_ids[0][0]
    
    with rds_manager:
        last_id = rds_manager.select_last_id('place_id', table_name)

    tag = 'p'
    if last_id == None:
        new_id = tag+'1'
    else:
        id_num = int(last_id[1:])
        new_id = f'{tag}{id_num+1}'
    place_dict['place_id'] = new_id
    place_dict['created_at'] = get_current_datetime()
    place_dict['user_id'] = exp_dict['user_id']

    with rds_manager:
        rds_manager.insert_data(PLACE_COLS, place_dict, table_name)

    return new_id

def insert_photo_info(exp_dict, place_id):
    photo_dict = exp_dict['photo']
    photo_dict['place_id'] = place_id
    table_name = 'travel_photos'

    rds_manager = RDSManager(DB_ID, DB_SECRET_NAME, is_proxy=True)

    filter_col = 'place_id'
    with rds_manager:
        places = rds_manager.select_filter('travel_places', filter_col, photo_dict[filter_col])
        if (len(places) == 0) and (len(place_id) != 0):
            return
    
    with rds_manager:
        last_id = rds_manager.select_last_id('photo_id', table_name)

    tag = 'o'
    if last_id == None:
        new_id = tag+'1'
    else:
        id_num = int(last_id[1:])
        new_id = f'{tag}{id_num+1}'
    photo_dict['photo_id'] = new_id
    photo_dict['created_at'] = get_current_datetime()
    photo_dict['user_id'] = exp_dict['user_id']

    with rds_manager:
        rds_manager.insert_data(PHOTO_COLS, photo_dict, table_name)

    return new_id


def insert_exp_info(exp_dict):
    place_id = insert_place_info(exp_dict)
    photo_id = insert_photo_info(exp_dict, place_id)

    table_name = 'travel_experiences'
    rds_manager = RDSManager(DB_ID, DB_SECRET_NAME, is_proxy=True)

    exp_dict['place_id'] = place_id
    exp_dict['photo_id'] = photo_id
    exp_dict['created_at'] = get_current_datetime()
    exp_dict['details'] = json.dumps(exp_dict['details'], ensure_ascii=False)

    with rds_manager:
        rds_manager.insert_data(EXP_COLS, exp_dict, table_name)
