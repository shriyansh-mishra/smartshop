import os
import asyncio
import json
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse, parse_qs
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET
from django.core.cache import cache
from asgiref.sync import sync_to_async

import aiohttp
from aiohttp import ClientTimeout
from bs4 import BeautifulSoup

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
CACHE_TTL_SECONDS = 300
REQUEST_TIMEOUT = 10


# --- Utility to extract weight from product name ---
def _extract_weight(text: Optional[str]) -> Optional[str]:
    import re
    if not text:
        return None

    # Normalize
    text = re.sub(r"\s+", " ", text)
    text = text.replace("×", "x")  # unify multiplication sign

    # Common units and synonyms
    unit_map = {
        "gallon": "gal",
        "gallons": "gal",
        "liter": "l",
        "liters": "l",
        "milliliter": "ml",
        "milliliters": "ml",
        "lb.": "lb",
        "lbs": "lb",
        "oz.": "oz",
        "fl. oz": "fl oz",
        "fl.oz": "fl oz",
    }

    def norm_unit(u: str) -> str:
        u = u.lower().strip()
        u = unit_map.get(u, u)
        return u

    # Multipack like "12 x 12 oz" or "12x12oz"
    m = re.search(r"(\d+)\s*[xX]\s*(\d+(?:\.\d+)?)\s*(fl\.?\s*oz|oz\.?,?|lb\.?,?|lbs\b|g\b|kg\b|ml\b|l\b|gallon|gallons|gal)", text, re.I)
    if m:
        count = int(m.group(1))
        qty = float(m.group(2))
        unit = norm_unit(m.group(3))
        total = qty * count
        return f"{count} x {qty:g} {unit} ({total:g} {unit})"

    # "Pack of 2 1 lb" or "2 pack 1 lb"
    m = re.search(r"(pack of\s*(\d+)|\b(\d+)\s*pack)\D+(\d+(?:\.\d+)?)\s*(fl\.?\s*oz|oz\.?,?|lb\.?,?|lbs\b|g\b|kg\b|ml\b|l\b|gallon|gallons|gal)", text, re.I)
    if m:
        count = int(m.group(2) or m.group(3))
        qty = float(m.group(4))
        unit = norm_unit(m.group(5))
        total = qty * count
        return f"{count} x {qty:g} {unit} ({total:g} {unit})"

    # Number immediately followed by unit like "16oz" or with optional dot/space variants
    m = re.search(r"(\d+(?:\.\d+)?)\s*(fl\.?\s*oz|oz\.?,?|lb\.?,?|lbs\b|g\b|kg\b|ml\b|l\b|gallon|gallons|gal)", text, re.I)
    if m:
        qty = float(m.group(1))
        unit = norm_unit(m.group(2))
        return f"{qty:g} {unit}"

    # Count-only like "12 ct" / "12 count"
    m = re.search(r"(\d+)\s*(ct|count)\b", text, re.I)
    if m:
        return f"{m.group(1)} ct"

    return None


def _extract_weight_from_extensions(extensions: Optional[List[str]]) -> Optional[str]:
    """Attempt to extract weight from SerpAPI extensions list."""
    if not extensions:
        return None
    for ext in extensions:
        w = _extract_weight(ext)
        if w:
            return w
    return None


# --- SerpAPI fetch ---
async def fetch_serpapi(query: str) -> List[Dict]:
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_shopping",
        "q": query,
        "hl": "en",
        "gl": "us",
        "api_key": SERPAPI_KEY.strip('"') if SERPAPI_KEY else None,
        "num": 20,
    }
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
    except Exception:
        return []

    results: List[Dict] = []
    for item in data.get("shopping_results", []):
        title = item.get("title")
        price = item.get("price") or item.get("extracted_price")
        vendor = item.get("source")
        link = item.get("link") or item.get("product_link")
        weight = _extract_weight(title) or _extract_weight_from_extensions(item.get("extensions"))
        results.append({
            "name": title,
            "price": price,
            "vendor": vendor,
            "link": link,
            "weight": weight,
        })
    return results


# --- HTML fallback scraping ---
async def fetch_html_shopping(query: str) -> List[Dict]:
    query_str = query.replace(" ", "+")
    url = f"https://www.google.com/search?tbm=shop&q={query_str}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return []
                html = await resp.text()
    except Exception:
        return []

    soup = BeautifulSoup(html, "lxml")
    results = []
    cards = soup.select("div.sh-dgr__grid-result") or soup.select("div.sh-pr__product-results li, div.sh-dlr__list-result")
    for card in cards:
        name = card.select_one(".tAxDx, .sh-np__product-title, h3")
        price = card.select_one(".a8Pemb, .hrTbp, .T14wmb")
        vendor = card.select_one(".aULzUe, .E5ocAb")
        link_el = card.select_one("a")

        href: Optional[str] = None
        if link_el and link_el.has_attr("href"):
            raw = link_el["href"]
            if raw.startswith("/url?"):
                q = parse_qs(urlparse(raw).query).get("q", [None])[0]
                href = q
            elif raw.startswith("/"):
                href = urljoin("https://www.google.com", raw)
            else:
                href = raw
        results.append({
            "name": name.get_text(strip=True) if name else None,
            "price": price.get_text(strip=True) if price else None,
            "vendor": vendor.get_text(strip=True) if vendor else None,
            "link": href,
            "weight": _extract_weight(name.get_text(strip=True) if name else None),
        })
    return results


# --- Dispatcher: try SerpAPI, fallback to scraping ---
async def fetch_from_sources(query: str) -> List[Dict]:
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = []
        if SERPAPI_KEY:
            tasks.append(asyncio.create_task(fetch_serpapi(query)))
        tasks.append(asyncio.create_task(fetch_html_shopping(query)))

        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        serp_results: List[Dict] = []
        html_results: List[Dict] = []

        idx = 0
        if SERPAPI_KEY:
            first = results_list[idx]
            idx += 1
            if not isinstance(first, Exception):
                serp_results = first or []
        second = results_list[idx]
        if not isinstance(second, Exception):
            html_results = second or []

        return serp_results or html_results


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
