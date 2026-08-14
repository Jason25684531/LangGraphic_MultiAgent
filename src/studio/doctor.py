import sys

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
        model = create_chat_model(settings)
        model.invoke("Reply with OK")
    except Exception as exc:
        print(f"FAIL connection: {exc}\nStart Ollama and pull {settings.ollama_model}.")
        return 1
    checks = [("generation", lambda: model.invoke("Reply with OK")),
              ("tool calling", lambda: model.bind_tools([get_magic_number]).invoke("Call get_magic_number.")),
              ("structured output", lambda: model.with_structured_output(DiagnosticResult).invoke("Return status and message."))]
    for name, check in checks:
        try:
            value = check()
            if name == "tool calling" and not getattr(value, "tool_calls", None):
                raise RuntimeError("model did not call get_magic_number")
            print(f"PASS {name}")
        except Exception as exc:
            print(f"FAIL {name}: {exc}")
            return 1
    print("PASS runtime ready")
    return 0


if __name__ == "__main__":
    sys.exit(main())
