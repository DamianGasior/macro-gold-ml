# LEARNING CONTEXT — AI Engineer journey (Damian Gasior)

> Ten plik jest przeznaczony dla Claude.ai na urlopie (telefon, brak IDE).
> GitHub connector odczytuje go przy każdym pytaniu. Po powrocie z urlopu
> zaktualizuj lokalnie `claude_ai_engineer_checklist.md` i `memory/quiz_schedule.md`.

---

## Kim jestem

Damian Gasior. 15 lat w bankowości — 7 lat operacje, 8 lat Product Manager / Biznes Analityk w dużym międzynarodowym banku. Uczę się Pythona i ML od ~8 miesięcy. **Cel: praca jako AI Engineer w fintech/banku.**

**Mój poziom:**
- Python: dobry początkujący, możliwe luki w fundamentach
- ML: podstawy, projekt LGBM na danych finansowych (złoto)
- FastAPI, Docker, Azure, RAG — już zaimplementowane w projekcie (patrz niżej)
- LangChain, Kubernetes, Kafka, NoSQL — nie znam

**Strategiczna przewaga:** rozumiem domenę finansową + buduję realny projekt ML na danych rynkowych.

---

## Jak chcę żebyś mi pomagał

- Mów do mnie **po polsku**
- Tłumacz od ogółu do szczegółu — najpierw "po co", potem "jak"
- Używaj analogii z życia codziennego
- Przy nowym pojęciu: 1 konkretny przykład z ML
- Jeśli pytam o teorię — pokaż też kod (prosty najpierw)
- **Tryb mentora:** po każdym wytłumaczeniu daj 1 zadanie do samodzielnego wykonania
- Gdy wklejam kod — zrób code review: co działa, co poprawić i dlaczego
- Jeśli popełniam błąd — naprowadź pytaniem, nie poprawiaj od razu
- Uzupełniaj luki w podstawach PRZY OKAZJI — nie zatrzymujemy się na osobny kurs

---

## Stan projektu (na 2026-06-07)

Projekt: `macro-gold-ml` — model LGBM przewidujący kierunek ceny złota (long/short/no trade).

**Zbudowane:**
- ✅ LGBM classifier — walk-forward 5 foldów, zapisany jako `lgbm_classifier.pkl`
- ✅ FastAPI — GET /health, POST /predict (model), POST /post/chat (LLM + RAG)
- ✅ Docker — Dockerfile, image `damgas712/gold-api:latest` na Docker Hub
- ✅ Azure ACI — deploy działa, scheduled start/stop (8:30-23:30 CEST, pon-pt)
- ✅ GitHub Actions — CI/CD: push na main → build → push Docker Hub → redeploy ACI
- ✅ RAG pipeline — scraper.py + indexer.py (ChromaDB) + retriever.py
  - Źródła: simplevisorinsights.com (statyczna), Saxo (sitemap XML), gold.org (Algolia API)
  - gold.org: ~1000 artykułów przez Algolia REST API, filtr topics bez ESG
- ✅ LLM integracja — GPT-4o-mini analizuje sygnał LGBM + artykuły z RAG
- ✅ Frontend — `static/index.html` serwowany przez FastAPI

**Następny krok po urlopie:**
- FastAPI startup event (`@app.on_event("startup")`) — indexer gold.org + pre-warm cache przy starcie kontenera

---

## ZALEGŁE QUIZY — zrób te najpierw!

> Poniższe tematy mają przekroczone `next_due`. Zacznij od nich zanim przejdziemy do nowego materiału.

### 1. Docker (next_due: 2026-06-01 — ZALEGŁY)
1. Jaka jest różnica między `docker build` a `docker run`?
2. Dlaczego w Dockerfile kopiujemy `requirements.txt` PRZED kodem aplikacji?
3. Co robi flaga `-p 8000:8000` w `docker run -p 8000:8000 gold-api`?
4. Czy obraz (image) może sam przyjmować requesty HTTP bez `docker run`?
5. Co się stanie z obrazem jeśli kontener crashuje na Azure?

### 2. FastAPI — model poza endpointem (next_due: 2026-06-02 — ZALEGŁY)
1. Dlaczego `joblib.load()` ładujemy poza funkcją endpointu, a nie wewnątrz?
2. Jaki wzorzec łączy `joblib.load` poza endpointem z cache'owaniem odpowiedzi API?

