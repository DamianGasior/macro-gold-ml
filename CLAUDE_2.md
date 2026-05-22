# Ścieżka do AI Engineera — plan projektu portfolio

## Wniosek z analizy rynku (maj 2026)

Rynek szuka inżynierów z **end-to-end projektami produkcyjnymi**, nie tutorialami.
Najważniejszy skill w 2026: **RAG** (Retrieval-Augmented Generation).

---

## Rekomendowany projekt: Financial Intelligence Assistant dla złota

### Dlaczego ten projekt?

Mam trzy przewagi, których innym kandydatom brakuje:
1. **Istniejący ML model** — LGBM predykcja kierunku złota (walk-forward, 5 foldów)
2. **Domain expertise w finansach** — 8 lat w banku (PM/BA)
3. **FastAPI + Docker** — już zrobione, to fundament pod deploy

### Co projekt robi (architektura)

```
[Makroekonomiczne dokumenty]       [Model LGBM]
  (raporty Fed, NFP, CPI, itp.)      (predykcja LONG/SHORT)
          ↓                                  ↓
    RAG pipeline                      Sygnał + prawdopodobieństwo
    (LangChain + Qdrant)                     ↓
          ↓                                  ↓
    ←————————————————————————————————————————→
                        ↓
            LLM (GPT / Claude API)
                        ↓
    "Złoto ma sygnał LONG (73%). Oto dlaczego:
     Fed minutes z marca sugerują pivot,
     CPI spada 3 miesiące z rzędu..."
```

### Jakie skille pokazuje (vs. oferty pracy)

| Skill | Wymagany w ofertach | Projekt to pokazuje |
|---|---|---|
| RAG pipeline | #1 najczęściej | TAK — LangChain + Qdrant |
| Vector database | bardzo często | TAK — Qdrant |
| LLM integration | bardzo często | TAK — OpenAI / Claude API |
| FastAPI | standard | TAK — już zrobione |
| Docker | standard | TAK — już zrobione |
| Domain knowledge | rzadkość | TAK — finanse/banking |
| ML model w produkcji | często | TAK — LGBM endpoint |

---

## Odrzucony pomysł: Portfolio Tracker + Sygnały techniczne (analiza maj 2026)

### Opis pomysłu
Tracker pozycji (cena kupna, PnL), watchlist, sygnały MACD/RSI/MFI/MA, wyjaśnienie przez LLM.

### Dlaczego odrzucony

| Problem | Wyjaśnienie |
|---|---|
| Głównie CRUD | Tracker pozycji to baza danych + UI — 60-70% projektu bez wartości AI |
| MACD/RSI to nie ML | Gotowe formuły z biblioteki `ta`, nie ma tu nic do zaimplementowania w AI |
| Bardzo popularna kategoria | Tysiące takich projektów na GitHubie, hiring managerzy mają ich dość |
| Brak RAG | LLM tłumaczący "RSI > 70, sprzedaj" to prosty prompt, nie RAG pipeline |
| Ryzyko scope creep | Duże ryzyko utknięcia na CRUD, nigdy nie dotarcia do części AI |

### Możliwy kompromis (jeśli chcę tracker)
Tracker jako **warstwa UI** na wierzchu projektu złota — watchlist, PnL na pozycji długiej/krótkiej, a sygnał pochodzi z LGBM + RAG. Tracker = frontend, rdzeń = AI. Ale to etap 5+, nie priorytet.

---

## Plan nauki — etapy (do uzupełnienia)

### Etap 1: RAG — podstawy
- [ ] Co to embeddingi i jak działają
- [ ] Vector database — Qdrant lokalnie
- [ ] LangChain — podstawy
- [ ] Prosty RAG: wgraj PDF → zapytaj LLM

### Etap 2: RAG na dokumentach finansowych
- [ ] Pobieranie dokumentów makro (Fed minutes, raporty)
- [ ] Pipeline ingestion (chunking, embeddingi, zapis do Qdrant)
- [ ] Query pipeline z LangChain

### Etap 3: Integracja z modelem LGBM
- [ ] Endpoint FastAPI zwraca sygnał LGBM
- [ ] LangChain łączy sygnał + RAG w jeden prompt dla LLM
- [ ] LLM generuje wyjaśnienie decyzji

### Etap 4: Deploy
- [ ] Docker — pełny stack (FastAPI + Qdrant + LLM)
- [ ] Azure deploy (zgodnie z checklistą)
- [ ] Monitoring podstawowy

### Etap 5: Portfolio
- [ ] GitHub README z architekturą i demo
- [ ] GIF / screenshot z działającego systemu
- [ ] Opis biznesowy: co rozwiązuje, jakie dane, jakie wyniki

---

## Źródła (analiza rynku)

- https://dev.to/klement_gunndu/5-ai-portfolio-projects-that-actually-get-you-hired-in-2026-5bpl
- https://www.the-ai-corner.com/p/ai-engineer-roadmap-production-projects-2026
- https://www.mockexperts.com/blog/2026-ai-engineer-interview-roadmap-rag-llms
- https://www.dataexpert.io/blog/ultimate-guide-ai-engineering-portfolios
