import requests
from bs4 import BeautifulSoup
import logging
import trafilatura
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

CHUNK_SIZE = 400  # słowa na chunk

# Saxo renderuje strony listingowe przez JavaScript, więc używamy sitemapa XML zamiast scrape'ować HTML.
# Klucz: URL strony listingowej → kategoria w sitemapie
SAXO_SITEMAP_URL = "https://www.home.saxo/article-sitemap-en-1.xml"
SAXO_CATEGORY_MAP = {
    "https://www.home.saxo/insights/news-and-research/macro": "macro",
    "https://www.home.saxo/insights/news-and-research/commodities": "commodities",
    "https://www.home.saxo/insights/news-and-research/bonds": "bonds",
}


def fetch_saxo_article_links(category: str) -> list[str]:
    """Pobiera linki do artykułów Saxo z sitemapy XML (strony listingowe wymagają JS)."""
    logger.info(f"Pobieram linki Saxo z sitemapy dla kategorii: {category}")
    try:
        response = requests.get(SAXO_SITEMAP_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning(f"Nie udało się pobrać sitemapa Saxo: {e}")
        return []

    root = ET.fromstring(response.content)
    logger.debug(f"root is: {root}")
    # logger.debug(f"response.content is: {response.content}")

    ns = {"sm": "https://www.sitemaps.org/schemas/sitemap/0.9"}
    category_path = f"/content/articles/{category}/"

    links = []
    for loc in root.findall(".//sm:loc", ns):  # 1. tworzy loc
        logger.debug(f"loc.text is: {loc.text}")
        if loc.text and category_path in loc.text:  # 2. filtruje
            logger.debug(f"loc.text is: {loc.text}")
            links.append(loc.text)  # 3. zbiera wynik

    logger.info(f"Znaleziono {len(links)} artykułów Saxo dla kategorii '{category}'")
    return links


def fetch_article_links(index_url: str) -> list[str]:
    """Wchodzi na stronę z listą artykułów i zbiera linki do pojedynczych artykułów."""
    # Saxo wymaga JS do wyrenderowania listy artykułów — używamy sitemapy zamiast HTML
    if index_url in SAXO_CATEGORY_MAP:
        return fetch_saxo_article_links(SAXO_CATEGORY_MAP[index_url])

    logger.info(f"Pobieram linki z: {index_url}")
    response = requests.get(index_url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    # logger.debug(f"Odpowiedz to : {response}")
    soup = BeautifulSoup(response.text, "html.parser")
    logger.debug(f"Soup to : {soup}")
    logger.debug(f"Odpowiedz to : {response.text}")
    # Uderz bezpośrednio w sekcję artykułów — tylko linki z div.article-text-link
    article_tags = soup.select("div.article-text-link a")
    logger.debug(f"article_tags type : {type(article_tags)}")
    logger.debug(f"article_tags to : {article_tags}")
    links = []
    for tag in article_tags:
        if tag.get("href"):  # tylko jeśli href istnieje
            links.append(tag["href"])

    # Usuń duplikaty zachowując kolejność
    unique_links = list(dict.fromkeys(links))
    logger.info(f"Znaleziono {len(unique_links)} linków na stronie")
    logger.info(f"Linki to : {unique_links}")

    return unique_links


# commenting out at the moment this implementation, will replace it with trafilatura method

# def fetch_article_text(url: str) -> str:
#     """Pobiera tekst artykułu z podanego URL."""
#     logger.debug(f"Pobieram artykuł: {url}")
#     try:
#         response = requests.get(url, headers=HEADERS, timeout=10)
#         response.raise_for_status()
#     except requests.RequestException as e:
#         logger.warning(f"Nie udało się pobrać {url}: {e}")
#         return ""

#     soup = BeautifulSoup(response.text, "html.parser") # co to znaczy ? html.parser ?
#     logger.debug(f"Article_text to : {soup}")
#     # Usuń tagi które nie są treścią: menu, stopka, skrypty
#     for tag in soup(["script", "style", "nav", "footer", "header"]):
#         tag.decompose()

#     # Szukaj głównej treści artykułu — od najbardziej szczegółowego do ogólnego
#     for selector in ["article", "main", "div.content", "div.article", "body"]:
#         element = soup.select_one(selector) # co to jest select one metoda ?
#         if element:
#             text = element.get_text(separator=" ", strip=True)
#             if len(text) > 200:  # pomiń strony z za małą treścią
#                 return text

#     return ""


def fetch_article_text(url: str) -> str:
    logger.debug(f"Pobieram artykuł: {url}")

    # Krok 1: pobierz stronę
    downloaded = trafilatura.fetch_url(url)

    # Krok 2: wyciągnij tylko tekst artykułu
    text = trafilatura.extract(downloaded)
    logger.debug(f"Downloaded text id: {text}")

    if text:
        logger.debug(f"Pierwsze 500 znaków:\n{'-' * 40}")
        logger.debug(text[:500])
    else:
        logger.debug("BRAK TEKSTU — trafilatura nie poradziła sobie z tą stroną")
    return text or ""


def split_into_chunks(text: str, source_url: str) -> list[dict]:
    """Kroi tekst na chunki po ~CHUNK_SIZE słów. Zwraca listę słowników z tekstem i metadanymi."""
    OVERLAP = 100
    boundary_chunk = (
        CHUNK_SIZE - OVERLAP
    )  # this is to address the problem of ending the information in one chunk and being continued in the following one
    words = text.split()
    chunks = []

    for chunk_index, i in enumerate(range(0, len(words), boundary_chunk)):
        chunk_words = words[i : i + CHUNK_SIZE]
        chunk_text = " ".join(chunk_words)
        chunks.append(
            {
                "text": chunk_text,
                "source": source_url,
                "chunk_index": chunk_index,
            }
        )

    logger.debug(f"Pociąłem na {len(chunks)} chunków: {source_url}")
    return chunks


def scrape_site(index_url: str, max_articles: int = 5) -> list[dict]:
    """Główna funkcja: wchodzi na stronę, zbiera artykuły, kroi na chunki."""
    all_chunks = []

    article_links = fetch_article_links(index_url)

    # Ogranicz liczbę artykułów — im więcej chunków, tym więcej wywołań embedding API w indexer.py
    for url in article_links[:max_articles]:
        text = fetch_article_text(url)
        if text:
            chunks = split_into_chunks(text, source_url=url)
            all_chunks.extend(chunks)

    logger.debug(f"Łącznie chunków ze strony {index_url}: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    from src.logging_config import setup_logging

    setup_logging(level=logging.DEBUG)

    urls = [
        "https://simplevisorinsights.com/daily-update",
        "https://www.home.saxo/insights/news-and-research/macro",
        "https://www.home.saxo/insights/news-and-research/commodities",
        "https://www.home.saxo/insights/news-and-research/bonds",
    ]

    for url in urls:
        logger.debug(f"\n{'=' * 60}")
        logger.debug(f"Testuję: {url}")
        chunks = scrape_site(url, max_articles=2)
        if chunks:
            logger.debug("Pierwszy chunk (pierwsze 300 znaków):")
            logger.debug(chunks[0]["text"][:300])
        else:
            logger.debug("BRAK TREŚCI")
