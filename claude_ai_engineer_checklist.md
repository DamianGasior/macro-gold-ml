# Checklista: AI Engineer — droga do pracy

## 🎯 PLAN ZAMKNIĘCIA PROJEKTU GOLD (ustalone 2026-07-03)
*Po analizie ogłoszenia AI Engineer — kolejność zamykania Gold przed przejściem do RegRAG. Fraud Detection pominięty celowo (mniej istotny dla ścieżki AI Engineer).*

- [x] **MLflow — demo eksperymentu** ✅ (2026-07-08) — znacznie wykroczyło poza pierwotny zakres
  - `ml_flow.py`: `ml_flow__log_param`, `ml_flow__log_metrics`, `ml_flow__log_artifact` — osobny moduł, wywoływany z `lgbm_classification.py`
  - Param: nazwa/hiperparametry modelu, `train_start/end`, `test_start/end`, `PROBABILITY_THRESHOLD`
  - Metryki pogrupowane prefiksem `/` (`classification/*`, `strategy/*`, `benchmark/*`) — MLflow UI grupuje je w zwijane sekcje
  - `random_state=7` dodany do `LGBMClassifier` — bez tego wyniki nie były powtarzalne między runami (realny problem, który złapaliśmy przez porównanie dwóch identycznych uruchomień)
  - Po drodze znalezione i naprawione dwa poważne bugi metodologiczne w backteście: zły zakres dat w `self._bt` (liczył CAGR/Sharpe na całym train+test zamiast tylko na oknie testowym) i nakładające się pozycje (10-dniowe okna handlowe zachodzące na siebie, sztucznie pompujące CAGR do 120%+) — po naprawie: Sharpe ~0.8-1.1, CAGR ~11-16%, drawdown wyraźnie niższy niż buy-and-hold
  - `pipeline_with_time_series_split()` (walk-forward, 5 foldów) też podłączone do MLflow — jeden run per fold
  - Eksport wyników do Markdown: `ml_flow_export_results.py` — `mlflow.search_runs()` → tabela → `mflow_metrics_results.md` (do wklejenia do README, żeby ktoś mógł zobaczyć wyniki bez odpalania `mlflow ui` lokalnie)
  - **Quiz 2026-07-08 — 1/4 w pełni, 2 częściowe, 1 błędna:**
    - ✅ różnica param vs metric
    - ❌ **luka:** próba nadpisania `log_param` inną wartością w tym samym runie rzuca `MlflowException`, nie nadpisuje po cichu — to był realny bug w pętli walk-forward zanim dodaliśmy `with` per fold
    - ⚠️ **luka:** `with mlflow.start_run()` jest bezpieczniejsze bo gwarantuje zamknięcie runu **nawet przy wyjątku** (nie tylko przy normalnym zakończeniu bloku)
    - ⚠️ **luka:** `run_id` to nie "domyślna metryka" — to metadana runu (jak `status`, `start_time`), całkiem osobna kategoria od `metrics.`/`params.`/`tags.`
  - **Do powtórki (sierpień 2026):** różnica param immutability + `with` + exception safety + kategorie kolumn w `search_runs()`
- [ ] **Central banks gold purchases — jako kontekst LLM, NIE feature LGBM** (zdecydowane 2026-07-03)
  - Plik źródłowy sprawdzony: `Changes_latest_as_of_Jul2026_IFS (2).xlsx`, zakładka `Monthly` — 162 kraje, dane 2002-01 do 2026-05, zmiana rezerw w tonach/miesiąc, dużo NaN dla świeżych miesięcy (np. tylko 34/162 krajów ma dane za 2026-05)
  - Decyzja: dane zbyt rzadkie/dziurawe żeby bezpiecznie rozbić na dzienną częstotliwość bez ryzyka przesunięcia train/test split (confound z ostatniej lekcji o kontroli zmiennych)
  - Zamiast tego: agregacja trendu (12m / 3y / 4y / 5y net purchases) jako **tekstowy komentarz** wstrzykiwany do promptu LLM — ten sam wzorzec co `build_market_context()` / RAG, model interpretuje jakościowo, nie ilościowo
  - Konsekwencja: to zadanie NIE wymaga MLflow (nie ma retrainingu)
