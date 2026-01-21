import json
import time
from datetime import datetime
import os
from django.conf import settings


def _usage_path():
    try:
        base = settings.BASE_DIR
    except Exception:
        base = os.getcwd()
    return os.path.join(str(base), "ai_api_usage.log")


def log_api_call(kind, model=None, prompt_text=None, response=None, extra=None):
    """Append a JSON line with basic telemetry about an API call.

    kind: 'chat'|'transcription'|'tts' etc.
    model: model name string
    prompt_text: (optional) text sent to API (will log length only)
    response: (optional) API response object; if it has a .usage attribute we'll log it
    extra: optional dict for any other fields
    """
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "kind": kind,
        "model": model,
        "prompt_len": len(prompt_text) if prompt_text else None,
        "extra": extra or {}
    }

    # Try to extract usage information if available
    try:
        if response is not None:
            # Some SDK responses expose .usage or .get("usage")
            usage = None
            if hasattr(response, "usage"):
                usage = response.usage
            elif isinstance(response, dict) and "usage" in response:
                usage = response.get("usage")
            elif hasattr(response, "choices") and hasattr(response.choices[0], "usage"):
                usage = response.choices[0].usage

            if usage:
                # usage may have keys like prompt_tokens, completion_tokens, total_tokens
                try:
                    entry["usage"] = {
                        k: int(v) for k, v in dict(usage).items()
                    }
                except Exception:
                    entry["usage"] = str(usage)
    except Exception:
        pass

    try:
        path = _usage_path()
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, default=str) + "\n")
    except Exception:
        # Fail silently; telemetry must not break app
        pass
