## 🛍️ Smart Shop API 

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![aiohttp](https://img.shields.io/badge/aiohttp-3.x-2C5BB4)](https://docs.aiohttp.org/)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.x-4E9A06)](https://www.crummy.com/software/BeautifulSoup/)
[![lxml](https://img.shields.io/badge/lxml-6.x-0A0A0A)](https://lxml.de/)
[![Code Style: Prettier](https://img.shields.io/badge/Code%20Style-Prettier-ff69b4?logo=prettier&logoColor=white)](https://prettier.io/)
[![Repo size](https://img.shields.io/github/repo-size/shriyansh-mishra/smartshop)](https://github.com/shriyansh-mishra/smartshop)
[![Postman](https://img.shields.io/badge/Postman-Open%20in%20Postman-orange?logo=postman&logoColor=white)](https://blue-water-347559.postman.co/workspace/Student-expert-API~2d5343ae-3527-4ba7-8090-4a4fafe80bfa/collection/42614502-4caa142b-ce17-4fbd-b539-6acf3b76a92a?action=share&creator=42614502)

Simple Django API that searches Google Shopping via SerpAPI (with HTML scraping fallback). Returns product name, price, vendor, link, and a best‑effort weight extracted from the title.

### *Demo Video 👇🏻*
<a href="https://www.loom.com/share/378f034f354e4b0ab77da24a13bc7b46?sid=bc9e431f-4fe9-4ba6-8b8e-3bbfd88d375d">
  <img src="https://tse3.mm.bing.net/th/id/OIP.1KSc1AX282HhOEkQdkws3QHaCS?w=1217&h=375&rs=1&pid=ImgDetMain&o=7&rm=3" alt="Loom" width="90"/>
</a>

>
⬇️ Clone

```bash
git clone https://github.com/shriyansh-mishra/smartshop
cd smartshop
```
### ⚠️ Caution 

```code
Some products weight will show null, the data likely doesn't include size.
The request may take 15-30 sec as of cold start.
```

🔎 Sample queries and JSON output

API Endpoint

`https://smartshop-kzgm.onrender.com/api/search/?q=365+WholeFoods+Peanut+Butter
`

```json
{
  "query": "365 WholeFoods Peanut Butter",
  "cached": false,
  "results": [
    {
      "name": "365 by Whole Foods Market, Organic Peanut Butter",
      "price": "$4.99",
      "vendor": "Whole Foods",
      "link": "https://www.google.com/shopping/product/5488843124821120299?gl=us",
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

- Create a simple GET request to:
  - `https://smartshop-kzgm.onrender.com/api/search/?q=365+WholeFoods+Peanut+Butter` 

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
> Streamlit UI for api response comming soon!!!
