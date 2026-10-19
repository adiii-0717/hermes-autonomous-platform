#!/usr/bin/env python3
"""
APInex Live API Test Script for Hermes
======================================
Tests live communication with the APInex OpenAI-compatible API endpoint
using the local credentials in your environment or .env file.

SECURITY NOTICE:
This script NEVER prints or exposes your raw API key in terminal output or logs.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

# Load .env if present
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip()
            if k not in os.environ:
                os.environ[k] = v

def main():
    api_key = os.getenv("APINEX_API_KEY", "").strip()
    base_url = (os.getenv("APINEX_BASE_URL") or "https://api.apinex.bond/v1").rstrip("/")
    model = os.getenv("APINEX_MODEL", "free/gemini-3.8-flash")

    print("==================================================")
    print(" Hermes - APInex Live API Endpoint Verification")
    print("==================================================")
    print(f" Endpoint:  {base_url}/chat/completions")
    print(f" Model:     {model}")

    if not api_key:
        print("\n❌ ERROR: APINEX_API_KEY is not set.")
        print("Please configure your API key by running:")
        print("  export APINEX_API_KEY=\"your_key_here\"")
        print("or add it to your .env file:")
        print("  APINEX_API_KEY=your_key_here\n")
        sys.exit(1)

    masked_key = (api_key[:4] + "..." + api_key[-4:]) if len(api_key) > 8 else "***"
    print(f" API Key:   {masked_key} (securely loaded)")
    print("\nSending live test prompt to APInex...")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are Hermes assistant. Keep responses under 20 words."},
            {"role": "user", "content": "Confirm you are connected and working via APInex."}
        ],
        "temperature": 0.2
    }

    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "HermesAgent/1.0"
        }
    )

    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            elapsed = time.time() - start_time
            raw = json.loads(resp.read().decode("utf-8"))
            content = raw["choices"][0]["message"]["content"].strip()
            usage = raw.get("usage", {})

            print(f"\n✅ SUCCESS (HTTP {resp.status}) - Latency: {elapsed:.2f}s")
            print(f" Model Returned: {raw.get('model', model)}")
            if usage:
                print(f" Token Usage:    Prompt: {usage.get('prompt_tokens', '?')}, Completion: {usage.get('completion_tokens', '?')}")
            print(f"\n Assistant Response:\n \"{content}\"")
            print("\nAPInex integration is healthy and ready for Hermes agent turns.")

    except urllib.error.HTTPError as err:
        elapsed = time.time() - start_time
        err_msg = ""
        try:
            err_msg = err.read().decode("utf-8", errors="ignore")
        except Exception:
            pass
        print(f"\n❌ API Error: HTTP {err.code} ({err.reason}) after {elapsed:.2f}s")
        if err.code in (401, 403):
            print(" -> Authentication failed. Verify that your APINEX_API_KEY is correct.")
        elif err.code == 402:
            print(" -> Daily check-in required to use free models on APInex.")
            print(" -> Please visit https://apinex.bond/airdrop?tab=quests to check in and unlock your 10M free tokens.")
        elif err.code == 429:
            print(" -> Rate limit or quota exhausted on APInex. Try a different free model or check daily allowance.")
        elif err.code == 404:
            print(f" -> Model '{model}' not found. Check available free models at https://apinex.bond/models.")
        if err_msg:
            try:
                parsed = json.loads(err_msg)
                print(f" Server Message: {parsed.get('error', {}).get('message', err_msg)}")
            except Exception:
                print(f" Raw Details: {err_msg[:250]}")
        sys.exit(2)

    except Exception as exc:
        print(f"\n❌ Network or Connection Failure: {exc}")
        print(" Check your internet connection or verify that https://api.apinex.bond is reachable.")
        sys.exit(3)

if __name__ == "__main__":
    main()
