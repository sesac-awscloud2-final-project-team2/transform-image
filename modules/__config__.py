from modules.utils import load_json, get_secret

secrets = get_secret()
DB_ID = secrets['DB_ID']
DB_SECRET_NAME = secrets['DB_SECRET_NAME']

PLACE_COLS = load_json('json/db-table-columns/travel_places.json')
PHOTO_COLS = load_json('json/db-table-columns/travel_photos.json')
EXP_COLS = load_json('json/db-table-columns/travel_experiences.json')

USER_COLS = load_json('json/db-table-columns/users.json')

TRIP_COLS = load_json('json/db-table-columns/travel.json')
