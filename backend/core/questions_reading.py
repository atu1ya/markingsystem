from typing import List, Tuple

Rect = Tuple[int, int, int, int]


class QuestionROI:
    def __init__(self, qid: int, options: List[Rect]):
        self.id = qid
        self.options = options  # [A, B, C, D, E]


def _placeholder_options() -> List[Rect]:
    return [(0, 0, 0, 0)] * 5


QUESTIONS_READING: List[QuestionROI] = [
    QuestionROI(qid, _placeholder_options())
    for qid in range(1, 36)
]
