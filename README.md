🛍️ Smart Shop API 

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![aiohttp](https://img.shields.io/badge/aiohttp-3.x-2C5BB4)](https://docs.aiohttp.org/)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.x-4E9A06)](https://www.crummy.com/software/BeautifulSoup/)
[![lxml](https://img.shields.io/badge/lxml-6.x-0A0A0A)](https://lxml.de/)
[![Code Style: Prettier](https://img.shields.io/badge/Code%20Style-Prettier-ff69b4?logo=prettier&logoColor=white)](https://prettier.io/)
[![Repo size](https://img.shields.io/github/repo-size/OWNER/REPO)](https://github.com/OWNER/REPO)
[![Postman](https://img.shields.io/badge/Postman-Open%20in%20Postman-orange?logo=postman&logoColor=white)](https://www.postman.com/collections/YOUR_COLLECTION_UID)

Simple Django API that searches Google Shopping via SerpAPI (with HTML scraping fallback). Returns product name, price, vendor, link, and a best‑effort weight extracted from the title.

⬇️ Clone

```bash
git clone https://github.com/shriyansh-mishra/smartshop
cd smartshop
```

🔎 Sample queries and JSON output

Success

```text
q=365 WholeFoods Peanut Butter
```

```json
{
  "query": "365 WholeFoods Peanut Butter",
  "cached": false,
  "results": [
    {
      "name": "365 by Whole Foods Market, Organic Peanut Butter, 16 oz",
      "price": "$4.99",
      "vendor": "Whole Foods",
      "link": "https://example.com/product/1",
      "weight": "16 oz"
    }
  ]
}
```

Error (missing query param `q`)

Request without `q`:

```text
/api/search/
```

Response (HTTP 400):

```json
{
  "error": "query param 'q' is required"
}
```

📬 Open in Postman

- Direct link (replace with your public Postman collection link):
  - https://www.postman.com/collections/YOUR_COLLECTION_UID
- Or create a simple GET request to:
  - `http://127.0.0.1:8000/api/search/?q=365%20WholeFoods%20Peanut%20Butter`

🤝 Contributing

1) Fork the repo and create a feature branch.
2) Keep changes focused and documented in the PR description.
3) Run the app locally and verify the `/api/search` endpoint works.
4) Submit a PR; include screenshots or sample responses if UI/data changes.

Nice-to-have guidelines:
- Add or update tests if logic changes.
- Keep README snippets runnable.
- Avoid committing databases or secrets.

Made with ❤️ [mishrashriyansh@outlook.com](mailto:mishrashriyansh@outlook.com)


