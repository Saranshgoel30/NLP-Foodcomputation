"""
Rate limiting and security middleware for the API
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger()


class RateLimiter:
    """
    Token bucket rate limiter
    Allows burst requests while enforcing average rate
    """
    
    def __init__(self, rate: int = 60, per: int = 60):
        """
        Args:
            rate: Number of requests allowed
            per: Time window in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance: Dict[str, float] = defaultdict(lambda: rate)
        self.last_check: Dict[str, float] = defaultdict(lambda: time.time())
    
    def is_allowed(self, key: str) -> Tuple[bool, float]:
        """
        Check if request is allowed for given key (usually IP or API key)
        
        Returns:
            (is_allowed, retry_after_seconds)
        """
        current = time.time()
        time_passed = current - self.last_check[key]
        self.last_check[key] = current
        
        # Add tokens based on time passed
        self.allowance[key] += time_passed * (self.rate / self.per)
        
        # Cap at rate limit
        if self.allowance[key] > self.rate:
            self.allowance[key] = self.rate
        
        # Check if we have tokens
        if self.allowance[key] < 1.0:
            retry_after = (1.0 - self.allowance[key]) / (self.rate / self.per)
            return False, retry_after
        
        # Consume one token
        self.allowance[key] -= 1.0
        return True, 0.0
    
    def reset(self, key: str):
        """Reset rate limit for a key"""
        if key in self.allowance:
            del self.allowance[key]
        if key in self.last_check:
            del self.last_check[key]


# Global rate limiters for different endpoints
rate_limiters = {
    "default": RateLimiter(rate=60, per=60),  # 60 requests per minute
    "search": RateLimiter(rate=30, per=60),   # 30 searches per minute
    "stt": RateLimiter(rate=10, per=60),      # 10 STT requests per minute (expensive)
    "voice": RateLimiter(rate=10, per=60),    # 10 voice searches per minute
}


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies"""
    # Check X-Forwarded-For header (from proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take first IP in chain
        return forwarded.split(",")[0].strip()
    
    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fall back to direct connection IP
    if request.client:
        return request.client.host
    
    return "unknown"


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware
    Applies different limits based on endpoint
    """
    # Skip rate limiting for health checks and docs
    if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Determine which rate limiter to use
    path = request.url.path.lower()
    if "/search" in path and "/voice" not in path:
        limiter_key = "search"
    elif "/stt" in path or "/voice" in path:
        limiter_key = "voice"
    else:
        limiter_key = "default"
    
    limiter = rate_limiters[limiter_key]
    client_ip = get_client_ip(request)
    
    # Check rate limit
    is_allowed, retry_after = limiter.is_allowed(client_ip)
    
    if not is_allowed:
        logger.warning(
            "rate_limit_exceeded",
            client_ip=client_ip,
            path=request.url.path,
            retry_after=retry_after
        )
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "RateLimitExceeded",
                "message": "Too many requests. Please slow down.",
                "retry_after_seconds": round(retry_after, 2)
            },
            headers={
                "Retry-After": str(int(retry_after) + 1),
                "X-RateLimit-Limit": str(limiter.rate),
                "X-RateLimit-Remaining": "0"
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    remaining = int(limiter.allowance.get(client_ip, limiter.rate))
    response.headers["X-RateLimit-Limit"] = str(limiter.rate)
    response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + limiter.per)
    
    return response


async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # CORS headers are handled by CORSMiddleware
    
    return response


async def request_id_middleware(request: Request, call_next):
    """Add unique request ID for tracing"""
    import uuid
    
    # Generate or use existing request ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    # Add to logger context
    logger.bind(request_id=request_id)
    
    # Process request
    response = await call_next(request)
    
    # Add request ID to response
    response.headers["X-Request-ID"] = request_id
    
    return response
