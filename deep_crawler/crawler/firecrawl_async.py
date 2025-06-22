import asyncio
import aiohttp
import time
import hashlib
from .extractor import simple_extract, looks_dynamic
from pathlib import Path
import toml
import json

CFG = toml.load(Path(__file__).parents[2] / "config.toml")
FC = CFG["firecrawl"]["base_url"]

async def _fc_submit(session, url, limit):
    r = await session.post(f"{FC}/v1/crawl", json={"url": url, "limit": limit})
    js = await r.json()
    return js["id"]

async def _fc_poll(session, jid, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        r = await session.get(f"{FC}/v1/crawl/{jid}")
        js = await r.json()
        if js["status"] == "completed":
            return js["pages"]
        if js["status"] == "failed":
            raise RuntimeError("Firecrawl job failed")
        await asyncio.sleep(2)
    raise TimeoutError("Firecrawl job timeout")

async def _handle_one(session, url, limit):
    try:
        jid = await _fc_submit(session, url, limit)
        return await _fc_poll(session, jid)
    except Exception:
        # static fallback
        return [simple_extract(url)]

async def crawl_urls(urls, limit=None, concurrency=None):
    limit = limit or CFG["firecrawl"]["limit_per_url"]
    concurrency = concurrency or CFG["firecrawl"]["concurrency"]
    sem = asyncio.Semaphore(concurrency)
    pages = []

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(30)) as s:
        async def worker(u):
            async with sem:
                try:
                    return await _handle_one(s, u, limit)
                except Exception:
                    return []

        tasks = [worker(u) for u in urls]
        for coro in asyncio.as_completed(tasks):
            pages += await coro
    return pages