### 3. Embeddingi — teoria (next_due: 2026-06-02 — ZALEGŁY, ostatni wynik: 60%)
1. Co to list comprehension? Przepisz `[item.embedding for item in response.data]` jako klasyczną pętlę for.
2. Dlaczego nie podajemy całego dokumentu jako jednego embeddingu zamiast kroić na chunki? (dwa powody)
3. Dlaczego modele embeddingowe mają limit tokenów — jaka jest matematyczna przyczyna?
4. Co to token? Czy token = słowo? Podaj przykład tokenizacji.
5. Ile liczb ma wektor `text-embedding-3-small`?
6. Na czym polega agregacja (mean pooling) — jak z N wektorów tokenów powstaje 1 wektor chunka?
7. Jaki jest zakres wartości w wektorze embeddingowym i dlaczego?
8. Co to cosine similarity — co oznacza 0.0, 1.0, -1.0?
9. Jakim mechanizmem uczono modele embeddingowe? Co to Masked Language Model?
10. Czy wymiar_42 wektora odpowiada konkretnemu słowu lub pojęciu?

### 4. Web scraping + RAG chunking + sitemap XML (next_due: 2026-06-02 — ZALEGŁY, ostatni wynik: 64%)
1. Co to CSS selector i co zwraca `soup.select("div.article-text-link a")`?
2. Jaka różnica między stroną statyczną a dynamiczną (JS-rendered)? Jak Python `requests` radzi sobie z każdą?
3. Dlaczego kroimy tekst na chunki zamiast podać cały artykuł do LLM?
4. Co to overlapping chunks i jaki problem rozwiązują?
5. Co robi `tag.decompose()` w BeautifulSoup?
6. Jaka różnica między `soup.select()` a `soup.select_one()`?
7. Co znaczy `max_articles: int = 5` w sygnaturze funkcji — kiedy użyje wartości 5?
8. Co to sitemap XML i kto go tworzy?
9. Dlaczego sitemap rozwiązał problem z JS-rendered listing page, skoro artykuły też są na tej samej domenie?

### 5. HTTP headers — User-Agent (next_due: 2026-06-01 — ZALEGŁY, bez quizu)
1. Co to HTTP header i czemu służy w zapytaniu GET?
2. Co to `User-Agent` — jaką informację przekazuje serwerowi?
3. Dlaczego serwer może zablokować zapytanie bez `User-Agent`?
4. Jak przekazujesz własne headers do `requests.get()`? Pokaż składnię.
5. Czy wszystkie strony wymagają podrobionego `User-Agent`?

---

## Quizy aktualne (nie zaległe)

### GitHub Actions / Azure secrets (next_due: 2026-06-09, ostatni wynik: 90%)
1. Opisz cały łańcuch: jak wartość z GitHub Secrets trafia do `os.getenv()` w kontenerze na Azure?
2. Co robi `load_dotenv()` gdy nie ma pliku `.env`? Czy crashuje?
3. Dlaczego `python-dotenv` musi być w `requirements.txt` nawet jeśli na Azure `.env` nie istnieje?
4. Czy zatrzymanie i ponowne uruchomienie kontenera ACI czyści zmienne środowiskowe?
5. Co się stanie jeśli zainstalujesz pakiet lokalnie ale nie zrobisz `pip freeze > requirements.txt`?

### Python logging (next_due: 2026-06-11, ostatni wynik: 70%)
1. Dlaczego `logging.basicConfig()` może być ignorowane?
2. Co się stanie gdy dwa moduły wywołają `basicConfig()` — który wygra?
3. Jaka różnica między `logging.info()` a `logger.info()`?
4. Jak wyciszy się logi konkretnej biblioteki (np. OpenAI) nie ruszając reszty?
5. Gdzie powinna być wywołana `setup_logging()` — w każdym pliku czy tylko raz?
6. Co to root logger i jak inne loggery go dziedziczą?
7. Jeśli root logger ma DEBUG a konkretny moduł ustawi INFO — co się pokaże?

