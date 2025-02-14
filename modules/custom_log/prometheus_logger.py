from prometheus_client import Counter, Histogram
import time

class PrometheusLogger:
    def __init__(self, job_name):
        self.job_name = job_name

        # 메트릭 정의
        self.function_calls = Counter('function_calls_t', 'Number of function calls', 
                                      ['function_name'])
        self.function_duration = Histogram('function_duration_seconds', 'Duration of function calls',
                                           ['function_name'])
        self.api_calls = Counter('api_calls_total', 'Number of API calls', 
                                 ['endpoint', 'method', 'status'])
        self.api_latency = Histogram('api_latency_seconds', 'Latency of API calls',
                                     ['endpoint', 'method'])
        self.db_operations = Counter('db_operations_total', 'Number of database operations',
                                     ['operation', 'database'])
        self.db_operation_duration = Histogram('db_operation_duration_seconds', 'Duration of database operations',
                                               ['operation', 'database'])
        self.data_processed = Counter('data_processed_total', 'Amount of data processed',
                                      ['data_type'])
        self.errors = Counter('errors_total', 'Number of errors', 
                              ['function_name'])
        self.warnings = Counter('warnings_total', 'Number of warnings', 
                                ['function_name'])

    class FunctionTimer:
        def __init__(self, logger, function_name):
            self.logger = logger
            self.function_name = function_name
            self.start_time = None

        def __enter__(self):
            self.start_time = time.time()
            self.logger.function_calls.labels(function_name=self.function_name).inc()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            self.logger.function_duration.labels(function_name=self.function_name).observe(duration)
            if exc_type is not None:
                self.logger.errors.labels(function_name=self.function_name).inc()

    def time_function(self, function_name):
        return self.FunctionTimer(self, function_name)

    def api_call(self, endpoint, method, status_code, response_time):
        self.api_calls.labels(endpoint=endpoint, method=method, status=status_code).inc()
        self.api_latency.labels(endpoint=endpoint, method=method).observe(response_time)

    def db_operation(self, operation, database, duration):
        self.db_operations.labels(operation=operation, database=database).inc()
        self.db_operation_duration.labels(operation=operation, database=database).observe(duration)

    def data_processing(self, data_type, count):
        self.data_processed.labels(data_type=data_type).inc(count)

    def error(self, function_name):
        self.errors.labels(function_name=function_name).inc()

    def warning(self, function_name):
        self.warnings.labels(function_name=function_name).inc()
