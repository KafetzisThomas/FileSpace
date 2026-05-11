<div align="center">
    <h1>FileSpace</h1>
    <p>Simple personal file storage.<br>Written in Python/Django</p>
    <img src="https://img.shields.io/badge/Docker-Enabled-blue?logo=docker"/>
</div>

## Usage

### Local Development

First install `uv` and sync the project dependencies:

```bash
cd path/to/root/directory
pip install uv
uv sync
```

Migrate database:

```bash
uv run manage.py migrate
```

Run Django server:

```bash
uv run manage.py runserver
```

Access web application at `http://127.0.0.1:8000` or `http://localhost:8000`.

### Production Deployment (Docker)

Set up your environment variables:

```bash
cp .env.prod .env
nano .env  # modify file, instructions inside
```

Build and start the container in the background:

```bash
docker compose up -d --build
```

Access web application at `http://127.0.0.1:8001` or `http://localhost:8001`.