### OOP — @property, class hierarchy (next_due: 2026-06-14, ostatni wynik: 80%)
1. Co się stanie gdy zrobię `pies.age = -5` na klasie bez `@property`, ale z walidacją w `__init__`?
2. Kiedy `@property` daje przewagę nad walidacją w `__init__`?
3. Jaka różnica między klasą a instancją?
4. Co to method overriding i polimorfizm?
5. Czy `List[str]` rzuci błąd gdy przekażę `[1, 2, 3]`?

### Type hints (next_due: 2026-06-14, ostatni wynik: 80%)
1. Czy Python sprawdza type hints w runtime?
2. Jak zapisać "funkcja może zwrócić float albo None"?
3. Z czego importujesz `List`, `Optional`, `Dict`?
4. Jaka różnica między type hint a walidacją?
5. Czy `def foo(x: int)` rzuci błąd gdy wywołasz `foo("hello")`?

### DevTools Network tab + Algolia API (next_due: 2026-06-14, bez quizu)
1. Co to zakładka Network w DevTools i do czego jej używamy?
2. Co to różnica między Fetch/XHR a resztą requestów?
3. Dlaczego `requests.get()` nie widzi artykułów na JS-rendered stronie?
4. Czym jest Algolia i dlaczego jej klucz może być publicznie widoczny?
5. Co to "search-only API key" — dlaczego nie jest niebezpieczny?
6. W Algolia `facetFilters=[["topics:A","topics:B"],"language:English"]` — co tu AND a co OR?
7. Dlaczego Algolia multi-query API wymaga URL-encoded string jako `params`, a nie słownika?
8. Co to `urllib.parse.urlencode()` i kiedy jest potrzebne?
9. Czym różni się podejście sitemap XML od Algolia API — kiedy które stosujesz?
10. Co to `favor_precision=True` w trafilatura i jaki problem rozwiązuje?

### OOP — dot notation, klasy SDK (next_due: 2026-06-21, ostatni wynik: 85%)
1. Dlaczego `response.choices[0]` a nie `response.choices`?
2. Jaka różnica między atrybutem który jest listą a atrybutem który jest pojedynczym obiektem?
3. Co to "dot notation" i jak się ma do OOP?
4. Skąd wiesz jakiego typu jest atrybut klasy którą dostajesz z zewnętrznej biblioteki?

---

## Tematy do nauki (teoria — dobre na urlop)

Na urlopie bez IDE — dobry czas na teorię, którą potem wdrożysz po powrocie:

1. **MLflow** — co to experiment tracking, po co `log_param` vs `log_metric` vs `log_artifact`
2. **LangChain basics** — po co frameworki RAG, co robi `LLMChain`, `RetrievalQA`
3. **LeetCode teoria** — tablice, słowniki, złożoność O(n) — bez kodowania, sam pomysł
4. **Pinecone** — czym różni się od ChromaDB, kiedy przejść na cloud vector DB
5. **Azure OpenAI vs OpenAI API** — dlaczego banki używają Azure OpenAI, co się zmienia w SDK
6. **Concept drift** — co to, jak wykryć, po co monitoring ML na produkcji

---

## Instrukcja dla Claude.ai na urlopie

**Jak robić quizy:**
1. Powiedz "zrób quiz z [tematu]" — Claude zadaje pytania jedno po jednym
2. Odpowiadasz — Claude ocenia, naprowadza jeśli błąd, nie podaje od razu odpowiedzi
3. Po quizie: wynik X/Y, lista luk, sugerowany next_due
4. Zanotuj wynik — po powrocie zaktualizuj quiz_schedule.md lokalnie

**Jak zadawać pytania o teorię:**
- "Wytłumacz mi X" → tłumaczenie + przykład + zadanie do samodzielnego wykonania
- "Porównaj X i Y" → analogia + kiedy co stosować
- "Jak działa X w projekcie gold-ml?" → konkretny przykład z kodu projektu

**Czego NIE robimy na urlopie:**
- Nie piszemy kodu (brak IDE)
- Nie zmieniamy plików projektu
- Nie deployujemy niczego

**Po powrocie:**
- Zaktualizuj `quiz_schedule.md` z wynikami quizów z urlopu
- Zaktualizuj `claude_ai_engineer_checklist.md`
- Następny krok w kodzie: FastAPI startup event

---

## Legenda wyników quizów

| Wynik | Interwał do następnego quizu |
|-------|------------------------------|
| ≤ 40% | +2 dni |
| 41–70% | +7 dni |
| > 70% | +21 dni |
