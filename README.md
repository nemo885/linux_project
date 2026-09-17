# Todo List — End-to-End DevOps Project

A simple application consisting of a frontend (HTML/JS), backend (FastAPI), and PostgreSQL database.

The project is initially designed to run without Docker. Later, the same project will be extended with Docker → CI/CD → Ansible → Kubernetes.

---

## Step 1 — Set Up PostgreSQL

Install PostgreSQL:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
```

Log in as the `postgres` system user:

```bash
sudo -u postgres psql
```

Inside `psql`:

```sql
-- Create a user
CREATE USER todouser WITH PASSWORD 'todopass';

-- Create a database
CREATE DATABASE tododb OWNER todouser;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE tododb TO todouser;

-- Exit
\q
```

### Configure PostgreSQL

Find the `pg_hba.conf` file (usually located at `/etc/postgresql/<version>/main/pg_hba.conf`) and make sure it contains:

```text
host    all             all             127.0.0.1/32            md5
```

In `postgresql.conf` (located in the same directory), check that:

```text
listen_addresses = 'localhost'
```

After making the changes, restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

Check that PostgreSQL is listening on port `5432`:

```bash
ss -tulpn | grep 5432
```

---

## Step 2 — Start the Backend

Navigate to the backend directory:

```bash
cd backend
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Copy the example environment configuration:

```bash
cp .env.example .env
```

You can modify the `.env` file according to your configuration.

Export the environment variables:

```bash
export $(cat .env | xargs)
```

Start the backend server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Check that the backend is running and can connect to the database:

```bash
curl http://localhost:8000/api/health
```

The expected response is:

```json
{"status":"ok","db":"connected"}
```

If you get a database connection error, this is useful practice for troubleshooting network and configuration issues.

Check:

```bash
ss -tulpn
```

Make sure the database credentials and database name in `.env` are correct, and verify that PostgreSQL is running:

```bash
sudo systemctl status postgresql
```

---

## Step 3 — Start the Frontend

No build system is required because the frontend is a static HTML application.

Navigate to the frontend directory:

```bash
cd frontend
```

Start a simple HTTP server:

```bash
python3 -m http.server 3000
```

Open the application in your browser:

```text
http://localhost:3000
```

If the frontend cannot connect to the backend, open the browser developer tools (`F12`) and check the console for errors such as CORS or `Connection refused`.

This is also part of the project's troubleshooting practice.

---

## Step 4 — Docker

The application was containerized using Docker.

### Dockerfile

A Dockerfile was created for the backend application.

The Dockerfile:

* Uses a Python base image
* Installs the required dependencies
* Copies the application files into the container
* Exposes the backend port
* Starts the FastAPI application with Uvicorn

Build the Docker image:

```bash
docker build -t todo-backend .
```

Run the container:

```bash
docker run -d -p 8000:8000 --name todo-backend todo-backend
```

Check running containers:

```bash
docker ps
```

Check container logs:

```bash
docker logs todo-backend
```

### Docker Image Layers and Cache

Docker builds images in layers. Each instruction in the Dockerfile creates a layer.

Docker can reuse previously built layers from the build cache, which makes subsequent builds faster.

To build the image without using the cache:

```bash
docker build --no-cache -t todo-backend .
```

Python dependencies are installed using:

```bash
pip install --no-cache-dir -r requirements.txt
```

The `--no-cache-dir` option prevents pip from storing downloaded packages inside the Docker image.

### Docker Registry

The Docker image was also pushed to a container registry.

The workflow is:

```text
Build image
    ↓
Tag image
    ↓
Login to registry
    ↓
Push image
    ↓
Pull image on another machine
    ↓
Run container
```

Example:

```bash
docker tag todo-backend username/todo-backend:latest
docker push username/todo-backend:latest
```

The image can then be downloaded on another machine:

```bash
docker pull username/todo-backend:latest
```

And started with:

```bash
docker run -d -p 8000:8000 --name todo-backend username/todo-backend:latest
```

### Docker Compose

Docker Compose was used to run multiple services together.

The project includes the following services:

* Backend
* PostgreSQL database

Docker Compose makes it possible to configure and start the application and database together instead of running each container manually.

Start the services:

```bash
docker compose up -d
```

Check the services:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs
```

Stop the services:

```bash
docker compose down
```

### Docker Volumes

A Docker volume is used to persist PostgreSQL data.

Without a volume, database data can be lost when the PostgreSQL container is removed.

The volume allows the database data to remain available even when the container is recreated.

### Troubleshooting

During the project, different port conflicts were encountered.

For example, when port `8000` was already being used by another process, the backend port was changed to `8001` instead of stopping the existing application.

The port can be checked with:

```bash
ss -tulpn | grep 8000
```

This helped practice real-world troubleshooting of processes, ports, containers, and service configuration.