- [ ] **Function calling / Tool use w `gold_analysis.py`** ⭐ — LLM sam wywołuje `get_lgbm_signal()` jako tool zamiast że wynik jest zawsze wklejany do promptu. Bezpośredni pomost do agentów LangGraph w RegRAG.
- [ ] **Evals dla `gold_analysis.py`** ⭐ — 10-20 scenariuszy testowych + LLM-as-judge. Odpowiada wprost na pytanie rekrutacyjne "skąd wiesz że LLM odpowiada poprawnie" (patrz sekcja Evals niżej).
- [ ] **Weryfikacja testów jednostkowych** — checklista niżej mówi "zero testów", ale `tests/test_financial_metrics.py` i `tests/test_feature_engineering_regression_lgbm.py` już istnieją (patrz Poziom 1 → Testy jednostkowe) — do odświeżenia stanu.

*Reszta Poziomu 1 (LeetCode, algorytmy od zera, docker-compose, Azure Blob/Monitor) — fundamenty ogólne, nie blokują zamknięcia Gold, można robić równolegle.*
*Pinecone, LangChain, LangGraph, Langfuse, RAGAS — świadomie zarezerwowane dla RegRAG, nie duplikować w Gold.*

---

## Twoja przewaga strategiczna
15 lat bankowość (PM + analityk) + budujący ML projekt na danych finansowych = idealny kandydat na AI Engineer w fintech / banku. Wiele firm płaci premium za kogoś, kto rozumie i domenę, i kod.

---

## POZIOM 1 — FUNDAMENT (zrób to najpierw)
*Bez tego nie przejdziesz rekrutacji technicznej*


- [ ] OOP w Pythonie — klasy, dziedziczenie, `__init__`, `@property` (masz basics, utrwal na własnym kodzie)
- [ ] Type hints — `def func(x: int) -> str:` (standard w każdym profesjonalnym repo)
- [ ] Obsługa błędów — `try/except`, własne wyjątki, logowanie (`logging`)
  - [ ] Hierarchia poziomów: DEBUG → INFO → WARNING → ERROR → CRITICAL ✅ (2026-05-13) — omówione, rozumie progi i filtrowanie
  - [ ] `basicConfig(force=True)` vs `getLogger(__name__)` — kiedy co używać ✅ (2026-05-13) — pułapka z uvicorn/FastAPI nadpisującym root logger
  - [x] `FileHandler` — zapis logów do pliku ✅ (2026-05-13) — `logging_config.py` napisany, dynamiczna nazwa pliku z datą CET, auto-tworzenie folderu `app_logs/`
    - **Quiz 2026-05-13 — wynik 4/5:** ✅ datetime.now() vs utc ✅ brak timezone.cet ✅ Path.parent.parent ✅ FileExistsError przy mkdir ❌ literówka `exists_ok` zamiast `exist_ok`
    - **Luka do zapamiętania:** `exist_ok` (nie `exists_ok`) + naive vs aware datetime
  - [ ] Przeglądanie logów na zdalnym serwerze — SSH / PuTTY + `tail -f app.log`
- [ ] Środowiska wirtualne — `venv` lub `conda`, rozumienie `requirements.txt` (już używasz)
- [ ] Testy jednostkowe — `pytest`, testowanie funkcji ML (zero testów w projekcie — to luka)

### Implementacja algorytmów od zera ⭐ INTERVIEW PREP
*Rozmowy techniczne w ML często proszą o implementację w numpy — bez sklearn. Rozumiesz wtedy naprawdę co robi model, nie tylko jak go wywołać.*

