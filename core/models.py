from typing import TypedDict, Literal

Subject = Literal["math", "science"]
Level = Literal[1, 2, 3, 4]


class DomainScore(TypedDict):
    score: float
    level: Level
    correct: int
    total: int


class AttemptResult(TypedDict):
    attempt_id: int
    student_name: str
    math_scores: dict
    science_scores: dict
    overall_level: Level
    completed_at: str


class Question(TypedDict):
    id: str
    domain: str
    difficulty: int
    stem: str
    options: list
    answer_index: int
    image_path: str | None
