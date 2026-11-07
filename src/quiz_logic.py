import json
import re


def parse_quiz_json(raw_text: str) -> list[dict]:
    """Extracts and validates a JSON array of quiz questions from raw AI output.

    Handles outputs wrapped in markdown code fences (```json ... ```).
    """
    cleaned = raw_text.strip()

    # Strip markdown code fence if present
    match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("AI response did not contain valid JSON.") from exc

    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("Parsed data must be a non-empty list of questions.")

    for item in data:
        required_keys = {"question", "options", "answer"}
        if not required_keys.issubset(item.keys()):
            raise ValueError(
                f"Question missing required fields: {required_keys - set(item.keys())}"
            )
        if not isinstance(item["options"], list) or len(item["options"]) < 2:
            raise ValueError("Each question must contain at least 2 options.")
        if item["answer"] not in item["options"]:
            raise ValueError("The designated answer must match one of the options.")

    return data


def calculate_score(user_answers: dict[int, str], questions: list[dict]) -> tuple[int, int]:
    """Calculates total correct answers against total questions.

    Returns (correct_count, total_count).
    """
    total = len(questions)
    correct = sum(
        1
        for idx, q in enumerate(questions)
        if user_answers.get(idx) == q["answer"]
    )
    return correct, total