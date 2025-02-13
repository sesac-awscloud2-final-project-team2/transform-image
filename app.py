'''
데이터 송수신을 확인하기 위한 api (develop)
'''

from flask import Flask, request, jsonify
from transform_data.join_to_rdb import insert_join_user
from transform_data.trip_to_rds import insert_trip_log
from transform_data.experience_to_rds import insert_exp_info

app = Flask(__name__)

@app.route('/join', methods=['POST'])
def join():
    user_info = request.json
    try:
        rds_save_result = insert_join_user(user_info)
        return jsonify({"message": "User data saved successfully in RDB", "user": rds_save_result}), 201
    
    except Exception as e:
        return jsonify({"message": "User data save failed in RDB", "error": str(e)}), 500

@app.route('/trip', methods=['POST'])
def trip():
    trip_info = request.json
    try:
        rds_save_result = insert_trip_log(trip_info)
        return jsonify({"message": "Trip data saved successfully in RDB", "trip": rds_save_result}), 201
    
    except Exception as e:
        return jsonify({"message": "Trip data save failed in RDB", "error": str(e)}), 500

@app.route('/experience', methods=['POST'])
def experience():
    experience_info = request.json
    
    try:
        rds_save_result = insert_exp_info(experience_info)
        return jsonify({"message": "Experience data save successfully in RDB", "exp": rds_save_result}), 201
    
    except Exception as e:
        return jsonify({"message": "Experience data save failed in RDB", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=30002)
