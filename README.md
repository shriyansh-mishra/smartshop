Smart Shopper P1

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![aiohttp](https://img.shields.io/badge/aiohttp-3.x-2C5BB4)](https://docs.aiohttp.org/)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.x-4E9A06)](https://www.crummy.com/software/BeautifulSoup/)
[![lxml](https://img.shields.io/badge/lxml-6.x-0A0A0A)](https://lxml.de/)
[![Code Style: Prettier](https://img.shields.io/badge/Code%20Style-Prettier-ff69b4?logo=prettier&logoColor=white)](https://prettier.io/)
[![Repo size](https://img.shields.io/github/repo-size/OWNER/REPO)](https://github.com/OWNER/REPO)
[![Postman](https://img.shields.io/badge/Postman-Open%20in%20Postman-orange?logo=postman&logoColor=white)](https://www.postman.com/collections/YOUR_COLLECTION_UID)

Simple Django API that searches Google Shopping via SerpAPI (with HTML scraping fallback). Returns product name, price, vendor, link, and a best‑effort weight extracted from the title.

Clone

```bash
git clone https://github.com/OWNER/REPO.git
cd REPO
```

Setup

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
echo "DJANGO_SECRET_KEY=dev-secret\nDEBUG=true\nSERPAPI_API_KEY=your_serpapi_key_here" > .env
python manage.py migrate
python manage.py runserver
```

Use the API

```bash
curl "http://127.0.0.1:8000/api/search/?q=365%20WholeFoods%20Peanut%20Butter"
```

If you see empty results, verify your `SERPAPI_API_KEY` has quota and works by calling SerpAPI directly with your key.

Open in Postman

- Direct link (replace with your public Postman collection link):
  - https://www.postman.com/collections/YOUR_COLLECTION_UID
- Or create a simple GET request to:
  - `http://127.0.0.1:8000/api/search/?q=365%20WholeFoods%20Peanut%20Butter`


