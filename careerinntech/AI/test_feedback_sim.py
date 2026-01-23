import json
from AI.services import parse_feedback_raw

# Simple simulation to validate parsing and ordering behavior

def run_sim():
    qa_pairs = [
        {"question": "Tell me about yourself", "answer": "I have 3 years experience in web dev."},
        {"question": "What are your strengths?", "answer": "Problem solving and teamwork."},
        {"question": "What are your weaknesses?", "answer": "I sometimes overwork."}
    ]

    weights = {
        "Technical Knowledge": 0.28,
        "Problem Solving": 0.28,
        "Communication": 0.14,
        "Confidence": 0.14,
        "Creativity": 0.08,
        "Time Management": 0.08
    }

    # Create a fake LLM raw response (intentionally reorders per-question feedback)
    fake_llm = {
        "overall_score": 75,
        "verdict_title": "Good",
        "verdict_summary": "Candidate shows promise.",
        "skills": [
            {"name": "Technical Knowledge", "score": 70},
            {"name": "Problem Solving", "score": 80},
            {"name": "Communication", "score": 65},
            {"name": "Confidence", "score": 60},
            {"name": "Creativity", "score": 50},
            {"name": "Time Management", "score": 55}
        ],
        "per_question_feedback": [
            {
                "question": "What are your weaknesses?",
                "answer": "I sometimes overwork.",
                "feedback": "Be concise and focus on steps to improve.",
                "score": 6
            },
            {
                "question": "Tell me about yourself",
                "answer": "I have 3 years experience in web dev.",
                "feedback": "Good summary, include specific achievements.",
                "score": 7
            },
            {
                "question": "What are your strengths?",
                "answer": "Problem solving and teamwork.",
                "feedback": "Strong examples; add metrics.",
                "score": 8
            }
        ]
    }

    raw_text = json.dumps(fake_llm)

    data = parse_feedback_raw(raw_text, weights, qa_pairs, conversation="")

    print("Parsed overall_score:", data.get("overall_score"))
    print("Per-question order:")
    for i, fb in enumerate(data.get("per_question_feedback", [])):
        print(f"{i+1}. Q={fb['question']}  score={fb['score']}")

    # Basic checks
    assert len(data.get("per_question_feedback", [])) == len(qa_pairs), "Per-question feedback length mismatch"
    for i, pair in enumerate(qa_pairs):
        assert data["per_question_feedback"][i]["question"] == pair["question"], "Ordering mismatch at index %s" % i

    print("All checks passed.")


if __name__ == '__main__':
    run_sim()
