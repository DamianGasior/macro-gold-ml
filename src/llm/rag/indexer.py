import logging
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from src.llm.rag.scraper import scrape_site, URLS

load_dotenv()

logger = logging.getLogger(__name__)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Model embeddingów — mały, tani, wystarczający do RAG
EMBEDDING_MODEL = "text-embedding-3-small"

# Folder na dysku gdzie ChromaDB zapisze swoją bazę
CHROMA_PATH = "src/llm/rag/chroma_db"


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Wysyła listę tekstów do OpenAI i zwraca listę wektorów (embeddingów)."""
    client = OpenAI()
    logger.info(f"Tworzę embeddingi dla {len(texts)} chunków...")

    # OpenAI przyjmuje całą listę tekstów naraz — jedno wywołanie API dla wszystkich chunków
    response = client.embeddings.create(
        input=texts,
        model=EMBEDDING_MODEL,
    )

    # Wyciągamy same wektory z odpowiedzi — response.data to lista obiektów, każdy ma .embedding
    # embeddings = [item.embedding for item in response.data]
    embeddings = []  # stwórz pustą listę
    logger.info(f"response.data to {response.data}")
    for item in response.data:  # przejdź po każdym elemencie
        # logger.info(f"item to {item}")
        logger.info(f"item_details  to {dir(item)}")
        logger.info(f"item.embedding to {item.embedding}")
        embeddings.append(item.embedding)  # weź tylko .embedding i dodaj
    logger.info(f"Otrzymano {len(embeddings)} wektorów, każdy ma {len(embeddings[0])} wymiarów")
    return embeddings


def save_to_chroma(chunks: list[dict], collection_name: str) -> None:
    """Zapisuje chunki z embeddingami do ChromaDB na dysku."""

    # PersistentClient = ChromaDB zapisuje dane na dysk (nie gubi przy restarcie)
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Kolekcja = odpowiednik tabeli w SQL — tu trzymamy wszystkie chunki
    # get_or_create = weź istniejącą lub utwórz nową
    collection = client.get_or_create_collection(name=collection_name)
    logger.info(f"Chunks to {chunks}")
    logger.info(f"Dlugosc Chunks to {len(chunks)}")

    # Przygotuj dane do zapisu — ChromaDB potrzebuje 4 rzeczy:

    # 1. Same teksty
    texts = []
    for chunk in chunks:
        texts.append(chunk["text"])
    logger.info(f"Texts  to {texts}")

    # 2. Wektory dla każdego tekstu
    embeddings = get_embeddings(texts)
    logger.info(f"embeddings  to {embeddings}")

    # 3. Metadane — skąd pochodzi każdy chunk
    metadatas = []
    for chunk in chunks:
        metadata = {"source": chunk["source"], "chunk_index": chunk["chunk_index"]}
        metadatas.append(metadata)

    # 4. Unikalny ID każdego chunka
    ids = []
    for chunk in chunks:
        chunk_id = f"{chunk['source']}_{chunk['chunk_index']}"
        ids.append(chunk_id)

    # Zapisz do ChromaDB
    # upsert = dodaj jeśli nie ma, zaktualizuj jeśli już istnieje (bezpieczne przy re-indeksowaniu)
    collection.upsert(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )
    logger.info(f"Zapisano {len(chunks)} chunków do kolekcji '{collection_name}'")
    logger.info(f"Zapisano collection:  '{collection}'")


def index_site(url: str, max_articles: int) -> None:
    """Główna funkcja: scraping → embeddingi → ChromaDB."""
    logger.info(f"Indeksuję: {url}")

    # Krok 1: pobierz chunki ze scrapera
    chunks = scrape_site(url, max_articles=max_articles)

    if not chunks:
        logger.warning(f"Brak chunków dla: {url}")
        return

    logger.info(f"Pobrano {len(chunks)} chunków, zaczynam indeksowanie...")

    url_ending = url.rsplit("/", 1)[-1]
    print(url_ending)
    print(type(url_ending))
    # Krok 2 + 3: embeddingi → ChromaDB (wszystko w save_to_chroma)
    save_to_chroma(chunks, url_ending)
    logger.info("Indeksowanie zakończone ✅")


def index_side_chunks(chunks):
    logger.info(f"Pobrano {len(chunks)} chunków, zaczynam indeksowanie...")
    for url in URLS:
        url_ending = url.rsplit("/", 1)[-1]
        logger.info(f"url_ending is : {url_ending}")
        logger.info(f"type url_ending is : {type(url_ending)}")
        # Krok 2 + 3: embeddingi → ChromaDB (wszystko w save_to_chroma)
        save_to_chroma(chunks, url_ending)
        logger.info("Indeksowanie zakończone ✅")


if __name__ == "__main__":
    from src.logging_config import setup_logging

    setup_logging(level=logging.INFO)

    # index_site(
    #     url="https://simplevisorinsights.com/daily-update",
    #     max_articles=2,
    # )

    urls = [
        "https://simplevisorinsights.com/daily-update",
        "https://www.home.saxo/insights/news-and-research/macro",
        "https://www.home.saxo/insights/news-and-research/commodities",
        "https://www.home.saxo/insights/news-and-research/bonds",
    ]

    for url in urls:
        index_site(url, max_articles=5)
