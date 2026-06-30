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

### 1. Docker (next_due: 2026-06-17 — ZALEGŁY, ostatni wynik: 38%)
1. Jaka jest różnica między `docker build` a `docker run`?
2. Dlaczego w Dockerfile kopiujemy `requirements.txt` PRZED kodem aplikacji?
3. Co robi flaga `-p 8000:8000` w `docker run -p 8000:8000 gold-api`?
4. Czy obraz (image) może sam przyjmować requesty HTTP bez `docker run`?
5. Co się stanie z obrazem jeśli kontener crashuje na Azure?

UWAGA: quiz zdany 5/5 w maju, ale 2026-06-13 wynik spadł do ~38% — wiedza wyparowała bez powtórki.

Luki do poprawy (2026-06-13):
- build vs run: build (z Dockerfile) tworzy OBRAZ = zamrożony szablon, nic nie działa.
  run tworzy z obrazu KONTENER = żywą instancję, dopiero tu startuje apka. 1 obraz → wiele kontenerów.
- requirements PRZED kodem: chodzi o CACHE WARSTW, nie o "potrzebne moduły". Każda linia Dockerfile
  = warstwa, Docker cache'uje niezmienione warstwy. requirements (rzadko zmienne) na górze —
  zmiana kodu nie unieważnia ciężkiej warstwy pip install. Zasada: rzadko zmienne na górę, często na dół.
- -p 8000:8000 = port mapping. Lewa = port HOSTA, prawa = port w KONTENERZE. NIE muszą być równe
  (-p 9000:8000 OK). Przebija tunel do izolowanego kontenera.
- Obraz a HTTP: NIE może przyjmować requestów — to martwy plik, żaden proces nie żyje.
  Tylko KONTENER (z uruchomionym uvicorn) nasłuchuje na porcie.
- Crash a obraz: obraz ZOSTAJE nienaruszony (odwrotnie niż myślałem). Crash zabija instancję,
  szablon leży nietkniętym — ACI bierze ten sam obraz i odpala nowy kontener. Obraz = źródło prawdy.

---

## Quizy aktualne (nie zaległe)

### HTTP headers — User-Agent (next_due: 2026-06-17, PRZEROBIONY TEORETYCZNIE — bez quizu)
1. Co to HTTP header i czemu służy w zapytaniu GET?
2. Co to `User-Agent` — jaką informację przekazuje serwerowi?
3. Dlaczego serwer może zablokować zapytanie bez `User-Agent`?
4. Jak przekazujesz własne headers do `requests.get()`? Pokaż składnię.
5. Czy wszystkie strony wymagają podrobionego `User-Agent`?

2026-06-13: Damian nie umiał odpowiedzieć, więc materiał WYŁOŻONY (nie odpytany) — brak wyniku %.
Do realnego quizu ~2026-06-17 (razem z powtórką Dockera). Notatki:
- HTTP header = para klucz-wartość z metadanymi O zapytaniu (kto pyta, jakim narzędziem, jaki język/
  format). "Koperta z adnotacjami" wokół właściwego żądania. Serwer czyta headers zanim odpowie.
- User-Agent = nagłówek mówiący CZYM jest klient (przeglądarka/system/wersja). requests domyślnie wysyła
  "python-requests/2.31.0" — serwer od razu widzi, że to skrypt, nie człowiek.
- Blokada: serwery broniące się przed botami widzą python-requests lub brak UA — 403 / pusta strona /
  captcha. Podstawiasz UA przeglądarki, by request wyglądał jak ruch człowieka.
- Składnia: headers = {"User-Agent": "Mozilla/5.0 ..."}; requests.get(url, headers=headers).
  Słownik, można dodać więcej (np. "Accept-Language": "en-US").
- NIE każda strona wymaga: wiele (zwł. statycznych/przyjaznych) odda treść bez sztuczek. UA podstawiasz
  tylko gdy serwer filtruje boty. Praktyka: najpierw bez, przy 403/pustce dorzuć nagłówek. Kwestia etykiety
  (robots.txt) — udawanie przeglądarki bywa w szarej strefie.

### Web scraping + RAG chunking + sitemap XML (next_due: 2026-07-04, ostatni wynik: 72%)

Quiz 9 pytań, dokończony 2026-06-13 (skok z 64% → 72%). Druga połowa znacznie lepsza niż pierwsza.

Wyniki:
- P1 (CSS selector): ⚠️ selektor wybiera ELEMENTY HTML (tagi), NIE tekst. `div.article-text-link a`
  = wszystkie <a> WEWNĄTRZ diva o klasie article-text-link (spacja = potomek). Zwraca listę <a>.
- P2 (statyczna vs dynamiczna): ⚠️ SEDNO: requests.get() pobiera HTML ale NIE wykonuje JS.
  Statyczna = treść gotowa w HTML → requests widzi. Dynamiczna (JS-rendered) = pusty szkielet,
  JS dociąga treść w przeglądarce → requests nie widzi artykułów. Problem na listing page Saxo/gold.org.
- P3 (czemu chunki): ✅ sam przywołał N² (300×300). Powody: limit tokenów + N² + (c) precyzja retrievalu.
- P4 (overlapping chunks): ✅ wzorowo — pokazał liczbowo (1-400, 300-700, 600-1000, overlap 100).
  Temat/zdanie na granicy cięcia nie ginie, powtarza się w sąsiednich chunkach — ciągłość.
