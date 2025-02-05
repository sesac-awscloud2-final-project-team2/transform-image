from utils import load_json

DB_ID = 'travelog-public-db'
DB_SECRET_NAME = 'rds!db-a35d4553-2fa4-463c-90d0-309ed70330bc'

USER_COLS = load_json('db-table-columns/users.json')
TRIP_COLS = load_json('db-table-columns/travel.json')
PLACE_COLS = load_json('db-table-columns/travel_places.json')
PHOTO_COLS = load_json('db-table-columns/travel_photos.json')
EXP_COLS = load_json('db-table-columns/travel_experiences.json')