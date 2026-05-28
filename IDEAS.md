# Pomysły na nowe projekty

---

## PROJEKT 1: Earnings Intelligence / FundaSignal

**Status:** Pomysł — planowanie  
**Data:** 2026-05-26

### Cel projektu

System łączący fundamenty spółek (dokumenty SEC) z danymi rynkowymi (ceny, volatility, indeksy).
Pozwala zadawać pytania typu:
- *"Co powiedział CEO Apple o popycie w Q3 2023 i jak zareagował kurs?"*
- *"Pokaż volatility JPMorgan przed i po earnings w ostatnich 4 kwartałach"*
- *"Znajdź przypadki gdzie guidance była pozytywna, ale kurs spadł — co rynek widział inaczej?"*

Kluczowa wartość: **rozbieżność między narracją zarządu a reakcją rynku** — to jest właśnie alfa.

---

### Dwa strumienie danych

```
FUNDAMENTY (tekst)                    RYNEK (liczby)
──────────────────                    ──────────────
SEC 10-K / 10-Q                       Ceny akcji (OHLCV)
Earnings call transcript (8-K)        Wolumen
Management guidance                   Volatility historyczna (HV)
Risk factors                          VIX (market volatility)
                                      Indeksy: S&P500, Nasdaq
```

**Punkt łączący:** data zdarzenia (filing date) — oś czasu do korelacji.

---

### Źródła danych — wszystko darmowe

| Źródło | Co daje | Koszt |
|--------|---------|-------|
| SEC EDGAR API | 10-K, 10-Q, 8-K (z transkryptami) | $0 |
| `yfinance` (Python lib) | Ceny OHLCV, wolumen, historia | $0 |
| `^VIX` via yfinance | CBOE Volatility Index | $0 |
| Obliczona HV | Rolling std dev z cen (własna kalkulacja) | $0 |

Transkrypcje earnings call są w SEC jako 8-K filings — nie trzeba płacić za Seeking Alpha.

---

### Architektura (wstępna)

```
[SEC EDGAR API] ──→ 10-K, 10-Q, 8-K (transcripts)
                         ↓
                   [Chunking + Embeddings]
                         ↓
                   [Vector DB — Qdrant / Pinecone]

[yfinance] ──→ OHLCV, Volume, VIX, indeksy (S&P500, Nasdaq)
                    ↓
             [PostgreSQL / SQLite]
             (ceny + daty eventów — joinowanie po dacie)

                    ↓
             [LLM Agent z Function Calling]
             Funkcje: get_prices(), get_volatility(),
                      get_transcript(), get_filing()
             + RAG po dokumentach
             + Correlation analysis

                    ↓
             [FastAPI backend]
                    ↓
             [Dashboard — Plotly / Dash]
             Wykres ceny + markery na datach filingów
             Sentiment overlay
             Chat Q&A
```

---

### Nowe umiejętności (vs. obecny projekt)

| Skill | Jak pojawia się w projekcie |
|-------|----------------------------|
| Agents + Function Calling | Agent decyduje: dokument? cena? volatility? |
| Vector DB (Qdrant/Pinecone) | Indeksowanie dokumentów SEC |
| Time series + SQL | JOIN cen z datami eventów |
| Evals | Czy odpowiedź RAG jest trafna |
| Streaming | Live odpowiedzi w chacie |
| Plotly dashboard | Wizualizacja cen + eventów |

---

### Etapy budowy (szkic)

1. **MVP — dane:** Pobieranie 10-K jednej spółki z SEC + ceny z yfinance / mozna z twelva data, mam juz konto i gotowa implementacje
2. **RAG:** Chunking, embeddingi, Vector DB — Q&A po dokumencie
3. **Korelacja:** JOIN dokumentów z cenami po dacie, wykres z markerami
4. **Transcripts:** Pobieranie 8-K, sentiment z LLM
5. **Agent:** Function calling — agent sam sięga po właściwy zasób
6. **Dashboard:** FastAPI + Plotly, chat + wykresy
7. **Evals + MLflow:** Ocena jakości odpowiedzi, tracking eksperymentów

---

### Pomysły do rozwinięcia / otwarte pytania

- [ ] Które spółki jako dane startowe? (duże: AAPL, JPM, MSFT — dużo danych historycznych)
- [ ] Jak liczyć "rozbieżność" sentiment vs. cena? (prosta korelacja? ranking?)
- [ ] Alerting — powiadomienie gdy wychodzi nowy filing?
- [ ] Porównanie wielu spółek w jednym pytaniu
- [ ] Czy dodać dane makro (CPI, stopy procentowe) jako dodatkowy kontekst?