- [ ] Logistic regression w numpy od zera (gradient descent, sigmoid, binary cross-entropy)
- [ ] K-means w numpy od zera (centroidy, iteracja, przypisanie klastrów)
- [ ] Gradient descent krok po kroku — zaktualizuj wagi ręcznie dla prostego przykładu

### LeetCode — podstawy DSA
*Duże banki i fintech często mają rundę algorytmiczną. 15-20 zadań Easy/Medium wystarczy na start.*

- [ ] Arrays i słowniki — najczęstsze struktury na rozmowach
- [ ] Sortowanie i wyszukiwanie binarne — klasyki
- [ ] 15-20 zadań Easy na LeetCode (category: Arrays, Hash Map)

### Git & CI/CD

*CI = automatyczne sprawdzanie kodu przy każdym push. CD = automatyczny deploy jeśli testy przeszły. Pre-commit to lokalny odpowiednik CI — sprawdza zanim w ogóle wypchniesz.*

- [ ] Git flow — branche, PR, merge, rebase (widzę, że używasz branchy — dobry start)
- [x] Pre-commit hooks — `flake8`, `black` — skonfigurowane, pierwszy commit przeszedł ✅ (2026-05-08)
- [x] GitHub Actions — automatyczny test po `git push` (1 prosty workflow wystarczy do CV) ✅ (2026-05-15)
  - *To samo co pre-commit, ale na serwerze — odpala się dla całego teamu przy każdym PR*
  - **Quiz 2026-05-16 — wynik 4/5:**
    - ✅ P1 Runner (wirtualna maszyna, checkout)
    - ✅ P2 Pipeline od git push do ACI (logika poprawna, drobna nieścisłość: ACI sam ściąga image, nie runner)
    - ⚠️ P3 Łańcuch secrets — rozumie koniec (Azure container config), ale pominął środek: `${{ secrets.X }}` → flaga `--environment-variables` w `az container create`
    - ✅ P4 load_dotenv() bez .env — nie crashuje + python-dotenv w requirements.txt (ImportError)
    - ⚠️ P5 Stop/start ACI — poprawna odpowiedź "nie czyści", błędne wyjaśnienie: env vars są w konfiguracji zasobu ACI (Azure RM), nie w "plikach image"
  - **Luki do powtórki (czerwiec 2026):** P3 łańcuch secrets, P5 gdzie dokładnie siedzą env vars w ACI
  - **Koncept przyswojony 2026-05-15:**
    - ✅ Automatyzacja procesów przy pushu na main
    - ✅ Odpalanie testów jednostkowych automatycznie
    - ✅ Budowanie wersji systemu (build image)
    - ✅ **Kluczowy koncept runner:** GitHub Actions = zdalny komputer (Ubuntu VM), który czeka i odpala się gdy coś się dzieje w repo (push, PR, harmonogram). Jak kolega który siedzi i czeka — jak tylko widzi coś na main, buduje, testuje i deployuje.
    - ✅ **Artefakt** = wynik procesu build (np. obraz Dockera, plik `.whl`). Nexus = firmowy magazyn artefaktów (odpowiednik Azure Container Registry w chmurze).

- [ ] Artefakty i repozytoria artefaktów (Nexus / ACR)
  - *Artefakt = gotowy produkt z procesu build, który można wersjonować, cofnąć i deployować. Nie kod źródłowy — skompilowany/spakowany wynik.*
  - *Nexus = firmowy magazyn artefaktów (on-premise). Azure Container Registry (ACR) = odpowiednik Nexusa dla obrazów Docker w Azure.*

### FastAPI ⭐ PRIORYTET #1

