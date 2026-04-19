from starlette.middleware.base import BaseHTTPMiddleware

# This middleware adds security headers to the response to enhance security against common web vulnerabilities.
# should be async to ensure it works properly with the asynchronous nature of FastAPI and Starlette.
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
     async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
     