---

*Plik do zbierania pomysłów — uzupełniaj na bieżąco.*

---

## PROJEKT 2: Bank Fraud Detection

**Status:** Pomysł — porównany z Projektem 1  
**Data:** 2026-05-27

### Cel projektu

Model ML wykrywający fraudy na transakcjach kartowych.  
Wejście: dane transakcji → Wyjście: prawdopodobieństwo fraudu + wyjaśnienie decyzji (SHAP).  
End-to-end: dane → model → FastAPI → Docker → (opcjonalnie) Azure.

---

### Dataset

**Credit Card Fraud Detection** — Kaggle (ULB)  
- 284k transakcji, ~0.17% to fraud  
- Features V1–V28: PCA z prawdziwych danych europejskiego banku (zanonimizowane)  
- Dodatkowe: `Amount`, `Time`  
- Darmowy, gotowy do użycia

---

### Nowe umiejętności (vs. gold projekt)

| Skill | Jak pojawia się w projekcie |
|---|---|
| Imbalanced data (SMOTE, class_weight) | fraud = 0.17% transakcji |
| Precision / Recall / F1 / AUC-ROC | właściwe metryki — accuracy tu myli |
| SHAP (Explainable AI) | "dlaczego ta transakcja to fraud?" |
| Feature engineering z transakcji | Twoja domena bankowa |
| FastAPI endpoint (ML serving) | POST /predict → fraud_prob + reasons |
| Docker | konteneryzacja modelu |

---

### Etapy budowy

**Etap 1 — Dane + EDA (1-2 dni)**
- Wczytanie datasetu Kaggle
- Analiza: ile fraudów, rozkład kwot, godzin
- Wizualizacja korelacji
- Cel: zrozumieć jak wygląda fraud w danych

**Etap 2 — Feature Engineering + Model (2-3 dni)**
- SMOTE — oversampling klasy mniejszości
- LightGBM z `class_weight='balanced'`
- Metryki: precision, recall, F1, AUC-ROC, confusion matrix
- Kluczowa lekcja: dlaczego accuracy = 99.9% jest tu bezużyteczna

**Etap 3 — Explainability / SHAP (1-2 dni)**
- SHAP values: które featury wpływają na decyzję modelu?
- Wyjaśnienie dla pojedynczej transakcji: "dlaczego fraud?"
- Kluczowa lekcja: XAI wymagane prawnie w regulacjach bankowych (model risk)

**Etap 4 — API + Docker (2-3 dni)**
- FastAPI endpoint: `POST /predict` → `{fraud_prob, is_fraud, top_reasons}`
- Dockerize
- Opcjonalnie: deploy na Azure

---

### Przykład odpowiedzi API

```json
POST /predict
{
  "amount": 1250.00,
  "hour": 2,
  "v1": -1.35, "v2": -0.07
}

Response:
{
  "is_fraud": true,
  "fraud_probability": 0.94,
  "top_reasons": [
    {"feature": "hour", "impact": 0.31},
    {"feature": "amount", "impact": 0.22}
  ]
}
```

---

### Wnioski z porównania z Projektem 1 (FundaSignal)

**Fraud Detection** to projekt klasycznego ML — solidny, ale większość technologii (LightGBM, FastAPI, Docker) już opanowana. Zakres nowych rzeczy jest wąski: SMOTE, SHAP, lepsze metryki.

**FundaSignal** ma ~2x większy scope nowych umiejętności: RAG, Vector DB, LLM Agents, Function Calling, Embeddings, Evals, Streaming. To są core skille AI Engineera w 2025/2026.

**Rekomendacja:**
- Jeśli priorytet to AI Engineer jak najszybciej → **zacznij od FundaSignal**
- SHAP i SMOTE można ogarnąć samodzielnie w 2-3h bez osobnego projektu
- Fraud Detection jako projekt uzupełniający po FundaSignal lub równolegle

**Unikalny atut Fraud Detection:** domena bankowa — możesz opowiedzieć jak fraud detection działa w praktyce, bo widziałeś to z drugiej strony przez 15 lat.

---

## Porównanie wszystkich 3 projektów

