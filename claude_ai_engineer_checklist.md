# Checklista: AI Engineer — droga do pracy

## Twoja przewaga strategiczna
15 lat bankowość (PM + analityk) + budujący ML projekt na danych finansowych = idealny kandydat na AI Engineer w fintech / banku. Wiele firm płaci premium za kogoś, kto rozumie i domenę, i kod.

---

## POZIOM 1 — FUNDAMENT (zrób to najpierw)
*Bez tego nie przejdziesz rekrutacji technicznej*

### Python & Inżynieria oprogramowania

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

### Git & CI/CD

*CI = automatyczne sprawdzanie kodu przy każdym push. CD = automatyczny deploy jeśli testy przeszły. Pre-commit to lokalny odpowiednik CI — sprawdza zanim w ogóle wypchniesz.*

- [ ] Git flow — branche, PR, merge, rebase (widzę, że używasz branchy — dobry start)
- [x] Pre-commit hooks — `flake8`, `black` — skonfigurowane, pierwszy commit przeszedł ✅ (2026-05-08)
- [ ] GitHub Actions — automatyczny test po `git push` (1 prosty workflow wystarczy do CV)
  - *To samo co pre-commit, ale na serwerze — odpala się dla całego teamu przy każdym PR*

### FastAPI ⭐ PRIORYTET #1

- [x] Tworzenie endpointu REST: `GET`, `POST` ✅ (2026-05-10) — GET /health + POST /predict zbudowane i działają lokalnie
- [x] Serwowanie modelu ML przez API — `POST /predict` → zwraca predykcję złota ✅ (2026-05-10) — model LGBM załadowany przez joblib, Pydantic waliduje 96 features
- [x] Pydantic do walidacji danych wejściowych ✅ (2026-05-10) — PredictRequest + PredictResponse, walidacja typów działa
- [x] Swagger UI / dokumentacja automatyczna ✅ (2026-05-10) — localhost:8000/docs działa out-of-the-box

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

**Następny krok:** deploy na Azure (Azure Container Registry → Azure Container Apps)

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

### Vector Databases

- [ ] Co to jest indeks wektorowy i dlaczego szybki
- [ ] Qdrant (open source, lokalnie) lub Pinecone (cloud) — minimum jedno
- [ ] `similarity_search()` — znajdowanie podobnych dokumentów

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

- [ ] MLflow — logowanie eksperymentów, metryk, artefaktów modelu (dodaj do swojego LightGBM projektu!)
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