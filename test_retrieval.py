from app.ai.retrieval.retriever import Retriever


def main() -> None:
    retriever = Retriever()
    results = retriever.retrieve("What language is used for AI?")
    print(results)


if __name__ == "__main__":
    main()
