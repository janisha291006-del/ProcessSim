"""
insights.py - asks Gemini for 4 short insights about the comparison results.

The API key is read from the .env file (GEMINI_API_KEY) and is only used here on the
server, so it is never visible in the browser.
"""
import json
import os
import time

import requests

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# gemini-2.5-flash was retired by Google, so the default is a current model.
# Change it any time with GEMINI_MODEL in the .env file.
DEFAULT_MODEL = "gemini-3.6-flash"
# If the main model is busy (HTTP 503) or retired (HTTP 404), these are tried next
FALLBACK_MODELS = ["gemini-3.5-flash", "gemini-3.1-flash-lite"]
TRIES_PER_MODEL = 2   # a busy model gets a second chance
WAIT_SECONDS = 2      # pause before trying again


# Saved insights: same processes + same quantum -> same insights, and no extra Gemini call.
# It lives in memory only, so it is cleared when the server restarts.
_saved_insights = {}


class InsightError(Exception):
    """A problem we can explain to the user in plain words."""


def _build_prompt(processes, quantum, comparison):
    # Send only the numbers Gemini needs, so the answer stays grounded in our results
    summary = {
        "processes": processes,
        "round_robin_time_quantum": quantum,
        "results": [
            {
                "algorithm": row["label"],
                "avg_waiting_time": row["wt"],
                "avg_turnaround_time": row["tat"],
                "avg_response_time": row["rt"],
                "context_switches": row["context_switches"],
                "waiting_time_per_process": row["wt_by_process"],
            }
            for row in comparison
        ],
    }
    return (
        "You are an Operating Systems teaching assistant. A student ran FCFS, SJF "
        "(non-preemptive), SRTF (preemptive) and Round Robin on the same set of processes. "
        "Here are the results (all times in ms):\n\n"
        f"{json.dumps(summary)}\n\n"
        "Write exactly 4 insights that explain these specific results, in this exact order, "
        "one insight per topic:\n"
        "Insight 1 = which algorithm is best for average waiting/turnaround time and why.\n"
        "Insight 2 = response time and fairness, especially Round Robin and the effect of the time quantum.\n"
        "Insight 3 = the cost of preemption (context switches).\n"
        "Insight 4 = one risk or trade-off visible in this data, such as the convoy effect or starvation of a long job.\n"
        "Do not add, skip, merge or reorder topics.\n"
        "Rules: use the real numbers from the results, never invent numbers. "
        "Each insight has a short title (max 6 words) and a body of 1-2 simple sentences "
        "that a second-year BTech student can understand. Plain text only, no markdown."
    )


def _send_with_retry(api_key, models, body):
    """
    Sends the request to Gemini. A busy model (503) is tried twice, then the next model is used.
    A retired model (404) is skipped straight away. Returns the successful response.
    """
    last_error = None

    for model in models:
        for attempt in range(TRIES_PER_MODEL):
            try:
                res = requests.post(
                    GEMINI_URL.format(model=model),
                    headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                    json=body,
                    timeout=30,
                )
            except requests.exceptions.Timeout:
                last_error = InsightError("Gemini took too long to respond. Please try again.")
                continue
            except requests.exceptions.RequestException:
                raise InsightError("Could not reach Gemini. Check your internet connection.")

            if res.status_code == 200:
                return res

            if res.status_code == 404:  # model retired or not available for this key -> next model
                last_error = InsightError(
                    f"Gemini model '{model}' was not found or has been retired. "
                    "Set GEMINI_MODEL in your .env file to a current model."
                )
                break

            if res.status_code in (500, 503):  # Gemini is busy for a moment -> wait and try again
                last_error = InsightError("Gemini is busy right now. Wait a few seconds and press Try again.")
                if attempt < TRIES_PER_MODEL - 1:  # no point waiting after the last try of this model
                    time.sleep(WAIT_SECONDS)
                continue

            # These will not get better by trying again
            if res.status_code in (400, 403) and "API key" in res.text:
                raise InsightError("Gemini rejected the API key. Check GEMINI_API_KEY in your .env file.")
            if res.status_code == 429:  # this model's quota is used up -> the next model has its own quota
                last_error = InsightError("Gemini rate limit reached. Wait a minute and try again.")
                break
            raise InsightError(f"Gemini returned an error (HTTP {res.status_code}). Please try again.")

    raise last_error


def get_insights(processes, quantum, comparison):
    """Returns a list of 4 dicts: [{"title": "...", "text": "..."}, ...]"""
    key = json.dumps([processes, quantum], sort_keys=True)
    if key in _saved_insights:
        return _saved_insights[key]

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_new_key_here":
        raise InsightError("Gemini API key is missing. Add GEMINI_API_KEY to your .env file and restart the server.")

    first_model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    models = [first_model] + [m for m in FALLBACK_MODELS if m != first_model]

    body = {
        "contents": [{"parts": [{"text": _build_prompt(processes, quantum, comparison)}]}],
        "generationConfig": {
            # Ask Gemini for clean JSON so we do not have to parse free text
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "title": {"type": "STRING"},
                        "text": {"type": "STRING"},
                    },
                    "required": ["title", "text"],
                },
            },
        },
    }

    res = _send_with_retry(api_key, models, body)

    try:
        text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
        items = json.loads(text)
        insights = [
            {"title": str(i["title"]).strip(), "text": str(i["text"]).strip()}
            for i in items
            if str(i.get("title", "")).strip() and str(i.get("text", "")).strip()
        ]
    except (KeyError, IndexError, TypeError, ValueError):
        raise InsightError("Gemini sent an answer we could not read. Please try again.")

    if len(insights) < 4:
        raise InsightError("Gemini returned fewer than 4 insights. Please try again.")
    _saved_insights[key] = insights[:4]  # only good answers are saved, errors are never saved
    return insights[:4]
