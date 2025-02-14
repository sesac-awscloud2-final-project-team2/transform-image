import logging
from datetime import datetime
import os
import json
from logging.handlers import RotatingFileHandler
import time

class CustomLogger:
    def __init__(self, name, log_dir='logs'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # 로그 디렉토리 생성
        # if not os.path.exists(log_dir):
        #     os.makedirs(log_dir)

        # 콘솔 핸들러 설정
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(console_formatter)

        # # 파일 핸들러 설정 (RotatingFileHandler 사용)
        # log_file = os.path.join(log_dir, f'{name}.log')
        # fh = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
        # fh.setLevel(logging.DEBUG)
        # file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # fh.setFormatter(file_formatter)

        # 핸들러 추가
        self.logger.addHandler(ch)
        # self.logger.addHandler(fh)

    def _log_with_context(self, level, func_name, message, extra=None):
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "function": func_name,
            "message": message
        }
        if extra:
            log_data.update(extra)
        
        log_message = json.dumps(log_data)
        getattr(self.logger, level)(log_message)

    class FunctionTimer:
        def __init__(self, logger, func_name):
            self.logger = logger
            self.func_name = func_name
            self.start_time = None

        def __enter__(self):
            self.start_time = time.time()
            self.logger._log_with_context("info", self.func_name, "Function started")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            if exc_type:
                self.logger._log_with_context("error", self.func_name, f"Function failed: {exc_val}", {"duration": duration})
            else:
                self.logger._log_with_context("info", self.func_name, "Function finished", {"duration": duration})

    def time_function(self, func_name):
        return self.FunctionTimer(self, func_name)

    def boto_call(self, func_name, aws_service, status_code, response_time):
        self._log_with_context("info", func_name, "API Call", {
            "aws_service": aws_service,
            "status_code": status_code,
            "response_time_ms": response_time
        })

    def dynamodb_operation(self, func_name, operation, table, items_affected, start_time):
        duration = time.time() - start_time
        self._log_with_context("info", func_name, "DynamoDB Operation", {
            "operation": operation,
            "table": table,
            "items_affected": items_affected,
            "duration_ms": duration * 1000
        })

    def rds_operation(self, func_name, operation, database, items_affected, start_time):
        duration = time.time() - start_time
        self._log_with_context("info", func_name, "RDS Operation", {
            "operation": operation,
            "database": database,
            "items_affected": items_affected,
            "duration_ms": duration * 1000
        })
        
    def data_processing(self, func_name, data_type, count, start_time):
        duration = time.time() - start_time
        self._log_with_context("info", func_name, "Data Processing", {
            "data_type": data_type,
            "count": count,
            "duration_ms": duration * 1000
        })

    def error(self, func_name, message, exc_info=True):
        self._log_with_context("error", func_name, message, {"exc_info": exc_info})

    def warning(self, func_name, message):
        self._log_with_context("warning", func_name, message)

    def debug(self, func_name, message):
        self._log_with_context("debug", func_name, message)

if __name__ == "__main__":
    logger = CustomLogger("my_app")

    with logger.time_function("my_function"):
        # 함수 로직
        pass

    logger.api_call("my_function", "/api/data", "GET", 200, 100)
    logger.error("my_function", "An error occurred")