| Skill | Fraud Detection | FundaSignal | RegRAG |
|---|---|---|---|
| LightGBM / ML klasyczne | ✅ już znasz | ❌ | ❌ |
| Imbalanced data / SMOTE | ✅ nowe | ❌ | ❌ |
| SHAP / Explainability | ✅ nowe | ❌ | ❌ |
| FastAPI | już umiesz | już umiesz | już umiesz |
| Docker | już umiesz | już umiesz | już umiesz |
| RAG | ❌ | ✅ nowe | ✅ nowe |
| Vector DB | ❌ | ✅ nowe | ✅ nowe |
| **LangChain / LlamaIndex** | ❌ | ✅ nowe | ✅ nowe |
| **LangGraph (multi-agent)** | ❌ | ✅ nowe | ✅ nowe |
| Embeddings | ❌ | ✅ nowe | ✅ nowe |
| PostgreSQL + time series JOIN | ❌ | ✅ nowe | ❌ |
| Streaming responses | ❌ | ✅ nowe | ✅ nowe |
| Evals (RAGAS) | ❌ | ✅ nowe | ✅ nowe |
| **Langfuse (LLM observability)** | ❌ | ❌ | ✅ nowe |
| **Azure AI Search** | ❌ | ❌ | ✅ nowe |
| PDF parsing | ❌ | ❌ | ✅ nowe |
| Web scraping / RSS watcher | ❌ | ❌ | ✅ nowe |
| Multi-source doc management | ❌ | ❌ | ✅ nowe |
| GitHub Actions CI/CD | ❌ | ❌ | ✅ nowe |
| **Nowych skillów** | **~3** | **~10** | **~13** |
| **Zgodność z rynkiem PL 2026** | niska | średnia | **bardzo wysoka** |
| **Konkurencja** | Kaggle | Google Finance AI | praktycznie brak |
| **Twoja przewaga domenowa** | wysoka | niska | bardzo wysoka |
| **Wartość biznesowa** | średnia | niska | wysoka |

### Wnioski końcowe

**RegRAG wygrywa** pod każdym kątem istotnym dla Ciebie:
- Najwięcej nowych skillów (~9 vs ~8 vs ~3)
- Zero sensownej konkurencji — Google Finance AI nie robi RAG po dokumentach regulacyjnych EBA/FinCEN/BIS
- Twoja 15-letnia wiedza bankowa to przewaga której żaden junior AI Engineer nie ma
- Compliance teams płacą krocie za tego typu narzędzia — realny biznes

**Rekomendowana kolejność:**
```
Gold Project     →    Fraud Detection     →    RegRAG
(w toku)              ~2 tygodnie              ~8-10 tygodni
dokończ RAG           SMOTE + SHAP             główny cel
+ Azure deploy        klasyczny ML done        AI Engineer path
```

---

## PROJEKT 3: RegRAG — Regulatory Intelligence

**Status:** Pomysł — zaplanowany  
**Data:** 2026-05-27

### Cel projektu

System RAG do przeszukiwania dokumentów regulacyjnych banków z Europy i USA.  
Wejście: pytanie w języku naturalnym → Wyjście: odpowiedź z cytatem źródłowym + wskazaniem regulatora i dokumentu.  
Unikalna wartość: **porównanie regulacji między jurysdykcjami** (EU vs USA) w jednym zapytaniu.

---

### Źródła dokumentów (wszystko darmowe, publiczne)

| Instytucja | Co publikuje | Forma |
|---|---|---|
| **EBA** (European Banking Authority) | Guidelines, RTS, ITS, Q&A | PDF |
| **ECB** (European Central Bank) | Supervisory guidance, stress tests | PDF |
| **BIS** (Bank for International Settlements) | Basel III/IV, core standards | PDF |
| **ESMA** | MiFID II, regulacje rynków kapitałowych | PDF |
| **KNF** (Polska) | Rekomendacje, komunikaty nadzorcze | PDF |
| **Fed** (Federal Reserve) | SR Letters, supervision manuals | PDF |
| **OCC** | Comptroller's Handbooks | PDF |
| **FinCEN** | AML/KYC guidelines, SARs guidance | PDF |
| **CFPB** | Consumer protection rules | PDF |

---

### Przykładowe pytania do systemu

```
"Jakie są wymogi EBA dotyczące LCR (Liquidity Coverage Ratio)?"
"Porównaj wymogi kapitałowe Basel IV z podejściem Fed dla banków systemowych"
"Co mówi FinCEN o beneficial ownership od 2024?"
"Jakie są różnice między PSD2 a PSD3 w zakresie strong authentication?"
"Znajdź wszystkie regulacje dotyczące operational resilience w EU i USA"
"Jakie kary grożą za naruszenie wymogów AML według EBA vs FinCEN?"
```

---

### Nowe umiejętności (vs. gold projekt)

