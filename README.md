# Todo List — сквозной DevOps-проект

Простое приложение: **фронтенд (HTML/JS) + бэкенд (FastAPI) + PostgreSQL**.
Никакого Docker — запускается голыми руками. Дальше этот же проект
пойдёт в Docker → CI/CD → Ansible → Kubernetes.

---

## Шаг 1 — Поднять PostgreSQL

```bash
# Установить
sudo apt update
sudo apt install postgresql postgresql-contrib -y

# Зайти под системным пользователем postgres
sudo -u postgres psql
```

Дальше внутри psql:

```sql
-- Создать пользователя
CREATE USER todouser WITH PASSWORD 'todopass';

-- Создать базу
CREATE DATABASE tododb OWNER todouser;

-- Выдать права
GRANT ALL PRIVILEGES ON DATABASE tododb TO todouser;

-- Выйти
\q
```

**Открыть порт (разрешить подключение с localhost по паролю):**

Найди файл `pg_hba.conf` (обычно `/etc/postgresql/<версия>/main/pg_hba.conf`) и убедись, что там есть строка:
```
host    all             all             127.0.0.1/32            md5
```

И в `postgresql.conf` (там же) проверь, что:
```
listen_addresses = 'localhost'
```

После правки — перезапустить:
```bash
sudo systemctl restart postgresql
```

Проверить, что порт 5432 слушается:
```bash
ss -tulpn | grep 5432
```

---

## Шаг 2 — Запустить backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Скопировать пример настроек (можно менять под себя)
cp .env.example .env

# Экспортировать переменные окружения (или используй python-dotenv, если хочешь автоматом)
export $(cat .env | xargs)

# Запустить сервер
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Проверить, что бэкенд живой и видит базу:
```bash
curl http://localhost:8000/api/health
```
Должно вернуть `{"status":"ok","db":"connected"}`.

Если получаешь ошибку подключения — это и есть та самая "практика с проблемами"
из блока Сети: проверяй `ss -tulpn`, правильность пароля/имени БД в `.env`,
и что PostgreSQL вообще запущен (`sudo systemctl status postgresql`).

---

## Шаг 3 — Запустить frontend

Никакого сборщика не нужно — это просто статический HTML.

```bash
cd frontend
python3 -m http.server 3000
```

Открой в браузере: **http://localhost:3000**

Если фронтенд не видит бэкенд — открой консоль браузера (F12), посмотри на
ошибки CORS/Connection refused. Это тоже часть практики диагностики.

---

## Что дальше по роадмапу

- Упаковать backend и frontend каждый в свой Dockerfile
- Прогнать через `docker-compose` вместе с PostgreSQL
- Настроить Nginx как reverse proxy перед этим всем
- Собрать CI/CD пайплайн (build → test → deploy)
- Задеплоить в Kubernetes (Ansible → манифесты → Helm chart)
