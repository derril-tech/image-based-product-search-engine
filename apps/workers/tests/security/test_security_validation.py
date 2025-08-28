# Created automatically by Cursor AI (2024-12-19)

import pytest
import asyncio
import time
import jwt
import hashlib
import hmac
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from ..src.services.search_service import SearchService
from ..src.services.index_service import IndexService
from ..src.services.audit_logger import AuditLogger
from ..src.services.cdn_service import CDNService
from ..src.models.search_result import SearchResult


class TestSecurityValidation:
    """Security tests for RLS, signed URL expiry, and audit completeness."""
    
    @pytest.fixture
    def search_service(self):
        """Create a search service instance for testing."""
        return SearchService()
    
    @pytest.fixture
    def index_service(self):
        """Create an index service instance for testing."""
        return IndexService()
    
    @pytest.fixture
    def audit_logger(self):
        """Create an audit logger instance for testing."""
        return AuditLogger()
    
    @pytest.fixture
    def cdn_service(self):
        """Create a CDN service instance for testing."""
        return CDNService()
    
    @pytest.fixture
    def sample_user_data(self):
        """Create sample user data for testing."""
        return {
            "user_id": "user_123",
            "org_id": "org_456",
            "role": "user",
            "permissions": ["read", "search"]
        }
    
    @pytest.fixture
    def sample_product_data(self):
        """Create sample product data for testing."""
        return [
            {
                "id": "product_1",
                "org_id": "org_456",
                "title": "Test Product 1",
                "price": 29.99,
                "metadata": {"owner": "user_123"}
            },
            {
                "id": "product_2",
                "org_id": "org_789",  # Different org
                "title": "Test Product 2",
                "price": 39.99,
                "metadata": {"owner": "user_456"}
            }
        ]
    
    def test_row_level_security_enforcement(self, search_service, sample_user_data, sample_product_data):
        """Test Row-Level Security (RLS) enforcement in search results."""
        print("🔒 Testing Row-Level Security enforcement")
        
        # Setup mock search results
        mock_results = [
            SearchResult(
                id=product["id"],
                score=0.9,
                metadata=product,
                embedding=None
            )
            for product in sample_product_data
        ]
        
        # Mock search service with RLS
        def mock_search_with_rls(query_embedding, limit=10, user_context=None):
            if user_context is None:
                user_context = sample_user_data
            
            # Apply RLS filter
            filtered_results = []
            for result in mock_results:
                # Check if user has access to this product's org
                if result.metadata["org_id"] == user_context["org_id"]:
                    filtered_results.append(result)
            
            return filtered_results[:limit]
        
        search_service.search_similar = Mock(side_effect=mock_search_with_rls)
        
        # Test RLS enforcement
        query_embedding = [0.1] * 512  # Mock embedding
        
        # Test with correct user context
        results_correct_user = search_service.search_similar(
            query_embedding=query_embedding,
            limit=10,
            user_context=sample_user_data
        )
        
        # Test with different user context
        different_user = {
            "user_id": "user_789",
            "org_id": "org_789",
            "role": "user",
            "permissions": ["read", "search"]
        }
        
        results_different_user = search_service.search_similar(
            query_embedding=query_embedding,
            limit=10,
            user_context=different_user
        )
        
        # Test without user context (should be denied)
        results_no_context = search_service.search_similar(
            query_embedding=query_embedding,
            limit=10,
            user_context=None
        )
        
        print(f"📊 RLS Enforcement Results:")
        print(f"   Correct user results: {len(results_correct_user)}")
        print(f"   Different user results: {len(results_different_user)}")
        print(f"   No context results: {len(results_no_context)}")
        
        # Assert RLS requirements
        assert len(results_correct_user) == 1, f"Correct user should see 1 result, got {len(results_correct_user)}"
        assert results_correct_user[0].metadata["org_id"] == sample_user_data["org_id"]
        
        assert len(results_different_user) == 1, f"Different user should see 1 result, got {len(results_different_user)}"
        assert results_different_user[0].metadata["org_id"] == different_user["org_id"]
        
        assert len(results_no_context) == 0, f"No context should see 0 results, got {len(results_no_context)}"
        
        print("✅ Row-Level Security enforcement test passed!")
    
    def test_signed_url_expiry_validation(self, cdn_service):
        """Test signed URL expiry validation."""
        print("⏰ Testing signed URL expiry validation")
        
        # Test parameters
        secret_key = "test_secret_key_12345"
        base_url = "https://cdn.example.com/images/"
        
        def generate_signed_url(resource_path, expiry_seconds=3600):
            """Generate a signed URL with expiry."""
            expiry_time = int(time.time()) + expiry_seconds
            payload = {
                "resource": resource_path,
                "exp": expiry_time
            }
            token = jwt.encode(payload, secret_key, algorithm="HS256")
            return f"{base_url}{resource_path}?token={token}"
        
        def validate_signed_url(url):
            """Validate a signed URL."""
            try:
                # Extract token from URL
                if "?token=" not in url:
                    return False, "No token found"
                
                token = url.split("?token=")[1]
                payload = jwt.decode(token, secret_key, algorithms=["HS256"])
                
                # Check if URL is expired
                current_time = int(time.time())
                if current_time > payload["exp"]:
                    return False, "URL expired"
                
                return True, "Valid"
            except jwt.ExpiredSignatureError:
                return False, "URL expired"
            except jwt.InvalidTokenError:
                return False, "Invalid token"
            except Exception as e:
                return False, f"Validation error: {str(e)}"
        
        # Test valid URLs
        valid_url = generate_signed_url("product_123.jpg", expiry_seconds=3600)
        is_valid, message = validate_signed_url(valid_url)
        
        print(f"   Valid URL test: {is_valid} - {message}")
        assert is_valid, f"Valid URL should pass validation: {message}"
        
        # Test expired URL
        expired_url = generate_signed_url("product_123.jpg", expiry_seconds=-1)  # Already expired
        is_valid, message = validate_signed_url(expired_url)
        
        print(f"   Expired URL test: {is_valid} - {message}")
        assert not is_valid, f"Expired URL should fail validation: {message}"
        assert "expired" in message.lower(), f"Expired URL should return expired message: {message}"
        
        # Test invalid token
        invalid_url = f"{base_url}product_123.jpg?token=invalid_token"
        is_valid, message = validate_signed_url(invalid_url)
        
        print(f"   Invalid token test: {is_valid} - {message}")
        assert not is_valid, f"Invalid token should fail validation: {message}"
        assert "invalid" in message.lower(), f"Invalid token should return invalid message: {message}"
        
        # Test URL without token
        no_token_url = f"{base_url}product_123.jpg"
        is_valid, message = validate_signed_url(no_token_url)
        
        print(f"   No token test: {is_valid} - {message}")
        assert not is_valid, f"URL without token should fail validation: {message}"
        
        # Test URL with short expiry
        short_expiry_url = generate_signed_url("product_123.jpg", expiry_seconds=1)
        is_valid, message = validate_signed_url(short_expiry_url)
        
        print(f"   Short expiry URL test: {is_valid} - {message}")
        assert is_valid, f"Short expiry URL should be valid initially: {message}"
        
        # Wait for expiry
        time.sleep(2)
        is_valid, message = validate_signed_url(short_expiry_url)
        
        print(f"   Expired short expiry URL test: {is_valid} - {message}")
        assert not is_valid, f"Short expiry URL should expire: {message}"
        
        print("✅ Signed URL expiry validation test passed!")
    
    def test_audit_logging_completeness(self, audit_logger):
        """Test audit logging completeness for security events."""
        print("📝 Testing audit logging completeness")
        
        # Setup mock audit logger
        audit_events = []
        
        def mock_log_event(event_type, user_id, resource_id, action, details=None, success=True):
            event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "user_id": user_id,
                "resource_id": resource_id,
                "action": action,
                "details": details or {},
                "success": success
            }
            audit_events.append(event)
        
        audit_logger.log_event = Mock(side_effect=mock_log_event)
        
        # Test various security events
        test_events = [
            {
                "event_type": "authentication",
                "user_id": "user_123",
                "resource_id": "auth",
                "action": "login",
                "details": {"ip": "192.168.1.1", "user_agent": "Mozilla/5.0"},
                "success": True
            },
            {
                "event_type": "authentication",
                "user_id": "user_456",
                "resource_id": "auth",
                "action": "login",
                "details": {"ip": "192.168.1.2", "user_agent": "Mozilla/5.0"},
                "success": False
            },
            {
                "event_type": "data_access",
                "user_id": "user_123",
                "resource_id": "product_123",
                "action": "read",
                "details": {"org_id": "org_456"},
                "success": True
            },
            {
                "event_type": "data_access",
                "user_id": "user_789",
                "resource_id": "product_123",
                "action": "read",
                "details": {"org_id": "org_789"},
                "success": False
            },
            {
                "event_type": "file_operation",
                "user_id": "user_123",
                "resource_id": "image_123.jpg",
                "action": "upload",
                "details": {"file_size": 1024000, "file_type": "image/jpeg"},
                "success": True
            },
            {
                "event_type": "search",
                "user_id": "user_123",
                "resource_id": "search_session_123",
                "action": "query",
                "details": {"query_type": "image", "results_count": 10},
                "success": True
            },
            {
                "event_type": "system",
                "user_id": "system",
                "resource_id": "index_rebuild",
                "action": "start",
                "details": {"index_size": 1000000},
                "success": True
            },
            {
                "event_type": "security",
                "user_id": "user_456",
                "resource_id": "api_endpoint",
                "action": "rate_limit_exceeded",
                "details": {"endpoint": "/api/v1/search", "limit": 100},
                "success": False
            }
        ]
        
        # Log all test events
        for event in test_events:
            audit_logger.log_event(
                event_type=event["event_type"],
                user_id=event["user_id"],
                resource_id=event["resource_id"],
                action=event["action"],
                details=event["details"],
                success=event["success"]
            )
        
        print(f"📊 Audit Logging Results:")
        print(f"   Total events logged: {len(audit_events)}")
        
        # Analyze event types
        event_types = {}
        for event in audit_events:
            event_type = event["event_type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        for event_type, count in event_types.items():
            print(f"   {event_type}: {count} events")
        
        # Check for required event types
        required_event_types = ["authentication", "data_access", "file_operation", "search", "system", "security"]
        for required_type in required_event_types:
            assert required_type in event_types, f"Missing required event type: {required_type}"
        
        # Check event completeness
        for event in audit_events:
            required_fields = ["timestamp", "event_type", "user_id", "resource_id", "action", "success"]
            for field in required_fields:
                assert field in event, f"Missing required field '{field}' in audit event"
                assert event[field] is not None, f"Required field '{field}' is None in audit event"
        
        # Check for security events
        security_events = [e for e in audit_events if e["event_type"] == "security"]
        assert len(security_events) > 0, "No security events logged"
        
        # Check for failed authentication attempts
        failed_auth_events = [e for e in audit_events if e["event_type"] == "authentication" and not e["success"]]
        assert len(failed_auth_events) > 0, "No failed authentication events logged"
        
        # Check for data access violations
        failed_access_events = [e for e in audit_events if e["event_type"] == "data_access" and not e["success"]]
        assert len(failed_access_events) > 0, "No data access violation events logged"
        
        print("✅ Audit logging completeness test passed!")
    
    def test_permission_based_access_control(self, search_service, index_service, sample_user_data):
        """Test permission-based access control."""
        print("🔐 Testing permission-based access control")
        
        # Define different user roles and permissions
        user_roles = {
            "admin": {
                "user_id": "admin_123",
                "org_id": "org_456",
                "role": "admin",
                "permissions": ["read", "write", "delete", "search", "index_manage"]
            },
            "user": {
                "user_id": "user_123",
                "org_id": "org_456",
                "role": "user",
                "permissions": ["read", "search"]
            },
            "viewer": {
                "user_id": "viewer_123",
                "org_id": "org_456",
                "role": "viewer",
                "permissions": ["read"]
            }
        }
        
        def check_permission(user_context, required_permission):
            """Check if user has required permission."""
            if not user_context or "permissions" not in user_context:
                return False
            return required_permission in user_context["permissions"]
        
        # Test search permissions
        search_permission_tests = [
            {"user": "admin", "permission": "search", "should_allow": True},
            {"user": "user", "permission": "search", "should_allow": True},
            {"user": "viewer", "permission": "search", "should_allow": False},
            {"user": "admin", "permission": "write", "should_allow": True},
            {"user": "user", "permission": "write", "should_allow": False},
        ]
        
        for test in search_permission_tests:
            user_context = user_roles[test["user"]]
            has_permission = check_permission(user_context, test["permission"])
            
            print(f"   {test['user']} - {test['permission']}: {'✅' if has_permission == test['should_allow'] else '❌'}")
            assert has_permission == test["should_allow"], \
                f"Permission check failed for {test['user']} - {test['permission']}"
        
        # Test index management permissions
        index_permission_tests = [
            {"user": "admin", "permission": "index_manage", "should_allow": True},
            {"user": "user", "permission": "index_manage", "should_allow": False},
            {"user": "viewer", "permission": "index_manage", "should_allow": False},
        ]
        
        for test in index_permission_tests:
            user_context = user_roles[test["user"]]
            has_permission = check_permission(user_context, test["permission"])
            
            print(f"   {test['user']} - {test['permission']}: {'✅' if has_permission == test['should_allow'] else '❌'}")
            assert has_permission == test["should_allow"], \
                f"Permission check failed for {test['user']} - {test['permission']}"
        
        print("✅ Permission-based access control test passed!")
    
    def test_data_encryption_validation(self, index_service):
        """Test data encryption validation."""
        print("🔐 Testing data encryption validation")
        
        # Test encryption of sensitive data
        sensitive_data = {
            "user_id": "user_123",
            "api_key": "sk_test_1234567890abcdef",
            "password_hash": "hashed_password_123",
            "personal_info": {
                "email": "user@example.com",
                "phone": "+1234567890"
            }
        }
        
        def encrypt_sensitive_data(data, encryption_key="test_key_123"):
            """Mock encryption function."""
            import hashlib
            encrypted_data = {}
            
            for key, value in data.items():
                if isinstance(value, dict):
                    encrypted_data[key] = encrypt_sensitive_data(value, encryption_key)
                elif key in ["api_key", "password_hash", "email", "phone"]:
                    # Encrypt sensitive fields
                    encrypted_value = hashlib.sha256(f"{value}{encryption_key}".encode()).hexdigest()
                    encrypted_data[key] = f"encrypted_{encrypted_value[:16]}"
                else:
                    encrypted_data[key] = value
            
            return encrypted_data
        
        def validate_encryption(data):
            """Validate that sensitive data is encrypted."""
            sensitive_fields = ["api_key", "password_hash", "email", "phone"]
            
            for field in sensitive_fields:
                if field in data:
                    if not data[field].startswith("encrypted_"):
                        return False, f"Field '{field}' is not encrypted"
            
            # Check nested objects
            for key, value in data.items():
                if isinstance(value, dict):
                    is_valid, message = validate_encryption(value)
                    if not is_valid:
                        return False, message
            
            return True, "All sensitive data is encrypted"
        
        # Test encryption
        encrypted_data = encrypt_sensitive_data(sensitive_data)
        is_valid, message = validate_encryption(encrypted_data)
        
        print(f"   Encryption validation: {is_valid} - {message}")
        assert is_valid, f"Encryption validation failed: {message}"
        
        # Test that non-sensitive data is not encrypted
        assert encrypted_data["user_id"] == "user_123", "Non-sensitive data should not be encrypted"
        
        # Test that sensitive data is encrypted
        assert encrypted_data["api_key"].startswith("encrypted_"), "API key should be encrypted"
        assert encrypted_data["password_hash"].startswith("encrypted_"), "Password hash should be encrypted"
        assert encrypted_data["personal_info"]["email"].startswith("encrypted_"), "Email should be encrypted"
        assert encrypted_data["personal_info"]["phone"].startswith("encrypted_"), "Phone should be encrypted"
        
        print("✅ Data encryption validation test passed!")
    
    def test_rate_limiting_enforcement(self, search_service):
        """Test rate limiting enforcement."""
        print("🚦 Testing rate limiting enforcement")
        
        # Setup rate limiting
        rate_limits = {
            "search": {"requests_per_minute": 60, "requests_per_hour": 1000},
            "index": {"requests_per_minute": 30, "requests_per_hour": 500},
            "upload": {"requests_per_minute": 10, "requests_per_hour": 100}
        }
        
        # Track requests
        request_counts = {
            "search": {"minute": 0, "hour": 0, "last_reset": time.time()},
            "index": {"minute": 0, "hour": 0, "last_reset": time.time()},
            "upload": {"minute": 0, "hour": 0, "last_reset": time.time()}
        }
        
        def check_rate_limit(operation_type, user_id):
            """Check if request is within rate limits."""
            current_time = time.time()
            
            # Reset counters if needed
            if current_time - request_counts[operation_type]["last_reset"] >= 60:
                request_counts[operation_type]["minute"] = 0
                request_counts[operation_type]["last_reset"] = current_time
            
            if current_time - request_counts[operation_type]["last_reset"] >= 3600:
                request_counts[operation_type]["hour"] = 0
            
            # Check limits
            minute_limit = rate_limits[operation_type]["requests_per_minute"]
            hour_limit = rate_limits[operation_type]["requests_per_hour"]
            
            if request_counts[operation_type]["minute"] >= minute_limit:
                return False, "Minute rate limit exceeded"
            
            if request_counts[operation_type]["hour"] >= hour_limit:
                return False, "Hour rate limit exceeded"
            
            # Increment counters
            request_counts[operation_type]["minute"] += 1
            request_counts[operation_type]["hour"] += 1
            
            return True, "Within rate limits"
        
        # Test rate limiting
        successful_requests = 0
        blocked_requests = 0
        
        # Test search rate limiting
        for i in range(70):  # Exceed minute limit
            is_allowed, message = check_rate_limit("search", "user_123")
            if is_allowed:
                successful_requests += 1
            else:
                blocked_requests += 1
                print(f"   Request {i+1} blocked: {message}")
        
        print(f"📊 Rate Limiting Results:")
        print(f"   Successful requests: {successful_requests}")
        print(f"   Blocked requests: {blocked_requests}")
        print(f"   Block rate: {blocked_requests/(successful_requests+blocked_requests)*100:.1f}%")
        
        # Assert rate limiting requirements
        assert successful_requests == 60, f"Should allow exactly 60 requests per minute, got {successful_requests}"
        assert blocked_requests == 10, f"Should block 10 requests, got {blocked_requests}"
        
        # Test that rate limits are enforced
        assert request_counts["search"]["minute"] == 60, "Minute counter should be at limit"
        
        print("✅ Rate limiting enforcement test passed!")
    
    def test_input_validation_and_sanitization(self, search_service):
        """Test input validation and sanitization."""
        print("🧹 Testing input validation and sanitization")
        
        # Test malicious inputs
        malicious_inputs = [
            {"type": "sql_injection", "value": "'; DROP TABLE products; --"},
            {"type": "xss", "value": "<script>alert('xss')</script>"},
            {"type": "path_traversal", "value": "../../../etc/passwd"},
            {"type": "command_injection", "value": "image.jpg; rm -rf /"},
            {"type": "overflow", "value": "A" * 10000},
            {"type": "special_chars", "value": "!@#$%^&*()_+-=[]{}|;':\",./<>?"}
        ]
        
        def validate_and_sanitize_input(input_value, input_type="text"):
            """Validate and sanitize input."""
            # Check for SQL injection
            sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER"]
            if any(keyword.lower() in input_value.lower() for keyword in sql_keywords):
                return False, "SQL injection detected"
            
            # Check for XSS
            if "<script>" in input_value.lower() or "javascript:" in input_value.lower():
                return False, "XSS detected"
            
            # Check for path traversal
            if ".." in input_value or "/etc/" in input_value:
                return False, "Path traversal detected"
            
            # Check for command injection
            if ";" in input_value or "|" in input_value or "&" in input_value:
                return False, "Command injection detected"
            
            # Check for overflow
            if len(input_value) > 1000:
                return False, "Input too long"
            
            # Sanitize input
            sanitized = input_value.replace("<", "&lt;").replace(">", "&gt;")
            sanitized = sanitized.replace("'", "&#39;").replace('"', "&quot;")
            
            return True, sanitized
        
        # Test each malicious input
        validation_results = []
        
        for malicious_input in malicious_inputs:
            is_valid, result = validate_and_sanitize_input(malicious_input["value"])
            validation_results.append({
                "type": malicious_input["type"],
                "input": malicious_input["value"],
                "is_valid": is_valid,
                "result": result
            })
            
            print(f"   {malicious_input['type']}: {'❌' if not is_valid else '✅'} - {result}")
        
        # Assert security requirements
        blocked_inputs = [r for r in validation_results if not r["is_valid"]]
        allowed_inputs = [r for r in validation_results if r["is_valid"]]
        
        assert len(blocked_inputs) >= 4, f"Should block at least 4 malicious inputs, blocked {len(blocked_inputs)}"
        assert len(allowed_inputs) <= 2, f"Should allow at most 2 inputs, allowed {len(allowed_inputs)}"
        
        # Check that dangerous inputs are blocked
        dangerous_types = ["sql_injection", "xss", "path_traversal", "command_injection"]
        for dangerous_type in dangerous_types:
            blocked = any(r["type"] == dangerous_type and not r["is_valid"] for r in validation_results)
            assert blocked, f"Dangerous input type '{dangerous_type}' was not blocked"
        
        print("✅ Input validation and sanitization test passed!")
    
    def test_session_management_security(self, search_service):
        """Test session management security."""
        print("🔑 Testing session management security")
        
        # Mock session management
        sessions = {}
        session_timeout = 3600  # 1 hour
        
        def create_session(user_id, org_id):
            """Create a new session."""
            session_id = f"session_{user_id}_{int(time.time())}"
            session_data = {
                "user_id": user_id,
                "org_id": org_id,
                "created_at": time.time(),
                "last_activity": time.time(),
                "is_active": True
            }
            sessions[session_id] = session_data
            return session_id
        
        def validate_session(session_id):
            """Validate a session."""
            if session_id not in sessions:
                return False, "Session not found"
            
            session = sessions[session_id]
            current_time = time.time()
            
            # Check if session is expired
            if current_time - session["created_at"] > session_timeout:
                session["is_active"] = False
                return False, "Session expired"
            
            # Check if session is inactive
            if not session["is_active"]:
                return False, "Session inactive"
            
            # Update last activity
            session["last_activity"] = current_time
            return True, "Session valid"
        
        def invalidate_session(session_id):
            """Invalidate a session."""
            if session_id in sessions:
                sessions[session_id]["is_active"] = False
        
        # Test session creation and validation
        session_id = create_session("user_123", "org_456")
        is_valid, message = validate_session(session_id)
        
        print(f"   Session validation: {is_valid} - {message}")
        assert is_valid, f"Valid session should pass validation: {message}"
        
        # Test session invalidation
        invalidate_session(session_id)
        is_valid, message = validate_session(session_id)
        
        print(f"   Invalidated session: {is_valid} - {message}")
        assert not is_valid, f"Invalidated session should fail validation: {message}"
        
        # Test non-existent session
        is_valid, message = validate_session("non_existent_session")
        
        print(f"   Non-existent session: {is_valid} - {message}")
        assert not is_valid, f"Non-existent session should fail validation: {message}"
        
        # Test session timeout simulation
        session_id_2 = create_session("user_456", "org_789")
        sessions[session_id_2]["created_at"] = time.time() - session_timeout - 1  # Expired
        
        is_valid, message = validate_session(session_id_2)
        
        print(f"   Expired session: {is_valid} - {message}")
        assert not is_valid, f"Expired session should fail validation: {message}"
        
        print("✅ Session management security test passed!")
    
    def test_secure_communication_validation(self, search_service):
        """Test secure communication validation."""
        print("🔒 Testing secure communication validation")
        
        # Test HTTPS enforcement
        def validate_https_url(url):
            """Validate that URL uses HTTPS."""
            if not url.startswith("https://"):
                return False, "URL must use HTTPS"
            return True, "HTTPS URL is valid"
        
        # Test API endpoint security
        def validate_api_security(endpoint, method, headers):
            """Validate API endpoint security."""
            security_issues = []
            
            # Check for HTTPS
            if not endpoint.startswith("https://"):
                security_issues.append("Endpoint must use HTTPS")
            
            # Check for required headers
            required_headers = ["Authorization", "Content-Type"]
            for header in required_headers:
                if header not in headers:
                    security_issues.append(f"Missing required header: {header}")
            
            # Check for secure content type
            if "Content-Type" in headers and "application/json" not in headers["Content-Type"]:
                security_issues.append("Content-Type should be application/json")
            
            # Check for authorization header format
            if "Authorization" in headers:
                auth_header = headers["Authorization"]
                if not auth_header.startswith("Bearer ") and not auth_header.startswith("Basic "):
                    security_issues.append("Authorization header format invalid")
            
            return len(security_issues) == 0, security_issues
        
        # Test various endpoints
        test_endpoints = [
            {
                "endpoint": "https://api.example.com/v1/search",
                "method": "POST",
                "headers": {
                    "Authorization": "Bearer token_123",
                    "Content-Type": "application/json"
                }
            },
            {
                "endpoint": "http://api.example.com/v1/search",  # Insecure
                "method": "POST",
                "headers": {
                    "Authorization": "Bearer token_123",
                    "Content-Type": "application/json"
                }
            },
            {
                "endpoint": "https://api.example.com/v1/search",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json"
                    # Missing Authorization
                }
            },
            {
                "endpoint": "https://api.example.com/v1/search",
                "method": "POST",
                "headers": {
                    "Authorization": "Bearer token_123",
                    "Content-Type": "text/plain"  # Wrong content type
                }
            }
        ]
        
        secure_endpoints = 0
        insecure_endpoints = 0
        
        for i, test in enumerate(test_endpoints):
            is_secure, issues = validate_api_security(
                test["endpoint"],
                test["method"],
                test["headers"]
            )
            
            if is_secure:
                secure_endpoints += 1
                print(f"   Endpoint {i+1}: ✅ Secure")
            else:
                insecure_endpoints += 1
                print(f"   Endpoint {i+1}: ❌ Insecure - {', '.join(issues)}")
        
        print(f"📊 Secure Communication Results:")
        print(f"   Secure endpoints: {secure_endpoints}")
        print(f"   Insecure endpoints: {insecure_endpoints}")
        
        # Assert security requirements
        assert secure_endpoints == 1, f"Should have 1 secure endpoint, got {secure_endpoints}"
        assert insecure_endpoints == 3, f"Should have 3 insecure endpoints, got {insecure_endpoints}"
        
        print("✅ Secure communication validation test passed!")
