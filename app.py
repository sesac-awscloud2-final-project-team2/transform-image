from flask import Flask, request, jsonify
import psycopg2
import hashlib
import os

import json
import boto3
from rds import get_rds_info, get_rds_secret

app = Flask(__name__)

# PostgreSQL 연결 정보
#DB_HOST = "35.216.105.120"
#DB_HOST = "localhost"
#DB_HOST = "test.cvckq4e8iqnx.ap-northeast-2.rds.amazonaws.com"
#DB_HOST = "10.178.0.7"
#DB_NAME = "testdb"
#DB_USER = "postgres"
#DB_PASSWORD = "Test1234!"

secrets = get_rds_secret()
db_info = get_rds_info()

DB_HOST = db_info['db_host']
DB_NAME = db_info['db_name']
DB_PORT = db_info['port']
DB_USER = secrets['username']
DB_PASSWORD = secrets['password']
TRANSFORM_PORT = 30002

# 비밀번호 해싱 함수
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# PostgreSQL 연결 함수
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# 사용자 등록 엔드포인트
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 444

    hashed_password = hash_password(password)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (%s, %s)
        """, (username, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "User registered successfully"}), 201
    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

# 서버 실행
if __name__ == '__main__':
   # app.run(debug=True)
   app.run(host='0.0.0.0', port=TRANSFORM_PORT, debug=True)
