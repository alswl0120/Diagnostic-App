def init_responses(subject: str, grouped: dict) -> dict:
    return {domain: [None] * len(items) for domain, items in grouped.items()}


def record_response(responses: dict, domain: str, item_index_in_domain: int, answer_index: int) -> dict:
    responses[domain][item_index_in_domain] = answer_index
    return responses


def is_section_complete(responses: dict) -> bool:
    return all(
        ans is not None
        for domain_responses in responses.values()
        for ans in domain_responses
    )


def get_flat_index(ordered_items: list, domain: str, item_index_in_domain: int) -> int:
    count = 0
    for item in ordered_items:
        if item["domain"] == domain:
            if item_index_in_domain == 0:
                return count
            item_index_in_domain -= 1
        count += 1
    return -1


def get_domain_and_local_index(ordered_items: list, flat_index: int) -> tuple:
    domain_counters = {}
    for i, item in enumerate(ordered_items):
        domain = item["domain"]
        if domain not in domain_counters:
            domain_counters[domain] = 0
        if i == flat_index:
            return domain, domain_counters[domain]
        domain_counters[domain] += 1
    return None, None
