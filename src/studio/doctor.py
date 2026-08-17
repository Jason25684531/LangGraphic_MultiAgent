import sys
import json
from urllib.request import urlopen

from pydantic import BaseModel

from studio.config import StudioSettings
from studio.models.factory import create_chat_model
from studio.tools.example_tools import get_magic_number


class DiagnosticResult(BaseModel):
    status: str
    message: str


def main() -> int:
    settings = StudioSettings()
    try:
        with urlopen(settings.ollama_base_url + "/api/tags", timeout=5) as response:
            names = {item["name"] for item in json.load(response).get("models", [])}
    except Exception as exc:
        print(f"FAIL Server: {exc}\nStart Ollama and pull {settings.ollama_model}.")
        return 1
    checks = [
        ("Server", lambda: True),
        ("Model", lambda: settings.ollama_model in names),
        ("Generation", lambda: create_chat_model(settings).invoke("Reply with OK")),
        ("Tool Calling", lambda: create_chat_model(settings).bind_tools([get_magic_number]).invoke("Call get_magic_number.")),
        ("Structured Output", lambda: create_chat_model(settings).with_structured_output(DiagnosticResult).invoke("Return status and message.")),
    ]
    for name, check in checks:
        try:
            value = check()
            if name == "Model" and not value:
                raise RuntimeError(f"{settings.ollama_model} is not installed")
            if name == "Tool Calling" and not getattr(value, "tool_calls", None):
                raise RuntimeError("model did not call get_magic_number")
            print(f"PASS {name}")
        except Exception as exc:
            print(f"FAIL {name}: {exc}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
