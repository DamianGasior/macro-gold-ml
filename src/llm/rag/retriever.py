import logging
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Ten sam model co przy indeksowaniu — MUSI być identyczny, inaczej wektory są nieporównywalne
EMBEDDING_MODEL = "text-embedding-3-small"
CHROMA_PATH = "src/llm/rag/chroma_db"


def embed_query(question: str) -> list[float]:
    """Zamienia pytanie na wektor — dokładnie tak samo jak chunki przy indeksowaniu."""
    client = OpenAI()
    response = client.embeddings.create(
        input=[question],
        model=EMBEDDING_MODEL,
    )
    # Jedno pytanie → jeden obiekt w response.data → bierzemy [0]
    # logger.info(f"odpowiedz to  {response.data[0].embedding})")
    return response.data[0].embedding


def search(question: str, n_results: int = 3, collection_name: str | None = None) -> list[dict]:
    """
    Szuka chunków podobnych do pytania w ChromaDB.

    collection_name=None  → przeszukuje wszystkie kolekcje naraz
    collection_name="macro" → szuka tylko w tej jednej kolekcji
    """
    logger.info(f"Szukam: '{question}' (top {n_results})")

    # Krok 1: zamień pytanie na wektor
    query_vector = embed_query(question)

    # Krok 2: otwórz bazę i wybierz kolekcje do przeszukania
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

    if collection_name:
        collections = [chroma_client.get_collection(collection_name)]
    else:
        # list_collections() zwraca wszystkie kolekcje w tej bazie
        collections = chroma_client.list_collections()

    logger.info(f"Przeszukuję {len(collections)} kolekcji: {[c.name for c in collections]}")

    results = []

    # Krok 3: odpytaj każdą kolekcję
    for collection in collections:
        logger.info(f"Szukam: {collection}")
        count = collection.count()
        if count == 0:
            continue

        # n_results nie może być większy niż liczba chunków w kolekcji
        actual_n = min(n_results, count)

        response = collection.query(
            query_embeddings=[query_vector],
            n_results=actual_n,
            include=["documents", "metadatas", "distances"],
        )

        logger.info(f"response type: {type(response)}")
        logger.info(f"response is: {response}")

        # response["documents"][0] — lista tekstów dla pierwszego (jedynego) zapytania
        for text, metadata, distance in zip(
            response["documents"][0],
            response["metadatas"][0],
            response["distances"][0],
        ):
            results.append(
                {
                    "text": text,
                    "source": metadata["source"],
                    "chunk_index": metadata["chunk_index"],
                    "collection": collection.name,
                    "distance": round(distance, 4),
                }
            )

            logger.info(f"results to: {results}")

    # Krok 4: posortuj wszystkie wyniki po odległości — mniejsza = bardziej podobny
    results.sort(key=lambda x: x["distance"])

    logger.info(f"Znaleziono {len(results)} wyników, zwracam top {n_results}")
    return results[:n_results]


def format_context(chunks: list[dict]) -> str:
    """
    Formatuje chunki jako jeden blok tekstu gotowy do wklejenia w prompt LLM.
    Każdy chunk dostaje nagłówek ze źródłem żeby LLM wiedział skąd pochodzi informacja.
    """
    if not chunks:
        return "Brak dostępnego kontekstu z artykułów."

    context_parts = []
    for i, chunk in enumerate(chunks, start=1):
        header = f"[Artykuł {i} | źródło: {chunk['source']} | odległość: {chunk['distance']}]"
        context_parts.append(f"{header}\n{chunk['text']}")

    return "\n\n---\n\n".join(context_parts)


if __name__ == "__main__":
    from src.logging_config import setup_logging

    setup_logging(level=logging.INFO)

    test_questions = [
        "What is the outlook for gold prices?",
        "How does Federal Reserve policy affect commodities?",
        "What are the risks for bond markets?",
    ]

    for question in test_questions:
        print(f"\n{'=' * 60}")
        print(f"PYTANIE: {question}")
        print("=" * 60)

        chunks = search(question, n_results=3)

        for chunk in chunks:
            print(f"\n  Kolekcja: {chunk['collection']}")
            print(f"  Odległość: {chunk['distance']}")
            print(f"  Źródło: {chunk['source']}")
            print(f"  Tekst: {chunk['text'][:200]}...")

        print("\n--- SFORMATOWANY KONTEKST DLA LLM ---")
        print(format_context(chunks))
