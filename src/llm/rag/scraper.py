import json
import urllib.parse
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

# Gold.org ukrywa Algolię za proxy, ale przy przewijaniu strony wysyła bezpośrednie zapytania
# do Algolia API z publicznym kluczem read-only (search-only key — bezpieczny).
GOLD_ORG_BASE_URL = "https://www.gold.org"
GOLD_ORG_RESEARCH_URL = "https://www.gold.org/goldhub/research/library"
ALGOLIA_ENDPOINT = "https://ic5o1qhija-dsn.algolia.net/1/indexes/*/queries"
ALGOLIA_APP_ID = "IC5O1QHIJA"
ALGOLIA_SEARCH_KEY = "a53dfaac4daa2df77914a57de3fb4e84"
ALGOLIA_INDEX = "goldorg2_research_prod_en"

# Dostępne topics: Gold Market structure and trends, Investment commentary, Central banks, ESG.
# Domyślnie bierzemy wszystkie poza ESG.
GOLD_ORG_DEFAULT_TOPICS = [
    "Gold Market structure and trends",
    "Investment commentary",
    "Central banks",
]

# Dostępne kolekcje: Gold Market Commentary, Gold ETF Flows, Outlook,
# Weekly Markets Monitor, Gold Demand Trends, Case for Gold, Blogs, Gold Market Primers, Central Banks Survey.
# Domyślnie pusty — filtrujemy tylko po topics, nie ograniczamy kolekcji.
GOLD_ORG_DEFAULT_COLLECTIONS: list[str] = []


def fetch_gold_org_article_links(
    collections: list[str] | None = None,
    topics: list[str] | None = None,
) -> list[str]:
    """Pobiera linki do artykułów gold.org przez Algolia API.

    collections: lista kolekcji (OR między nimi). None = GOLD_ORG_DEFAULT_COLLECTIONS (brak filtra).
                 Przykład: ["Gold Market Commentary", "Outlook"]
    topics:      lista topics (OR między nimi). None = GOLD_ORG_DEFAULT_TOPICS (wszystkie poza ESG).
                 Przykład: ["Central banks", "Investment commentary"]
    Oba filtry łączone są przez AND — artykuł musi pasować do obu.
    Przekaż [] dla dowolnego parametru żeby wyłączyć ten filtr.
    """
    if collections is None:
        collections = GOLD_ORG_DEFAULT_COLLECTIONS
    if topics is None:
        topics = GOLD_ORG_DEFAULT_TOPICS

    algolia_headers = {
        "x-algolia-api-key": ALGOLIA_SEARCH_KEY,
        "x-algolia-application-id": ALGOLIA_APP_ID,
        "Content-Type": "application/json",
    }

    # facetFilters: każdy element to warunek AND.
    # Element będący listą = OR między jego wartościami.
    # Przykład: [["topics:A","topics:B"], "language_text:English"]
    # → (topic A LUB B) AND język angielski
    facet_filters: list = ["language_text:English"]
    if collections:
        facet_filters.append([f"collections:{c}" for c in collections])
    if topics:
        facet_filters.append([f"topics:{t}" for t in topics])

    hits_per_page = 100
    page = 0
    all_urls = []

    # Algolia multi-query API wymaga żeby params był URL-encoded stringiem,
    # a zagnieżdżone listy (facetFilters) muszą być wcześniej JSON-encoded.
    attributes_to_retrieve = ["url", "title", "publication_date_display"]
    params_template = {
        "facetFilters": json.dumps(facet_filters),
        "attributesToRetrieve": json.dumps(attributes_to_retrieve),
    }

    while True:
        params_str = urllib.parse.urlencode(
            {
                **params_template,
                "hitsPerPage": hits_per_page,
                "page": page,
            }
        )
        body = {
            "requests": [
                {
                    "indexName": ALGOLIA_INDEX,
                    "params": params_str,
                }
            ]
        }

        try:
            response = requests.post(
                ALGOLIA_ENDPOINT, headers=algolia_headers, json=body, timeout=10
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Błąd Algolia API (strona {page}): {e}")
            break

        data = response.json()
        results = data.get("results", [{}])[0]
        hits = results.get("hits", [])
        nb_pages = results.get("nbPages", 0)

        for hit in hits:
            relative_url = hit.get("url", "")
            if relative_url:
                all_urls.append(f"{GOLD_ORG_BASE_URL}{relative_url}")

        logger.info(
            f"Gold.org Algolia: strona {page + 1}/{nb_pages}, zebrano {len(all_urls)} linków"
        )

        page += 1
        if page >= nb_pages:
            break

    logger.info(
        f"Znaleziono łącznie {len(all_urls)} artykułów gold.org "
        f"(topics: {topics or 'wszystkie'}, collections: {collections or 'wszystkie'})"
    )
    return all_urls


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

    # Gold.org używa Algolia — pobieramy linki bezpośrednio przez API
    if index_url == GOLD_ORG_RESEARCH_URL:
        return fetch_gold_org_article_links()

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

    downloaded = trafilatura.fetch_url(url)

    # favor_precision=True odrzuca stopki, disclaimery i bloki nawigacyjne —
    # trafilatura wybiera tylko tekst o wysokiej pewności że to treść artykułu.
    text = trafilatura.extract(downloaded, favor_precision=True)

    if text:
        logger.debug(f"Pierwsze 500 znaków:\n{'-' * 40}")
        logger.debug(text[:500])
    else:
        logger.warning(f"BRAK TEKSTU — artykuł prawdopodobnie za paywallem lub wymaga JS: {url}")
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
        GOLD_ORG_RESEARCH_URL,
    ]

    for url in urls:
        logger.debug(f"\n{'=' * 60}")
        logger.debug(f"Testuję: {url}")
        chunks = scrape_site(url, max_articles=5)
        if chunks:
            logger.debug("Pierwszy chunk (pierwsze 300 znaków):")
            logger.debug(chunks[0]["text"][:300])
        else:
            logger.debug("BRAK TREŚCI")
