# Warstwa 1: bazowy obraz — Python 3.12 w wersji slim (bez zbędnych narzędzi systemowych)
# "slim" waży ~150MB zamiast ~1GB pełnej wersji
FROM python:3.12-slim

# Warstwa 2: ustaw katalog roboczy wewnątrz kontenera
# Wszystkie kolejne komendy będą wykonywane z tego miejsca
# Odpowiednik "cd /app" — jeśli folder nie istnieje, Docker go tworzy
WORKDIR /app

# Warstwa 3: zainstaluj systemowe zależności których wymaga LightGBM
# libgomp1 = biblioteka OpenMP do równoległego przetwarzania (wymagana przez LightGBM)
# rm -rf /var/lib/apt/lists/* = usuń cache apt po instalacji (mniejszy rozmiar obrazu)
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

# Warstwa 4: skopiuj TYLKO requirements.txt (jeszcze nie cały kod)
# Dzięki temu Docker cache'uje warstwę z pip install —
# jeśli zmienisz tylko kod (nie pakiety), ta warstwa nie będzie przebudowywana
COPY requirements.txt .

# Warstwa 5: zainstaluj pakiety Pythona
# --no-cache-dir = nie przechowuj cache pip w obrazie (mniejszy rozmiar)
RUN pip install --no-cache-dir -r requirements.txt

# Warstwa 5: skopiuj resztę projektu do kontenera
# . (źródło) = cały bieżący katalog na Twoim komputerze
# . (cel)    = /app wewnątrz kontenera (WORKDIR)
COPY . .

# Warstwa 6: port na którym nasłuchuje uvicorn wewnątrz kontenera
# To tylko dokumentacja — informuje Dockera że aplikacja używa portu 8000
# Nie otwiera portu automatycznie — to robi "docker run -p"
EXPOSE 80

# Warstwa 7: komenda która odpala się gdy kontener startuje
# Bez --reload bo to środowisko produkcyjne, nie developerskie
# --host 0.0.0.0 = nasłuchuj na wszystkich interfejsach sieciowych kontenera
#                  bez tego kontener nie byłby dostępny z zewnątrz
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "80"]
