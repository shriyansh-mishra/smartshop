import os
import asyncio
import json
from typing import List, Dict, Optional
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET
from django.core.cache import cache
from asgiref.sync import sync_to_async

import aiohttp
from bs4 import BeautifulSoup

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
CACHE_TTL_SECONDS = 300
REQUEST_TIMEOUT = 10


# --- Utility to extract weight from product name ---
def _extract_weight(name: Optional[str]) -> Optional[str]:
    import re
    if not name:
        return None
    m = re.search(r'(\d+(\.\d+)?)\s*(kg|g|oz|lb)', name, re.I)
    return m.group(0) if m else None


# --- SerpAPI fetch ---
async def fetch_serpapi(query: str) -> List[Dict]:
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_shopping",
        "q": query,
        "hl": "en",
        "gl": "us",
        "api_key": SERPAPI_KEY.strip('"') if SERPAPI_KEY else None,  # remove quotes if present
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=REQUEST_TIMEOUT) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            results = []
            for item in data.get("shopping_results", []):
                results.append({
                    "name": item.get("title"),
                    "price": item.get("price"),
                    "vendor": item.get("source"),
                    "link": item.get("link"),
                    "weight": _extract_weight(item.get("title")),
                })
            return results


# --- HTML fallback scraping ---
async def fetch_html_shopping(query: str) -> List[Dict]:
    query_str = query.replace(" ", "+")
    url = f"https://www.google.com/search?tbm=shop&q={query_str}"
    headers = {"User-Agent": "Mozilla/5.0"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=REQUEST_TIMEOUT) as resp:
            html = await resp.text()

    soup = BeautifulSoup(html, "lxml")
    results = []
    for card in soup.select("div.sh-dgr__grid-result"):
        name = card.select_one(".tAxDx")
        price = card.select_one(".a8Pemb")
        vendor = card.select_one(".aULzUe")
        link = card.select_one("a")
        results.append({
            "name": name.get_text(strip=True) if name else None,
            "price": price.get_text(strip=True) if price else None,
            "vendor": vendor.get_text(strip=True) if vendor else None,
            "link": link["href"] if link and link.has_attr("href") else None,
            "weight": _extract_weight(name.get_text(strip=True) if name else None),
        })
    return results


# --- Dispatcher: try SerpAPI, fallback to scraping ---
async def fetch_from_sources(query: str) -> List[Dict]:
    if SERPAPI_KEY:
        results = await fetch_serpapi(query)
        if results:  # only fallback if SerpAPI fails or empty
            return results
    return await fetch_html_shopping(query)


# --- API endpoint ---
@require_GET
async def search_products(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return HttpResponseBadRequest(
            json.dumps({"error": "query param 'q' is required"}),
            content_type="application/json",
        )

    cache_key = f"product_search:{query.lower()}"
    cached = await sync_to_async(cache.get)(cache_key)
    if cached:
        return JsonResponse({"query": query, "cached": True, "results": cached})

    results = await fetch_from_sources(query)

    await sync_to_async(cache.set)(cache_key, results, CACHE_TTL_SECONDS)
    return JsonResponse({"query": query, "cached": False, "results": results})