- [x] Tworzenie endpointu REST: `GET`, `POST` ✅ (2026-05-10) — GET /health + POST /predict zbudowane i działają lokalnie
- [x] Serwowanie modelu ML przez API — `POST /predict` → zwraca predykcję złota ✅ (2026-05-10) — model LGBM załadowany przez joblib, Pydantic waliduje 96 features
- [x] Pydantic do walidacji danych wejściowych ✅ (2026-05-10) — PredictRequest + PredictResponse, walidacja typów działa
- [x] Swagger UI / dokumentacja automatyczna ✅ (2026-05-10) — localhost:8000/docs działa out-of-the-box
- [x] `POST /chat` — endpoint czatu z LLM + RAG ✅ (2026-06-05) — działa lokalnie i na Azure. `ChatRequest` (question + uuid), `ChatResponse` (response + uuid), historia per sesja w `_chat_sessions` dict (in-memory). UUID generowany w `pre_pipeline()`, zwracany do klienta, wysyłany przy kolejnych pytaniach.
  - **Debug w tej sesji:** UUID type mismatch — klucz w dict był `UUID object`, klient odsyłał `str` → fix: `str(id)` przy zapisie. Znaleziony przez breakpointy + Debug Console.
  - **Frontend:** `static/index.html` serwowany przez FastAPI (`StaticFiles` + `FileResponse`). Użytkownik otwiera `http://<url>/` — JavaScript wysyła POST do `/post/chat` za kulisami.
- [x] FastAPI startup event — cache pre-warming: `@app.on_event("startup")` wywołuje `get_latest_features()` zanim serwer przyjmie pierwszy request ✅ (2026-06-30)
  - `on_event("startup")` / `on_event("shutdown")` — dwie wartości; deprecated w nowszych FastAPI (nowy sposób: `lifespan`)
  - `async def` nie wymagane — działa też zwykły `def`; `async` potrzebne tylko gdy w środku jest `await`
  - łańcuch: `start.yml` → `az container start` → ACI → Docker CMD → uvicorn → startup hook → serwer gotowy
  - **Quiz 2026-07-07** — zaplanowany

**Quiz 2026-05-10 — wynik 4/5:**
✅ uvicorn (rola serwera HTTP)
✅ kod błędu 422 przy złym requeście
❌ dlaczego model ładujemy poza endpointem (luka: wydajność — joblib.load trwa ~2s, nie może być przy każdym requeście)
✅ walidacja Pydantic przy złym typie
✅ GET vs POST semantyka

**Do odpytania za ~2-3 tygodnie:** pytanie 3 — dlaczego model poza funkcją endpointu. Też warto sprawdzić czy pamięta różnicę GET/POST przy bardziej złożonych przypadkach.

**Luka architektoniczna — naprawiona ✅ (2026-05-11):**
POST /predict przyjmuje teraz tylko `{"asset_name": "gold"}` — API samo fetchuje dane z Twelve Data + FRED, uruchamia feature engineering, zwraca predykcję. Dodano in-memory cache z TTL 12h (dane dzienne — nie ma sensu odpytywać API przy każdym requeście). Omówiono różnicę cache lokalnego vs Redis na Azure (wieloinstancyjność). Na 1 instancji kontenera in-memory cache działa poprawnie.

### Docker ⭐ PRIORYTET #2

- [x] `Dockerfile` — budowanie obrazu aplikacji ✅ (2026-05-11) — Dockerfile napisany, image `gold-api` zbudowany, kontener działa lokalnie na porcie 8000
- [ ] `docker-compose` — uruchamianie app + baza danych razem
- [x] Konteneryzacja swojego projektu FastAPI + model ✅ (2026-05-11) — `docker run -p 8000:8000 gold-api` działa, /docs i /health odpowiadają z kontenera

**Quiz 2026-05-11 — wynik 5/5:**
✅ docker build vs docker run
✅ kolejność warstw w Dockerfile (cache — requirements.txt przed kodem)
✅ flaga -p (port mapping, izolacja sieci kontenera)
✅ image nie przyjmuje requestów bez docker run
✅ crash kontenera nie dotyka image, Azure uruchamia nowy automatycznie

**Do zrobienia jeszcze z Dockera:**
- docker-compose (gdy dodamy bazę danych lub więcej serwisów)
- deploy image na Azure Container Registry

