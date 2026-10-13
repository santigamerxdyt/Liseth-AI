from app.main import app

registered = []
for r in app.routes:
    if hasattr(r, "path"):
        registered.append(r.path)
    elif hasattr(r, "routes"):
        for sub_r in r.routes:
            registered.append(getattr(sub_r, "path", ""))

frontend_endpoints = [
    "/api/status",
    "/api/history",
    "/api/config",
    "/api/brain/chat",
    "/api/brain/status",
    "/api/brain/switch",
    "/api/google/status",
    "/api/google/auth-url",
    "/api/audit/logs",
    "/api/audit/confirm",
    "/api/scheduler/tasks",
    "/api/scheduler/tasks/trigger",
    "/api/notifications/test",
    "/api/upload",
    "/api/auth/login",
    "/api/auth/logout",
    "/api/auth/status",
]

print("=== CHECKING FRONTEND ENDPOINTS IN BACKEND ===")
for ep in frontend_endpoints:
    found = any(ep == r or ep.rstrip("/") == r.rstrip("/") for r in registered)
    print(f"{ep:<32} -> {'EXISTS' if found else 'MISSING 404'}")
