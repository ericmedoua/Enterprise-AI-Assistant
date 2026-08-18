from app.ai.retrieval.dependencies import get_retriever


EVALUATION_QUESTIONS = [
    "What do monkeys do?",
    "What do reindeer have?",
]


def test_print_retrieval_results():
    retriever = get_retriever()

    for question in EVALUATION_QUESTIONS:
        print("\n" + "=" * 70)
        print(f"QUESTION: {question}")
        print("=" * 70)

        documents = retriever.invoke(question)

        print(f"DOCUMENTS RETRIEVED: {len(documents)}")

        for index, document in enumerate(documents, start=1):
            print(f"\n--- RESULT {index} ---")
            print("METADATA:", document.metadata)
            print("CONTENT:", document.page_content[:500])

    assert True
