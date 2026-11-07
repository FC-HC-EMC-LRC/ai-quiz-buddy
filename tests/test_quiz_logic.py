import pytest

from src.quiz_logic import calculate_score, parse_quiz_json


def test_parse_quiz_json_clean_payload():
    raw_payload = """
    [
        {
            "question": "What is the capital of France?",
            "options": ["Paris", "Rome", "Berlin"],
            "answer": "Paris"
        }
    ]
    """
    result = parse_quiz_json(raw_payload)
    assert len(result) == 1
    assert result[0]["answer"] == "Paris"


def test_parse_quiz_json_with_markdown_fences():
    raw_payload = """
    ```json
    [
        {
            "question": "What is 2 + 2?",
            "options": ["3", "4", "5"],
            "answer": "4"
        }
    ]
    ```
    """
    result = parse_quiz_json(raw_payload)
    assert len(result) == 1
    assert result[0]["answer"] == "4"


def test_parse_quiz_json_missing_fields_raises_error():
    broken_payload = '[{"question": "No options given"}]'
    with pytest.raises(ValueError, match="Question missing required fields"):
        parse_quiz_json(broken_payload)


def test_calculate_score():
    sample_questions = [
        {"question": "Q1", "options": ["A", "B"], "answer": "A"},
        {"question": "Q2", "options": ["X", "Y"], "answer": "Y"},
    ]

    # Both correct
    correct, total = calculate_score({0: "A", 1: "Y"}, sample_questions)
    assert correct == 2
    assert total == 2

    # One correct, one wrong
    correct, total = calculate_score({0: "A", 1: "X"}, sample_questions)
    assert correct == 1
    assert total == 2

    # Incomplete answers
    correct, total = calculate_score({0: "A"}, sample_questions)
    assert correct == 1
    assert total == 2