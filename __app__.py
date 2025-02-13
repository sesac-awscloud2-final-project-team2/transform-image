'''개발용 Flask app
데이터 송수신을 확인하기 위한 API
'''

from flask import Flask, request, jsonify
from modules.transform_to_rds import load_insert_function

app = Flask(__name__)

@app.route('/join', methods=['POST'])
def join():
    user_info = request.json
    try:
        insert_join_user = load_insert_function('user')
        rds_save_result = insert_join_user(user_info)
        return jsonify({"message": "User data saved successfully in RDB", "user": rds_save_result}), 201
    
    except Exception as e:
        return jsonify({"message": "User data save failed in RDB", "error": str(e)}), 500

@app.route('/trip', methods=['POST'])
def trip():
    trip_info = request.json
    try:
        insert_trip_log = load_insert_function('trip')
        rds_save_result = insert_trip_log(trip_info)
        return jsonify({"message": "Trip data saved successfully in RDB", "trip": rds_save_result}), 201
    
    except Exception as e:
        return jsonify({"message": "Trip data save failed in RDB", "error": str(e)}), 500

@app.route('/experience', methods=['POST'])
def experience():
    experience_info = request.json
    
    try:
        insert_exp_info = load_insert_function('experience')
        rds_save_result = insert_exp_info(experience_info)
        return jsonify({"message": "Experience data save successfully in RDB", "exp": rds_save_result}), 201
    
    except Exception as e:
        return jsonify({"message": "Experience data save failed in RDB", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=30002)
