import logging
from datetime import datetime

class CustomLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # 콘솔 핸들러 설정
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 포맷터 설정
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        # 핸들러 추가
        self.logger.addHandler(ch)

    def start(self, function_name):
        self.logger.info(f"Function {function_name} started")
        return datetime.now()

    def finish(self, function_name):
        self.logger.info(f"Function {function_name} finished")

    def api_call(self, endpoint, method, status_code, response_time):
        self.logger.info(f"API Call: {method} {endpoint} - Status: {status_code} - Response Time: {response_time}ms")

    def dynamodb_operation(self, operation, table, items_affected, start_time):
        duration = datetime.now() - start_time
        self.logger.info(f"DynamoDB: {operation} on {table} - Items affected: {items_affected} - Duration: {duration}ms")

    def rds_operation(self, operation, database, items_affected, start_time):
        duration = datetime.now() - start_time
        self.logger.info(f"RDS: {operation} on {database} - Items affected: {items_affected} - Duration: {duration}ms")
        
    def data_processing(self, data_type, count, start_time):
        duration = datetime.now() - start_time
        self.logger.info(f"Data Processing: {data_type} - Count: {count} - Duration: {duration}ms")

    def error(self, message, exc_info=True):
        self.logger.error(message, exc_info=exc_info)

    def warning(self, message):
        self.logger.warning(message)

    def debug(self, message):
        self.logger.debug(message)


