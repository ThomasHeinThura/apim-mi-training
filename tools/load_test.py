#!/usr/bin/env python3
"""Simple async load tester for a list of HTTP endpoints.

Usage:
  pip install aiohttp
  python tools/load_test.py --endpoints tools/endpoints.json --concurrency 50 --requests 200

The endpoints JSON should be an array of objects like:
  [{"name": "Petstore", "method": "GET", "url": "http://localhost:5007/api/v3/openapi.json"}, ...]

The script runs the specified number of requests per endpoint with a global concurrency limit
and prints a simple latency/status summary.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from collections import defaultdict
from typing import List, Dict, Any

import aiohttp


def load_endpoints(path: str) -> List[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("endpoints file must contain a JSON array")
            return data
    except FileNotFoundError:
        print(f"Endpoints file not found: {path}")
        raise


async def fetch(session: aiohttp.ClientSession, method: str, url: str, timeout: int) -> Dict[str, Any]:
    ts = time.perf_counter()
    try:
        async with session.request(method.upper(), url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
            await resp.read()
            elapsed = (time.perf_counter() - ts) * 1000.0
            return {"ok": True, "status": resp.status, "elapsed_ms": elapsed}
    except Exception as e:
        elapsed = (time.perf_counter() - ts) * 1000.0
        return {"ok": False, "error": str(e), "elapsed_ms": elapsed}


async def run_endpoint(name: str, method: str, url: str, requests: int, semaphore: asyncio.Semaphore, session: aiohttp.ClientSession, timeout: int) -> Dict[str, Any]:
    results = []

    async def worker(i: int):
        async with semaphore:
            r = await fetch(session, method, url, timeout)
            results.append(r)

    tasks = [asyncio.create_task(worker(i)) for i in range(requests)]
    await asyncio.gather(*tasks)

    return {"name": name, "url": url, "results": results}


def summarize_endpoint(data: Dict[str, Any]) -> Dict[str, Any]:
    res = data["results"]
    latencies = [r["elapsed_ms"] for r in res if "elapsed_ms" in r]
    statuses = defaultdict(int)
    errors = 0
    for r in res:
        if r.get("ok"):
            statuses[r.get("status")] += 1
        else:
            errors += 1
            statuses["error"] += 1

    lat_sorted = sorted(latencies)
    def pct(p: float) -> float:
        if not lat_sorted:
            return 0.0
        idx = min(int(len(lat_sorted) * p / 100.0), len(lat_sorted) - 1)
        return lat_sorted[idx]

    return {
        "name": data["name"],
        "url": data["url"],
        "total": len(res),
        "errors": errors,
        "statuses": dict(statuses),
        "avg_ms": (sum(lat_sorted) / len(lat_sorted)) if lat_sorted else 0.0,
        "p50_ms": pct(50),
        "p95_ms": pct(95),
        "p99_ms": pct(99),
    }


async def run_all(endpoints: List[Dict[str, Any]], concurrency: int, requests_per_endpoint: int, timeout: int):
    semaphore = asyncio.Semaphore(concurrency)
    connector = aiohttp.TCPConnector(limit=0)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for ep in endpoints:
            name = ep.get("name") or ep.get("url")
            method = ep.get("method", "GET")
            url = ep.get("url")
            tasks.append(run_endpoint(name, method, url, requests_per_endpoint, semaphore, session, timeout))

        results = await asyncio.gather(*tasks)

    summary = [summarize_endpoint(r) for r in results]
    print(json.dumps({"summary": summary}, indent=2))


def default_endpoints() -> List[Dict[str, Any]]:
    return [
        {"name": "Petstore (backend)", "method": "GET", "url": "http://localhost:5007/api/v3/openapi.json"},
        {"name": "Petstore (APIM)", "method": "GET", "url": "http://localhost:8280/petstore/1.0.0/api/v3/openapi.json"},
    ]


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoints", help="Path to endpoints JSON file", default=None)
    parser.add_argument("--concurrency", help="Global concurrency", type=int, default=50)
    parser.add_argument("--requests", help="Requests per endpoint", type=int, default=100)
    parser.add_argument("--timeout", help="Per-request timeout in seconds", type=int, default=20)
    args = parser.parse_args(argv)

    if args.endpoints:
        endpoints = load_endpoints(args.endpoints)
    else:
        endpoints = default_endpoints()

    try:
        asyncio.run(run_all(endpoints, args.concurrency, args.requests, args.timeout))
        return 0
    except KeyboardInterrupt:
        print("Interrupted")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
