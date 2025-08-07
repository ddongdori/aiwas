# 파일명: backend/log_generator.py
import threading
import time
import random
from datetime import datetime
from .config import LOG_FILE, LOG_GENERATION_INTERVAL
from .db_manager import db_manager

class LogGenerator:
    def __init__(self):
        self.log_file = LOG_FILE
        self.db = db_manager
        self.generating = False
        self.generator_thread = None
        
        # 샘플 에러 메시지 (더 상세하고 현실적인 에러 메시지)
        self.sample_errors = [
            {
                'level': 'ERROR',
                'messages': [
                    'java.lang.OutOfMemoryError: Java heap space\n\tat com.example.service.UserService.loadUsers(UserService.java:45)\n\tat com.example.controller.UserController.getAllUsers(UserController.java:28)\n\tat org.springframework.web.method.support.InvocableHandlerMethod.invoke(InvocableHandlerMethod.java:219)\n\tCaused by: java.util.concurrent.TimeoutException: Pool timeout after 30000ms',
                    'java.sql.SQLException: Communications link failure\n\tThe last packet sent successfully to the server was 0 milliseconds ago.\n\tThe driver has not received any packets from the server.\n\tat com.mysql.cj.jdbc.exceptions.SQLError.createCommunicationsException(SQLError.java:174)\n\tat com.example.repository.ProductRepository.findById(ProductRepository.java:67)',
                    'org.springframework.web.client.ResourceAccessException: I/O error on POST request for "http://api.external-service.com/data"\n\tNested exception is java.net.ConnectException: Connection refused (Connection refused)\n\tat org.springframework.web.client.RestTemplate.doExecute(RestTemplate.java:747)\n\tat com.example.service.ExternalApiService.sendData(ExternalApiService.java:89)',
                    'java.lang.NullPointerException: Cannot invoke "User.getName()" because "user" is null\n\tat com.example.controller.ProductController.getProduct(ProductController.java:156)\n\tat com.example.controller.ProductController$FastClassBySpringCGLIB$12345.invoke(<generated>)\n\tat org.springframework.cglib.proxy.MethodProxy.invoke(MethodProxy.java:218)',
                    'org.hibernate.exception.ConstraintViolationException: could not execute statement\n\tSQL: INSERT INTO user_orders (user_id, product_id, quantity) VALUES (?, ?, ?)\n\tConstraint: FK_USER_ORDER_USER_ID\n\tat org.hibernate.exception.internal.SQLStateConversionDelegate.convert(SQLStateConversionDelegate.java:112)\n\tat com.example.service.OrderService.createOrder(OrderService.java:78)',
                    'java.util.concurrent.TimeoutException: Request timeout after 5000ms\n\tat com.example.util.HttpClientUtil.executeRequest(HttpClientUtil.java:234)\n\tat com.example.service.PaymentService.processPayment(PaymentService.java:45)\n\tURL: https://payment-gateway.example.com/api/v1/charge\n\tRequest ID: req_1234567890abcdef',
                    'org.springframework.security.access.AccessDeniedException: Access is denied\n\tUser: guest_user (IP: 192.168.1.100)\n\tAttempted action: DELETE /api/admin/users/123\n\tRequired authority: ROLE_ADMIN\n\tat org.springframework.security.access.vote.AffirmativeBased.decide(AffirmativeBased.java:84)'
                ]
            },
            {
                'level': 'FATAL',
                'messages': [
                    'FATAL: Database connection pool exhausted - no available connections\n\tPool size: 20, Active: 20, Idle: 0\n\tWaiting threads: 47\n\tLast successful connection: 2024-01-15 14:32:18\n\tConfiguration: maxPoolSize=20, connectionTimeout=30000ms\n\tRecommendation: Increase pool size or check for connection leaks',
                    'FATAL: Critical system error - application shutdown initiated\n\tReason: Unrecoverable JVM error detected\n\tError: java.lang.InternalError: a fault occurred in a recent unsafe memory access operation\n\tHeap usage: 98% of 8GB allocated\n\tGC overhead limit exceeded - stopping all user threads',
                    'FATAL: Security breach detected - unauthorized access attempt\n\tSource IP: 203.0.113.42 (Russia)\n\tAttempted endpoint: /api/admin/system/shutdown\n\tAuthentication: Failed (invalid JWT token)\n\tUser-Agent: curl/7.68.0\n\tAction taken: IP blocked, incident logged to security team'
                ]
            },
            {
                'level': 'Exception',
                'messages': [
                    'IllegalArgumentException: Invalid user ID provided\n\tProvided value: "abc123" (expected numeric ID)\n\tat com.example.validator.UserValidator.validateUserId(UserValidator.java:23)\n\tat com.example.service.UserService.getUserById(UserService.java:67)\n\tRequest URL: GET /api/users/abc123\n\tClient IP: 10.0.0.15',
                    'ConcurrentModificationException in thread pool executor\n\tThread: pool-1-thread-8\n\tTask: com.example.task.DataProcessingTask\n\tat java.util.ArrayList$Itr.checkForComodification(ArrayList.java:909)\n\tat com.example.service.DataProcessor.processItems(DataProcessor.java:145)\n\tConcurrent access detected on shared collection',
                    'FileNotFoundException: Configuration file not found\n\tFile: /opt/tomcat/conf/application-prod.properties\n\tWorking directory: /opt/tomcat/bin\n\tat java.io.FileInputStream.open0(Native Method)\n\tat com.example.config.ConfigLoader.loadProperties(ConfigLoader.java:89)\n\tFallback: Using default configuration',
                    'ClassCastException: com.example.dto.UserDTO cannot be cast to com.example.entity.User\n\tat com.example.service.UserService.processUser(UserService.java:234)\n\tat com.example.controller.UserController.updateUser(UserController.java:78)\n\tSerialization error detected in user data mapping'
                ]
            }
        ]
    
    def start_generating(self):
        """샘플 로그 생성 시작"""
        if not self.generating:
            self.generating = True
            self.generator_thread = threading.Thread(target=self._generation_loop, daemon=True)
            self.generator_thread.start()
            print("샘플 로그 생성 시작")
    
    def stop_generating(self):
        """샘플 로그 생성 중지"""
        self.generating = False
        if self.generator_thread:
            self.generator_thread.join(timeout=1)
        print("샘플 로그 생성 중지")
    
    def _generation_loop(self):
        """주기적으로 샘플 로그 생성"""
        while self.generating:
            try:
                self._generate_random_error()
                time.sleep(LOG_GENERATION_INTERVAL)
            except Exception as e:
                print(f"로그 생성 오류: {e}")
                time.sleep(1)
    
    def _generate_random_error(self):
        """랜덤 에러 로그 생성"""
        try:
            # 랜덤 에러 타입 선택
            error_type = random.choice(self.sample_errors)
            level = error_type['level']
            message = random.choice(error_type['messages'])
            
            # 랜덤 응답시간 생성 (100ms ~ 5000ms)
            response_time = random.randint(100, 5000)
            
            # 현재 시간을 정확히 사용
            current_time = datetime.now()
            timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 밀리초까지
            
            # 로그 포맷 생성 (현재 시간 사용)
            log_line = f"[{timestamp}] {level}: {message} [{response_time}ms]"
            
            # 파일에 기록
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
                f.flush()
            
            # DB에 직접 저장 (현재 시간으로 저장)
            self.db.insert_log(
                level=level,
                message=message,
                response_time=response_time
            )
            
            print(f"[{current_time.strftime('%H:%M:%S')}] 샘플 로그 생성: {level} - {message[:50]}...")
            
        except Exception as e:
            print(f"로그 생성 중 오류: {e}")

# 전역 인스턴스
log_generator = LogGenerator()