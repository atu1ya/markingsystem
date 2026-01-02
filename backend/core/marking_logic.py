from typing import Dict, List, Tuple

Letter = str  # "A" to "E"


def mark_section(
    student_answers: Dict[str, Letter],
    answer_key: Dict[str, Letter],
) -> Tuple[Dict[str, bool], int, int]:
    """Return (per_question_correct, total_correct, total_questions)."""
    results: Dict[str, bool] = {}
    total_correct = 0
    total_questions = len(answer_key)

    for qid, correct_letter in answer_key.items():
        student_letter = student_answers.get(qid)
        is_correct = student_letter == correct_letter
        results[qid] = is_correct
        if is_correct:
            total_correct += 1

    return results, total_correct, total_questions


def compute_strengths_weaknesses(
    per_question_correct_by_subject: Dict[str, Dict[str, bool]],
    concept_map: Dict[str, Dict[str, List[int]]],
) -> Dict[str, Dict[str, List[str]]]:
    """Return { subject: { 'done_well': [concepts], 'needs_improvement': [concepts] } }."""
    result: Dict[str, Dict[str, List[str]]] = {}

    for subject, concepts in concept_map.items():
        subject_results = {
            "done_well": [],
            "needs_improvement": [],
        }

        question_correct = per_question_correct_by_subject.get(subject, {})

        for concept_name, question_numbers in concepts.items():
            if not question_numbers:
                continue

            correct_count = 0
            total = len(question_numbers)

            for qnum in question_numbers:
                qid = str(qnum)
                if question_correct.get(qid):
                    correct_count += 1

            percent_correct = 100.0 * correct_count / total

            if percent_correct >= 51.0:
                subject_results["done_well"].append(concept_name)
            else:
                subject_results["needs_improvement"].append(concept_name)

        result[subject] = subject_results

    return result
