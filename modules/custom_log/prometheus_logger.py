from prometheus_client import Counter, Histogram, CollectorRegistry
import time

class PrometheusLogger:
    def __init__(self, job_name):
        self.job_name = job_name

        self.registry = CollectorRegistry()

        # 메트릭 정의
        self.function_calls = Counter('function_calls_total', 'Number of function calls', 
                                      ['function_name'], registry=self.registry)
        self.function_duration = Histogram('function_duration_seconds', 'Duration of function calls',
                                           ['function_name'], registry=self.registry)
        self.boto_calls = Counter('api_calls_total', 'Number of API calls', 
                                 ['func_name', 'aws_service', 'status'], registry=self.registry)
        self.boto_latency = Histogram('api_latency_seconds', 'Latency of API calls',
                                     ['func_name', 'aws_service'], registry=self.registry)
        self.db_operations = Counter('db_operations_total', 'Number of database operations',
                                     ['operation', 'database'], registry=self.registry)
        self.db_operation_duration = Histogram('db_operation_duration_seconds', 'Duration of database operations',
                                               ['operation', 'database'], registry=self.registry)
        self.data_processed = Counter('data_processed_total', 'Amount of data processed',
                                      ['data_type'], registry=self.registry)
        self.errors = Counter('errors_total', 'Number of errors', 
                              ['function_name'], registry=self.registry)
        self.warnings = Counter('warnings_total', 'Number of warnings', 
                                ['function_name'], registry=self.registry)

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

    def boto_call(self, func_name, aws_service, status_code, response_time):
        self.boto_calls.labels(func_name=func_name, aws_service=aws_service, status=status_code).inc()
        self.boto_latency.labels(func_name=func_name, aws_service=aws_service).observe(response_time)

    def db_operation(self, operation, database, duration):
        self.db_operations.labels(operation=operation, database=database).inc()
        self.db_operation_duration.labels(operation=operation, database=database).observe(duration)

    def data_processing(self, data_type, count):
        self.data_processed.labels(data_type=data_type).inc(count)

    def error(self, function_name):
        self.errors.labels(function_name=function_name).inc()

    def warning(self, function_name):
        self.warnings.labels(function_name=function_name).inc()
