from app.core.rag import ask

test_cases = [
    {
        "question": "NLP nedir?",
        "expected_keywords": ["Doğal dil", "bilgisayar", "anlama"],
        "expected_source": "ai.txt"
    },
    {
        "question": "Overfitting nedir?",
        "expected_keywords": ["ezber", "yeni veri", "başarısız"],
        "expected_source": "ml.txt"
    }
]


def evaluate():
    """Test senaryolarını çalıştır ve sonuçları döndür"""
    results = []
    for case in test_cases:
        answer, sources = ask(case["question"])
        keyword_hits = sum(
            1 for kw in case["expected_keywords"]
            if kw.lower() in answer.lower()
        )
        keyword_score = keyword_hits / len(case["expected_keywords"])

        source_correct = case["expected_source"] in sources

        results.append({
            "question": case["question"],
            "keyword_score": keyword_score,
            "source_correct": source_correct,
            "answer_preview": answer[:100]
        })

    return results