| Skill | Jak pojawia się w projekcie |
|---|---|
| PDF parsing (pdfplumber) | parsowanie dokumentów regulacyjnych |
| Chunking strategii | podział dokumentów na sensowne fragmenty |
| Embeddings (OpenAI / HuggingFace) | wektoryzacja fragmentów dokumentów |
| Vector DB — Qdrant | przechowywanie i wyszukiwanie embeddingów |
| RAG pipeline | retrieval → augmentation → generation |
| **LangChain** | orchestration layer dla RAG (pojawia się w 80%+ ofert AI Engineer PL) |
| **LangGraph** | multi-agent: search_eu / search_usa / compare jako osobne węzły grafu |
| Metadata filtering | filtrowanie po regulatorze, roku, temacie |
| Streaming responses | live odpowiedzi w chacie |
| Evals (RAGAS) | ocena jakości odpowiedzi RAG: faithfulness, answer relevancy, context recall |
| **Langfuse** | LLM observability: trace każdego zapytania (prompt, retrieval, odpowiedź, koszt) |
| Web scraping / RSS watcher | automatyczne pobieranie nowych dokumentów |
| Multi-source document management | wiele regulatorów, wiele formatów |
| Azure deploy | hosting API i Vector DB |
| **Azure AI Search** | alternatywa dla Qdrant na produkcji (wprost wymieniana w ogłoszeniach DCG, emagine) |
| GitHub Actions CI/CD | auto-deploy na Azure przy push na main |

---

### Architektura

```
[RSS Watcher / PDF Scraper]
EBA, ECB, BIS, Fed, OCC, FinCEN, KNF
           ↓
   [Document Parser]
   pdfplumber → czyszczenie tekstu → chunking
   Metadata: {regulator, rok, typ, jurysdykcja}
           ↓
   [Embeddings + Vector DB]
   OpenAI text-embedding-3-small
   → Qdrant lokalnie (dev) / Azure AI Search (produkcja)
   Filtrowanie po: EU/USA, regulator, temat
           ↓
   [LangChain RAG Chain]
   Retriever → PromptTemplate → LLM (GPT-4o-mini)
   Grounding: odpowiedź z cytatem źródłowym
           ↓
   [LangGraph Multi-Agent]
   Węzły: search_eu → search_usa → compare → summarize
   Agent sam decyduje który węzeł uruchomić
   Narzędzia: search_regulation(), compare_rules(),
              get_latest_update(), summarize_document()
           ↓
   [Langfuse — LLM Observability]
   Trace każdego zapytania: prompt, retrieval chunks,
   odpowiedź, latencja, koszt tokenów
           ↓
   [FastAPI backend]
   POST /query  → {answer, sources[], citations[]}
   GET  /docs   → lista dostępnych dokumentów
   GET  /update → trigger nowego scrapingu
           ↓
   [Prosta UI — Streamlit lub Gradio]
   Chat + filtry: EU / USA / regulator / rok
```

---

### Etapy budowy

**Etap 1 — Dane + Parser (1-2 dni)**
- Pobranie 5-10 dokumentów PDF (EBA + FinCEN jako start)
- `pdfplumber` → czyszczenie tekstu, usuwanie nagłówków/stopek
- Chunking: strategia fixed-size vs. sentence-based
- Metadata: regulator, rok, typ dokumentu, jurysdykcja
- Cel: pipeline do zamiany PDF → czysty tekst z metadanymi

**Etap 2 — Embeddings + Vector DB (2-3 dni)**
- OpenAI `text-embedding-3-small` (tanie, dobre jakościowo)
- Qdrant lokalnie (Docker) → indeksowanie chunków
- Testowanie similarity search: czy zwraca właściwy fragment?
- Kluczowa lekcja: jak działa cosine similarity, co to embedding

**Etap 3 — RAG Pipeline (2-3 dni)**
- Retrieval: zapytanie → embedding → top-k chunków z Qdrant
- Augmentation: prompt = pytanie + retrieved chunks
- Generation: GPT-4o-mini odpowiada z cytatem źródłowym
- Kluczowa lekcja: hallucination vs. grounding w dokumentach

**Etap 4 — LangChain + LangGraph Agent (2-3 dni)**
- LangChain jako warstwa RAG: retriever → prompt → LLM (nie piszemy od zera)
- LangGraph: multi-agent graph z węzłami `search_eu`, `search_usa`, `compare`
- Agent sam decyduje który węzeł uruchomić na podstawie zapytania
- Cross-jurisdiction queries: "porównaj EU vs USA"
- Kluczowa lekcja: jak działa graph-based agent, ReAct pattern, tool calling
- Dlaczego LangChain a nie od zera: pojawia się w 80%+ ofert AI Engineer w Polsce — słowo kluczowe w CV i rozmowach rekrutacyjnych

