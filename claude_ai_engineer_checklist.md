# Checklista: AI Engineer — droga do pracy

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