📝 TO-DO: Health Check Endpoints (Future Enhancement)
Priority: Low (Production Monitoring)
Effort: ~30 minutes
Value: High for production monitoring, container orchestration, and deployment automation
Implementation: Add three endpoints:
/health - Detailed health check (database, ChromaDB, environment vars)
/health/ready - Kubernetes readiness probe
/health/live - Kubernetes liveness probe
Use cases: Monitoring dashboards, load balancer health checks, Kubernetes probes, CI/CD deployment verification

📝 TO-DO: Better Error Handling for External API Calls (Production Reliability)
Priority: Medium (Production Stability)
Effort: ~45 minutes
Value: High for production resilience and user experience
Implementation: Replace basic requests with robust httpx + tenacity:
- Add retry logic with exponential backoff (3 attempts)
- Reduce timeout from 60s to 30s for better UX
- Add connection pooling and HTTP/2 support
- Categorize errors (auth, rate limit, network, server)
- Smart retry logic (only retry transient failures)
Dependencies: pip install httpx tenacity
Use cases: Handle network issues, API rate limits, server errors gracefully

Add this to the server startup
uvicorn main:app --host 0.0.0.0 --port 8000 --limit-max-requests 1000 --limit-request-field_size 8190