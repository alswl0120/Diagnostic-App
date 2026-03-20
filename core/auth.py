import json
import os


def get_user(headers: dict) -> dict:
    return {
        "user_id": headers.get("X-User-Id") or "anonymous",
        "email": headers.get("X-User-Email") or "",
        "name": headers.get("X-User-Name") or "",
        "roles": headers.get("X-User-Roles") or "",
    }


def get_dev_user() -> dict | None:
    raw = os.environ.get("DEV_USER")
    if not raw:
        return None
    return json.loads(raw)


def is_teacher(roles: str | None) -> bool:
    if not roles:
        return False
    parts = {r.strip() for r in roles.split(",")}
    return bool(parts & {"staff", "teacher"})
