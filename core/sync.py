import json
import os
import urllib.request
from core.database import get_pending_sync_items, mark_sync_item_done, increment_sync_attempt

SYNC_ENDPOINT = os.environ.get("SYNC_ENDPOINT", "")
MAX_RETRY = 5


def check_connectivity(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=3):
            return True
    except Exception:
        return False


def sync_pending_items(endpoint: str, conn=None) -> dict:
    items = get_pending_sync_items(conn=conn)
    synced = 0
    failed = 0
    for item in items:
        if item["attempts"] >= MAX_RETRY:
            continue
        payload_bytes = json.dumps({
            "operation": item["operation"],
            "payload": json.loads(item["payload"]),
        }).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=payload_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5):
                mark_sync_item_done(item["id"], conn=conn)
                synced += 1
        except Exception:
            increment_sync_attempt(item["id"], conn=conn)
            failed += 1
    return {"synced": synced, "failed": failed}


def try_sync(conn=None) -> dict:
    if not SYNC_ENDPOINT:
        return {"synced": 0, "failed": 0, "skipped": True}
    if not check_connectivity(SYNC_ENDPOINT):
        return {"synced": 0, "failed": 0, "offline": True}
    return sync_pending_items(SYNC_ENDPOINT, conn=conn)
