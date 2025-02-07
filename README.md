# Python Flask Backend - README

## 📌 Opis

Ten moduł to backend aplikacji napisany w Pythonie z wykorzystaniem **Flask**. Aplikacja jest konteneryzowana za pomocą **Dockera** i udostępnia API na porcie `5000`.

---

## 🛠 Wymagania

Przed uruchomieniem upewnij się, że masz zainstalowane:

- **Docker** (jeśli nie masz, zobacz: [Docker Install](https://docs.docker.com/get-docker/))
- **Python 3.12** (jeśli chcesz uruchomić aplikację lokalnie)
- **pip** (zarządzanie pakietami Pythona)
- **Node.js & npm** (dla obsługi skryptów w `font_extractor/svg_parser/mat-js`)

---

## 🚀 Uruchomienie w Dockerze

### 1️⃣ Budowa obrazu Dockera

W katalogu głównym projektu uruchom:

```sh
docker build -t python-api .
```

### 2️⃣ Uruchomienie kontenera

```sh
docker run -it -p 5000:5000 python-api
```

Aplikacja będzie dostępna pod adresem:

```
http://localhost:5000
```

---

## 🖥 Uruchomienie lokalne (bez Dockera)

Jeśli chcesz uruchomić aplikację lokalnie, wykonaj poniższe kroki.

### 1️⃣ Instalacja zależności

```sh
pip install -r requirements.txt
```

Dodatkowo, zainstaluj wymagane pakiety systemowe:

```sh
sudo apt update && sudo apt install -y pdf2svg fontforge
```

### 2️⃣ Instalacja Node.js i modułów JS

```sh
cd font_extractor/svg_parser/mat-js
npm install
cd ../../../
```

### 3️⃣ Uruchomienie aplikacji Flask

```sh
flask run --host=0.0.0.0 --port=5000
```

---

## 🛠 Struktura projektu

```
/app
│── /font_extractor
│   ├── /svg_parser
│   │   ├── /mat-js (moduł JS)
│── app.py (główny plik aplikacji Flask)
│── requirements.txt (zależności Pythona)
│── Dockerfile (definicja kontenera)
│── README.md (dokumentacja)
```

---

## 🛠 Technologie

- **Python 3.12**
- **Flask**
- **Gunicorn** (serwer WSGI)
- **Node.js** (do obsługi części `mat-js`)
- **Docker**

---

## 🛠 Konfiguracja środowiska

Możesz dostosować konfigurację aplikacji poprzez zmienne środowiskowe:

| Zmienna         | Domyślna wartość | Opis                                  |
|----------------|----------------|----------------------------------------|
| `PORT`         | `5000`         | Port, na którym działa aplikacja      |
| `FLASK_APP`    | `app.py`       | Plik startowy aplikacji Flask         |
| `FLASK_RUN_HOST` | `0.0.0.0`    | Adres IP dla Flask                    |

Jeśli chcesz zmienić domyślny port, uruchom:

```sh
docker run -it -p 8080:5000 -e PORT=8080 python-api
```

---

## ✅ Testowanie API

Po uruchomieniu aplikacji możesz sprawdzić jej działanie, wykonując zapytanie:

```sh
curl http://localhost:5000/
```

Jeśli aplikacja działa poprawnie, powinna zwrócić odpowiedź HTTP `200 OK`.

---

## 📜 Licencja

Projekt jest dostępny na licencji **MIT**.

---
📅 Ostatnia aktualizacja: **2025**