- P5 (decompose): ⚠️ kierunek ODWRÓCONY — decompose() USUWA wskazany śmieciowy tag (script/style/
  nav/footer), nie "zostawia chciane". Czyścisz śmieci PRZED .text.
- P6 (select vs select_one): ✅ select() = lista wszystkich, select_one() = pierwszy (lub None).
- P7 (max_articles: int = 5): ✅ argument domyślny, użyje 5 gdy nie podano, własna wartość nadpisuje.
- P8 (sitemap XML): ✅ tworzy właściciel strony. Plik (sitemap.xml) z listą URL-i, pierwotnie dla
  wyszukiwarek. Drobna korekta: zwykle URL-e (czasem data mod.), niekoniecznie tytuły.
- P9 (sitemap vs JS-rendered) — KLUCZOWE, trafione: sitemap = statyczny plik serwowany wprost przez
  serwer → requests dostaje pełną listę URL-i bez JS. Omija zepsutą (dla requests) listing page.
  Same artykuły są statyczne → requests.get(url) widzi treść. JS był potrzebny tylko do listy, nie artykułów.

>>> DO UTRWALENIA: selektor=elementy nie tekst (P1), requests NIE wykonuje JS (P2), decompose() USUWA tag (P5).

### Embeddingi — teoria (next_due: 2026-06-20, ostatni wynik: 52%)

Quiz 10 pytań, dokończony 2026-06-13 (wcześniej w toku 1-6, dziś 7-10).

Wyniki:
- P1 (list comprehension — pętla): ⚠️ pętla OK, zgubione `.embedding` (wrzucał cały `item`).
  Reguła: [WYRAŻENIE for ZMIENNA in ŹRÓDŁO] → append(WYRAŻENIE), nie samej zmiennej.
- P2 (czemu chunki, nie cały dokument): ✅ precyzja retrievalu (1 wektor = wąski temat).
  Drugi powód: limit tokenów + N². Cały dokument = "uśredniona papka" tematów.
- P3 (limit tokenów): ⚠️ kierunek OK, brak mechanizmu. SEDNO: self-attention = każdy-token-z-każdym
  = N². Podwójna długość → 4× koszt. Stąd twardy limit (8191 dla 3-small).
- P4 (token): ✅ token ≠ zawsze słowo (sunny → sun+ny). ~1 token → 4 znaki.
- P5 (overlapping chunks): ✅ sens na granicy cięcia nie ginie, overlap powtarza fragment.
- P6 (mean pooling): ⚠️ POWTÓRZYĆ — mylony z tokenizacją. Model daje 1 wektor NA KAŻDY token
  (N wektorów), mean pooling uśrednia je kolumnami (liczba-po-liczbie) → 1 wektor chunka.
  Działa na WEKTORACH, nie tokenach. Token=wejście, wektor=wyjście.
- P7 (zakres wartości): ⚠️ POWTÓRZYĆ — pomylił z liczbą wymiarów (1536 to wymiar = P5, nie zakres).
  Zakres KAŻDEJ liczby → od -1 do 1, bo wektory są znormalizowane (długość 1) → szybkie cosine.
- P8 (cosine similarity): ⚠️ intuicja OK (podobieństwo z wektorów), brakowało: mierzy KĄT nie odległość.
  1.0 = ta sama strona (max podobne), 0.0 = prostopadłe (brak związku), -1.0 = przeciwne.
- P9 (MLM): ⚠️ POWTÓRZYĆ — nie pamiętał. Masked Language Model = maskujesz słowa w zdaniu, model
  zgaduje zamaskowane z kontekstu. Miliardy powtórzeń → uczy się znaczeń (podobny kontekst → podobny wektor).
- P10 (czy wymiar = pojęcie): ✅ NIE — reprezentacja rozproszona (distributed), znaczenie rozłożone
  po wszystkich 1536 wymiarach naraz, pojedynczy wymiar nieczytelny dla człowieka.

>>> DO KONIECZNEJ POWTÓRKI: P6 mean pooling, P7 zakres+normalizacja, P9 MLM. Utrwalić N² i wartości cosine.

### FastAPI — model poza endpointem (next_due: 2026-06-20, ostatni wynik: 65%)
1. Dlaczego `joblib.load()` ładujemy poza funkcją endpointu? — ZROZUMIANE (po naprowadzeniu)
2. Wzorzec łączący ładowanie modelu z cache odpowiedzi — ⚠️ idea OK, brakowało nazwy

Domknięte 2026-06-13:
- Model poza funkcją = ładuje się 1× przy starcie aplikacji; wewnątrz funkcji = przy KAŻDYM
  requeście (100 req = 100× joblib.load ~2s). Niezależne od Dockera/Azure — działa tak samo lokalnie.
- A) załaduj model raz ≠ C) cache wyników predykcji — dwie OSOBNE optymalizacje, nie jedna.
- Wspólna zasada = caching / space-time tradeoff (pamięć w zamian za czas).
- Caching vs memoization: memoizacja = cache wyników CZYSTEJ funkcji po jej argumentach
  (determinizm, te same argumenty → ten sam wynik, brak TTL). Caching ogólny = dowolna kosztowna
  operacja (DB, API, plik), zwykle z TTL/invalidacją.
- Cache cen złota (Twelve Data, TTL 12h) = CACHING, NIE memoizacja (klucz "gold" stały, cena zmienna).
- Termin na rozmowy: space-time tradeoff.

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
