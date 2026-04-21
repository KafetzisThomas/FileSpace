<div align="center">
    <h1>FileSpace</h1>
    <p>Simple personal file storage.<br>Written in Python/Django</p>
</div>

## Usage

### Install dependencies

```bash
cd path/to/root/directory
pip install uv
uv sync
```

### Environment Setup

```bash
cp .env.example .env
nano .env  # modify file, instructions inside
```

### Migrate Database

```bash
uv run manage.py migrate
```

### Run Django Server

```bash
uv run manage.py runserver
```

Access web application at `http://127.0.0.1:8000` or `http://localhost:8000`.
