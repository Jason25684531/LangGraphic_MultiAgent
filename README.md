# Design Studio

以 LangGraph 與本機 Ollama 建立可動態編排的設計工作室。預設模型為 `gemma4:e2b`。

## 快速開始

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
Copy-Item .env.example .env
.\.venv\Scripts\python -m studio.demo "Develop motion direction for a logo reveal."
```

## 架構

`Role YAML → RoleRegistry → Supervisor → delegate_task → Specialist → Supervisor synthesis → Reviewer → LangGraph END`

- Role：`src/studio/roles/*.yaml` 定義名稱、描述、skills 與 tools。
- Skill：`SKILL.md` 前置資料只進 prompt；內容僅由 `load_skill` 按需載入。
- Tool：以 `@tool` 登錄於 `TOOL_REGISTRY`；Specialist 只能使用自己角色宣告的 tools。
- Supervisor：由 RoleRegistry 動態產生可用角色清單，並只綁定 `delegate_task`。
- Reviewer：輸出 `pass` 或 `revise`；revision 會把先前結果與 feedback 回送 Supervisor。
- LangGraph：負責 `STUDIO → REVIEW → END`，不含角色名稱或 routing sentinel。
- Ollama：模型名稱只由 `.env` 或設定提供。

新增 `motion_designer.yaml` 後，Supervisor 可選用該角色，不需要修改 `graph.py`；此行為由離線 graph 測試保護。

## 驗證

```powershell
.\.venv\Scripts\python -m pytest tests/unit tests/graph
.\.venv\Scripts\python -m pytest -m "ollama and not ollama_slow"
.\.venv\Scripts\python -m pytest -m ollama_slow
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m studio.doctor
```