**Następny krok:** GitHub Actions — auto-deploy po `git push`

### Azure — Deploy ⭐ PRIORYTET #3

- [x] Azure Container Instances (ACI) — deploy kontenera Docker ✅ (2026-05-13) — `gold-api` działa na ACI, `/health` i `/predict/gold` odpowiadają
- [x] Docker Hub jako prywatny rejestr — push image + PAT do Azure ✅ (2026-05-13) — `damgas712/gold-api:latest`, image type: Private, `index.docker.io` jako login server
- [x] GitHub Actions — automatyczny deploy po `git push` (build → push → az container create) ✅ (2026-05-15)
  - **Quiz 2026-05-16 — 4/5 ✅ (opisany wyżej przy GitHub Actions)**
  - *Odpowiednik ręcznego: docker build → tag → push → az container delete/create*
  - **Pipeline dla tego projektu (omówiony 2026-05-15):**
    ```
    push na main
        ↓
    1. checkout kodu
        ↓
    2. build Docker image (gold-api:latest)
        ↓
    3. push image na Docker Hub (damgas712/gold-api)
        ↓
    4. redeploy ACI na Azure (gold-api-prediction-v2)
    ```
  - *Runner (Ubuntu VM) wykonuje każdy krok z pliku `.yml` — plik `.github/workflows/deploy.yml`*
  - **Koncepty do quizu (2026-06):**
    - ✅ GitHub Secrets → `${{ secrets.X }}` w workflow → `--environment-variables` w `az container create` → `os.environ` kontenera → `os.getenv()` — cały łańcuch, wartość nigdzie nie jest w pliku ani kodzie
    - ✅ `load_dotenv()` na Azure: szuka `.env` → nie ma go → nic nie robi (nie crashuje). Zmienne są już w `os.environ` wstrzyknięte przez Azure
    - ✅ `python-dotenv` musi być w `requirements.txt` — bez niego `from dotenv import load_dotenv` rzuca `ImportError` przy starcie kontenera
    - ✅ Stop/Start kontenera NIE czyści zmiennych środowiskowych — są w konfiguracji kontenera, nie w RAM. Znikają tylko przy `az container delete`
    - ✅ `pip freeze > requirements.txt` — synchronizacja venv z plikiem. Jeśli pakiet jest w venv ale nie w pliku → Docker go nie zainstaluje → crash na Azure
- [x] GitHub Actions — scheduled start/stop ACI ✅ (2026-05-29) — `start.yml` (cron 06:30 UTC = 08:30 CEST, pon-pt) + `stop.yml` (cron 21:30 UTC = 23:30 CEST, pon-pt). Kontener wyłączony w weekend → oszczędność ~40-60% vs non-stop (~$8/mies vs ~$18/mies)
- [ ] Azure Blob Storage — zapis logów z kontenera
  - *Logi w pliku `app_logs/` istnieją tylko w kontenerze — giną przy restarcie. Blob Storage = zewnętrzny, trwały dysk*
- [ ] Azure Container Apps — scale-to-zero (tańsza alternatywa dla ACI)
  - *ACI kosztuje ~$36/mies. 24/7, Container Apps zatrzymuje się gdy brak ruchu → $0 przy bezczynności*
- [ ] Logi przez CLI — `az container logs --name gold-api --resource-group gold-api-rg` — podgląd logów działającego kontenera
  - *Odpowiednik `tail -f app.log` ale dla kontenera na ACI — minimum, które masz pod ręką*
  - *Wersja live: `az container logs --follow` — strumieniuje logi w czasie rzeczywistym*
- [ ] Azure Monitor / Application Insights — centralne logi z kontenera w portalu Azure
  - *Odpowiednik `tail -f app.log` ale w chmurze, z filtrowaniem i alertami*

---

## POZIOM 2 — LLM & AI APLIKACJE (serce roli AI Engineer)
*Tu jest 80% ofert pracy dla "AI Engineer" w 2025-2026*

