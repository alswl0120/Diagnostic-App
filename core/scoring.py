from core.models import DomainScore, Level


def classify_level(score: float) -> Level:
    if score <= 0.40:
        return 1
    if score <= 0.60:
        return 2
    if score <= 0.80:
        return 3
    return 4


def score_domain(responses: list, correct_indices: list) -> DomainScore:
    total = len(correct_indices)
    correct = sum(
        1 for r, c in zip(responses, correct_indices)
        if r is not None and r == c
    )
    score = correct / total if total > 0 else 0.0
    return DomainScore(score=score, level=classify_level(score), correct=correct, total=total)


def score_section(section_responses: dict, questions_by_domain: dict) -> dict:
    result = {}
    for domain, questions in questions_by_domain.items():
        responses = section_responses.get(domain, [None] * len(questions))
        correct_indices = [q["answer_index"] for q in questions]
        result[domain] = score_domain(responses, correct_indices)
    return result


def compute_overall_level(all_scores: dict) -> Level:
    if not all_scores:
        return 1
    avg = sum(d["score"] for d in all_scores.values()) / len(all_scores)
    return classify_level(avg)
