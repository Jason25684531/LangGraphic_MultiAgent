"""Small deterministic model for offline tests and examples."""
import json
from langchain_core.messages import AIMessage


class FakeChatModel:
    def __init__(self, responses=None):
        self.responses = list(responses or ["ok"])
        self.tools = []
        self.bound_tools = []
        self.prompts = []

    def bind_tools(self, tools):
        self.tools = list(tools)
        self.bound_tools.append(self.tools)
        return self

    def invoke(self, prompt):
        self.prompts.append(prompt)
        response = self.responses.pop(0) if self.responses else "ok"
        if isinstance(response, Exception):
            raise response
        return response if isinstance(response, AIMessage) else AIMessage(content=str(response))

    def with_structured_output(self, schema):
        model = self

        class Structured:
            def invoke(self, prompt):
                value = model.invoke(prompt)
                content = value.content if hasattr(value, "content") else value
                if isinstance(content, str) and content.startswith("{"):
                    return schema.model_validate(json.loads(content))
                if isinstance(content, str) and content in {"pass", "revise"}:
                    return schema(status=content, feedback="")
                raise ValueError("Malformed structured output")

        return Structured()