### LLM & OpenAI API

- [ ] OpenAI / Azure OpenAI API — `chat.completions.create()`, parametry (`temperature`, `max_tokens`)
- [ ] Prompt engineering — system prompt, few-shot examples, chain-of-thought
- [ ] Embeddings — co to jest wektor, po co, jak użyć `text-embedding-ada-002`
- [ ] Function calling / Tool use — model wywołuje funkcję Pythona (bardzo często na rozmowach!)
- [ ] Streaming odpowiedzi — `stream=True`

### RAG (Retrieval-Augmented Generation) ⭐ PRIORYTET #3
*Najczęściej proszona rzecz na rozmowach o pracę*

- [ ] Koncepcja RAG: dokument → chunking → embedding → vector DB → retrieval → LLM
- [ ] LangChain lub LlamaIndex — zbuduj 1 działający RAG
- [ ] Praktyczny projekt: RAG na dokumentach bankowych / raportach makroekonomicznych (idealnie pasuje do twojego projektu!)

**Postęp RAG (2026-05-24 → 2026-06-07):**
- ✅ `scraper.py` — scraper działa: simplevisorinsights.com (statyczna), Saxo (sitemap XML), gold.org (Algolia API)
- ✅ ChromaDB zainstalowane, trafilatura zainstalowane, Playwright zainstalowane
- ✅ `indexer.py` — embeddingi + zapis do ChromaDB (2026-05-24)
- ✅ `retriever.py` — similarity search (2026-05-26)

**✅ Saxo Bank — rozwiązane (2026-05-24):**
Sitemap XML (`article-sitemap-en-1.xml`) jako obejście JS-rendered listing page. `fetch_saxo_article_links()` parsuje XML przez `xml.etree.ElementTree`, filtruje po kategorii (macro/commodities/bonds).

**✅ gold.org — rozwiązane przez Algolia API (2026-06-07):**
Strona JS-rendered, ale przy scrollowaniu wysyła zapytania do Algolia API z publicznym search-only kluczem.
Odkryte przez DevTools → Network tab → Fetch/XHR. `fetch_gold_org_article_links()` wywołuje Algolia REST API bezpośrednio (POST, JSON body, URL-encoded params). Filtrowanie po `topics` (wszystkie poza ESG) i opcjonalnie `collections`. Łącznie 1000 artykułów dostępnych.
- `trafilatura.extract(favor_precision=True)` — odrzuca disclaimery i stopki ✅
- Artykuły za paywallem (Weekly Markets Monitor) — pomijane automatycznie (zwracają `""`) ✅
- **Quiz topic:** facetFilters AND/OR, Algolia multi-query API, URL-encoded params, search-only key

### Vector Databases

- [ ] Co to jest indeks wektorowy i dlaczego szybki
- [x] ChromaDB — lokalnie, do nauki i prototypów ✅ (2026-05-24) — `indexer.py` działa, 10 chunków zapisanych
- [ ] **Pinecone** ⭐ — następny krok po ChromaDB, najpopularniejszy w ogłoszeniach AI Engineer
  - *Przepnij z ChromaDB gdy będziesz deployował RAG na Azure — zmiana ~10 linii kodu*
  - *Free: 2GB storage, 2M write units/mies, 1M read units/mies — wystarczy na projekt*
- [ ] `similarity_search()` — znajdowanie podobnych dokumentów

*Weaviate, pgvector, FAISS — do rozważenia później jako rozszerzenie CV. Teraz fokus: ChromaDB → Pinecone.*

### Evals dla LLM ⭐ WAŻNE DLA ROZMÓW
*Jak sprawdzasz czy Twój LLM działa poprawnie? To pytają na każdej rozmowie o AI Engineer.*