**Etap 5 — Evals + Observability (1-2 dni)**
- **RAGAS**: ocena jakości RAG — faithfulness, answer relevancy, context recall
- **Langfuse**: LLM observability — trace każdego zapytania (prompt, retrieval, odpowiedź, latencja, koszt tokenów)
- Zestaw testowych pytań z oczekiwanymi odpowiedziami (golden dataset)
- Kluczowa lekcja: jak mierzyć jakość LLM — bez evals nie wiesz czy model kłamie; Langfuse różnicuje CV na poziomie senior

**Etap 6 — Streaming + RSS Watcher (1-2 dni)**
- Streaming odpowiedzi przez FastAPI (Server-Sent Events)
- RSS watcher: EBA i Fed publikują feed nowych dokumentów
- Auto-download + re-index przy nowym dokumencie
- Kluczowa lekcja: event-driven architecture, live updates

**Etap 7 — Deploy na Azure (2-3 dni)**
- Vector DB: Qdrant na Azure Container Instance LUB migracja na Azure AI Search
  - Azure AI Search pojawia się wprost w ogłoszeniach (DCG, emagine) — warto umieć jedno i drugie
- FastAPI jako Azure Container App
- GitHub Actions: auto-deploy przy push na main (CI/CD pipeline)
- Kluczowa lekcja: cloud deployment end-to-end, CI/CD w praktyce

---

### Wnioski końcowe

**Dlaczego RegRAG to najlepszy projekt dla Twojej ścieżki:**

1. **Scope nauki (~11 nowych skillów)** — więcej niż FundaSignal, żaden inny projekt nie uczy tylu rzeczy naraz wymaganych od AI Engineera
2. **Zero realnej konkurencji** — Google Finance AI robi finanse, ale nikt nie ma taniego RAG po dokumentach EBA/FinCEN/BIS dostępnego dla mniejszych banków i fintechów
3. **Twoja przewaga** — 15 lat w banku oznacza że rozumiesz kontekst dokumentów, widzisz czy odpowiedź jest sensowna, możesz zadawać realne pytania compliance teamów
4. **Wartość biznesowa** — compliance consulting to branża gdzie płaci się krocie za "znajdź mi to w regulacji"; narzędzie które robi to automatycznie ma realną wartość
5. **Naturalna kontynuacja gold projektu** — masz już zaczęty RAG w `src/llm/rag/`, scraper i indexer — to naturalne rozwinięcie tego co już robisz

**Rekomendowana kolejność projektów:**
```
Gold Project     →    Fraud Detection     →    RegRAG
(w toku)              ~2 tygodnie              ~8-10 tygodni
dokończ RAG           SMOTE + SHAP             główny cel
+ Azure deploy        klasyczny ML done        AI Engineer path
```

---

### Analiza rynku pracy — walidacja (maj 2026)

> Analiza ogłoszeń z JustJoinIT, NoFluffJobs, Pracuj.pl — maj 2026  
> Źródła: emagine, DCG, SCALO, Billennium, 7N, QX Consulting, EPAM

**Stack obowiązkowy w ogłoszeniach AI Engineer Polska (80%+ ofert):**

| Skill | Status w RegRAG |
|---|---|
| Python (advanced) | ✅ |
| RAG pipeline end-to-end | ✅ etap 3 |
| Vector DB (Qdrant / Weaviate / Pinecone) | ✅ etap 2 + Azure AI Search etap 7 |
| LLM integration (OpenAI / Azure OpenAI) | ✅ etap 3 |
| **LangChain lub LlamaIndex** | ✅ dodany etap 4 |
| **LangGraph (multi-agent)** | ✅ dodany etap 4 |
| FastAPI | ✅ etap po streaming |
| Docker | ✅ etap 2 (Qdrant) |
| Azure (Azure OpenAI, Container Apps, AI Search) | ✅ etap 7 |

**Stack różnicujący (senior / mid):**

| Skill | Status w RegRAG |
|---|---|
| **RAGAS evals** | ✅ etap 5 |
| **Langfuse (LLM observability)** | ✅ dodany etap 5 |
| Streaming (SSE) | ✅ etap 6 |
| GitHub Actions CI/CD | ✅ etap 7 |
| Kubernetes (podstawy) | ⚠️ opcjonalnie — nie w planie |
| MCP (Model Context Protocol) | ⚠️ emerging — warto śledzić, nie priorytet |

**Widełki płacowe dla tego stacka w Polsce (B2B):**
- Junior / pierwsze komercyjne projekty: 80–110 PLN/h netto
- Mid (1-3 lata, produkcyjny RAG): 130–170 PLN/h netto
- Senior (5+ lat, architektura systemów): 180–230 PLN/h netto
