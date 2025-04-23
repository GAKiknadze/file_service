# File Service

[![Run tests and upload coverage](https://github.com/GAKiknadze/file_service/actions/workflows/test.yml/badge.svg)](https://github.com/GAKiknadze/file_service/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/GAKiknadze/file_service/graph/badge.svg?token=32FBC0EVSN)](https://codecov.io/gh/GAKiknadze/file_service)

File Service is a microservice for handling file uploads, storage, and metadata management.

## Features

- File upload and download
- Metadata management
- S3-compatible storage support
- Async operations with Celery
- PostgreSQL for metadata storage

## Requirements

- Python 3.10+
- [Poetry](https://python-poetry.org/)
- [PoeThePoet](https://poethepoet.natn.io/index.html)
- PostgreSQL 15+
- Redis
- MinIO (or other S3-compatible storage)
- Docker and Docker Compose (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/GAKiknadze/file_service.git
cd file_service
```

2. Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install PoeThePoet:
```bash
pip install poethepoet # As dependency
poetry self add 'poethepoet[poetry_plugin]' # As poetry plugin
```

4. Install dependencies:
```bash
poetry install
```

5. Activate virtual environment:
```bash
poetry shell
```

6. Copy configuration example and adjust settings:
```bash
cp configs/config.example.yaml configs/config.yaml
```

## Running with Docker

1. Make the entrypoint script executable:

```bash
chmod +x entrypoint.sh
```

2. Build container:

```bash
docker build -t file-service .
```

3. Run Rest service:

```bash
docker run -p 8000:8000 file-service api
```

4. Run Celery Worker service:

```bash
docker run file-service worker
```

## Running with Docker Compose

Start all services using Docker Compose:

```bash
docker-compose up -d
```

## Manual Setup

1. Configure PostgreSQL database
2. Set up MinIO or S3 storage
3. Configure Redis for Celery
4. Update config.yaml with your settings

## Environment Variables

Required environment variables:
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `MINIO_ROOT_USER`
- `MINIO_ROOT_PASSWORD`
- `CONFIG_FILE`

## Development

### Running Tests

```bash
poe test
```

### Code Formatting
```bash
poe format
```

### Code Style

```bash
poe check
```

### Run Rest Server

```bash
poe run_dev
```

### Run Celery Worker

```bash
poe run_worker
```

## API Documentation

The service provides the following endpoints:
| Method | URL | Description |
|-|-|-|
| `GET` | `/api/v1/file` | List files |
| `POST` | `/api/v1/file` | Upload new file |
| `GET` | `/api/v1/file/{file_id}` | Download file |
| `GET` | `/api/v1/file/{file_id}/info` | Get file info |
| `DELETE` | `/api/v1/file/{file_id}` | Delete file |

## Contributing

1. Fork the repository
2. Create your feature branch
3. Run tests and linting
4. Submit a pull request

## License

This project is licensed under the MPL-2.0 license - see the [`LICENSE`](./LICENSE) file for details.

