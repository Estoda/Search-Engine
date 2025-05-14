# Estoda Search Engine

A web-based search engine built with Django, Docker, and MySQL, supporting crawling, indexing, ranking, and highlighting.

```text
Search-Engine/
│
├── backend/ # Folder for the backend
│ ├── manage.py
│ ├── Dockerfile
│ ├── static/ # Static files (CSS, JS, images)
│ ├── backend/ # Django Django project root
│ │ ├── **init**.py
│ │ ├── requirements.txt
│ │ ├── settings.py
│ │ └── urls.py
│ └── search_app/ # Django app
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── ...
│
├── crawler/
│ ├── crawler.py # Scrapes pages and stores data
│ └── pagerank.py # Computes PageRank using outgoing links
│
├── docker/ # Deployment and Docker configuration
│ └── docker-compose.yml
│
├── docs/ # Documentation files, diagrams, drafts
└── README.md  # Main project documentation
```
---

## Features:
- Async web crawler using `aiohttp` + `playwright` fallback
- Inverted index for full-text search
- PageRank-based result ranking
- Search with keyword highlight
- Stre and manage crawled data in MySQL
- Dockerized backend for easy deployment
- REST API using Django REST Framework

---

## Technologies Used:

- Backend: Django REST Framework
- Database: MySQL (via Docker)
- Crawler: Python + aiohttp + BeautifulSoup + Playwright
- Frontend: HTML/CSS (basic template)
- Deployment: Docker, Docker Compose

---

## Database Schema (ERD):

The following diagram shows the structure of the database and the relationship between entities:
![ERD](docs/ERD.png) 

---

## UI Preview:

![Search UI](docs/UI.png)

---

## Installing and Running the Project:

```bash
git clone https://github.com/Estoda/Search-Engine
cd Search-Engine/docker
docker compose up --build
```

---
## Useful Commands: 

```bash
# Enter the web container:
docker compose exec -it docker-web-1 bash

# Run the migrations:
python manage.py migrate

# Collect static files:
python manage.py collectstatic
```

---

## Crawler Notes:

- Run `crawler/crawler.py` to crawl and store web pages and links.
- Run `crawler/pagerank.py` after crawling to compute PageRank and update database

---

## Docker Image:

This project is available as a public Docker image on Docker Hub:
[https://hub.docker.com/repository/docker/estoda/search-engine-backend/general](https://hub.docker.com/repository/docker/estoda/search-engine-backend/general)

---


## API Documentation:

This project includes auto-generated API documentation using:

- **Swagger UI**: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- **ReDoc** [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

The schema is generated using `drf-yasg`, and documents all available search endpoints and query parameters.