- [ ] Format checks — odpowiedź po polsku? Mieści się w max 4 zdaniach? (testy jednostkowe stylu pytest)
- [ ] Behavior checks — przy sygnale LONG model nie odpowiada "brak sygnału", przy NO TRADE nie halucynuje kupna
- [ ] Zestaw 10-20 scenariuszy testowych dla `gold_analysis.py` z mock_response (bez prawdziwego API call)
- [ ] Metryka: % scenariuszy które przechodzą (cel: >80%)
- [ ] LLM-as-judge ⭐ KLUCZOWE NA ROZMOWACH — osobny skrypt odpalany raz na tydzień / przed deploy'em:
  - mocniejszy model (np. gpt-4o) ocenia próbkę odpowiedzi słabszego (gpt-4o-mini)
  - wejście: pytanie + odpowiedź; wyjście: PASS / FAIL + uzasadnienie
  - NIE przy każdym zapytaniu produkcyjnym — za drogo; uruchamiasz ręcznie lub przez GitHub Actions schedule
  - *"Skąd wiesz że twój LLM odpowiada poprawnie?"* — to jest właśnie odpowiedź na to pytanie

### MLflow — experiment tracking
*4 linijki kodu w istniejącym LGBM pipeline. Pokazuje że traktujesz ML produkcyjnie — pytają o to na każdej rozmowie.*

- [x] Zaloguj 1 trening LGBM: parametry (`threshold`, `n_estimators`) + metryki (Sharpe, CAGR) + artefakt `.pkl` ✅ (2026-07-08) — patrz szczegóły w sekcji "PLAN ZAMKNIĘCIA" na górze pliku
- [x] `mlflow ui` — porównaj 2-3 runy w przeglądarce ✅ (2026-07-08) — dodatkowo eksport wielu runów do tabeli Markdown przez `mlflow.search_runs()` (`ml_flow_export_results.py`)
- [x] Rozumiesz różnicę: `mlflow.log_param()` vs `mlflow.log_metric()` vs `mlflow.log_artifact()` ✅ (2026-07-08) — quiz 1/4 w pełni, luki w param immutability i exception-safety `with` (patrz notatka wyżej)

### LangChain / LlamaIndex

- [ ] `LLMChain`, `RetrievalQA`
- [ ] Agenty — `AgentExecutor`, tools
- [ ] Memory w konwersacji

---

## POZIOM 3 — CLOUD & MLOPS
*Potrzebne do seniorskich ról lub specjalizacji*

### Azure (strategicznie — bank używa Azure)

- [ ] Azure OpenAI Service — deployment modelu GPT-4o w Azure (banki nie używają OpenAI bezpośrednio, tylko Azure)
- [ ] Azure Blob Storage — przechowywanie danych / artefaktów modeli
- [ ] Azure Functions — serverless trigger
- [ ] Azure ML Studio — podstawy (nie musi być głębokie)
- [ ] Azure Monitor / Application Insights — przeglądanie logów aplikacji w chmurze (odpowiednik `tail -f` na Azure)

### Monitoring ML (MLOps basics)

- [ ] Concept drift — co to jest i jak wykrywać
- [ ] Model versioning

### SQL zaawansowany

- [ ] Window functions: `ROW_NUMBER()`, `LAG()`, `LEAD()` (kluczowe przy danych finansowych)
- [ ] CTEs (`WITH ...`)
- [ ] PostgreSQL — podstawowe różnice od Oracle

---

## POZIOM 4 — NICE TO HAVE
*Wyróżnik, nie wymóg*

- [ ] Kubernetes — podstawy: Pod, Deployment, Service (tylko wiedza koncepcyjna)
- [ ] Kafka — co to jest stream processing, po co (1 tutorial wystarczy)
- [ ] Databricks / Snowflake — jeśli celujesz w duże korporacje (twój bank pewnie ma jedno z tych)
- [ ] NoSQL — MongoDB: insert, find, aggregation pipeline

---

## Legenda
⭐ **PRIORYTET** — zacznij od tego  
*Kursywa* — dodatkowy kontekst