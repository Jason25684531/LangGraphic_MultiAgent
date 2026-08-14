# Design Studio

本地優先的多代理設計工作流，使用 Ollama 與 LangGraph。

## 安裝與設定

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

請啟動 Ollama，並將 `.env` 的 `OLLAMA_MODEL` 改為已安裝、支援 tool calling 與 structured output 的模型（本機已驗證 `qwen3.5:9b`）。

```powershell
.\.venv\Scripts\python -m studio.demo "建立咖啡品牌設計簡報"
.\.venv\Scripts\python -m studio.doctor
.\.venv\Scripts\python -m pytest tests/unit tests/graph
.\.venv\Scripts\python -m pytest -m ollama
.\.venv\Scripts\python -m pytest
```

## 擴充

- Role：在 `src/studio/roles/` 新增 YAML，填入 `name`、`description`、`system_prompt`、`skills`、`tools`。
- Skill：新增 `src/studio/skills/<name>/SKILL.md`，再於角色 YAML 宣告名稱。
- Tool：以 `@tool` 定義安全函式，加入 `src/studio/tools/registry.py` 的 `TOOL_REGISTRY`，再於角色 YAML 白名單中宣告。

新增角色不需要修改 graph；下一次建立 `RoleRegistry` 即會自動載入。
