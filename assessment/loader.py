import json
from pathlib import Path

QUESTIONS_DIR = Path(__file__).parent / "questions"


def load_questions(subject: str) -> dict:
    path = QUESTIONS_DIR / f"{subject}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_questions_by_domain(subject: str) -> dict:
    data = load_questions(subject)
    grouped = {}
    for item in data["items"]:
        domain = item["domain"]
        if domain not in grouped:
            grouped[domain] = []
        grouped[domain].append(item)
    return grouped


def get_ordered_items(subject: str) -> list:
    grouped = get_questions_by_domain(subject)
    ordered = []
    data = load_questions(subject)
    domain_order = list(data["domains"].keys())
    for domain in domain_order:
        items = sorted(grouped.get(domain, []), key=lambda x: x["difficulty"])
        ordered.extend(items)
    return ordered
