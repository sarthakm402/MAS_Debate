# Multi-Agent System — Debate Demo   
   
**Multi-Agent System — Debate Demo** is a lightweight FastAPI application that demonstrates a multi-agent debate pipeline using Google Generative AI (Gemini), LangChain-style memory, and a state graph (via `langgraph`) to orchestrate agents: **For**, **Against**, **FactChecker**, and **Mediator**.
 
---  
    
## Features 
  
- Multi-round debate flow with revision based on fact-check feedback
- Conversation memory (recent messages) using `ConversationBufferMemory`
- Agents implemented as state graph nodes (`ForAgent`, `AgainstAgent`, `FactChecker`, `Mediator`)
- FastAPI endpoints to run debates programmatically
- Easy-to-edit prompt templates for each agent's role

---

## Prerequisites

- Python 3.9+
- An API key for Google Generative AI (Gemini) with access to the configured model
- Optional: Docker

---

## Installation

```bash
git clone <your-repo-url>
cd <your-repo>
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
.\.venv\Scripts\activate   # Windows (PowerShell)
pip install -r requirements.txt
```

`requirements.txt` should include at minimum:

```
fastapi
uvicorn
google-generativeai
langchain
langgraph
pydantic
```

Add or pin versions as needed.

---

## Configuration

Set environment variables before running the app. Example (Linux/macOS):

```bash
export GENAI_API_KEY="your-google-genai-key"
```

On Windows (PowerShell):

```powershell
$env:GENAI_API_KEY = "your-google-genai-key"
```

Important: never commit secrets to source control.

---

## How it works (high level)

1. **Memory** — `ConversationBufferMemory` keeps the last few messages to provide context to agents.
2. **Agents** — `for_agent`, `against_agent`, `fact_checker`, `mediator` functions craft prompts and call the generative model.
3. **State Graph** — `langgraph.StateGraph` orchestrates agent execution and conditional transitions. The graph increments `round_number` and decides when to move to the `Mediator` node.
4. **FastAPI** — A small HTTP layer exposes the debate runner with `GET /debate?topic=...` and `POST /debate`.

---

## Running locally

Start the FastAPI app with Uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- `GET http://127.0.0.1:8000/` → health check
- `GET http://127.0.0.1:8000/debate?topic=Should%20AI%20be%20regulated%3F` → run debate for a topic

### Example curl

```bash
curl "http://127.0.0.1:8000/debate?topic=Should%20AI%20be%20regulated%3F"
```

Or POST JSON:

```bash
curl -X POST "http://127.0.0.1:8000/debate" -H "Content-Type: application/json" -d '{"topic":"Should AI be regulated by governments?"}'
```

---

## Endpoints

- `GET /` — returns `{ "status": "ok" }`
- `GET /debate?topic=<topic>` — runs debate flow and returns final results
- `POST /debate` — accepts JSON `{ "topic": "..." }` and returns results

Returned JSON includes:

```json
{
  "topic": "...",
  "for_argument": "...",
  "against_argument": "...",
  "fact_check": "...",
  "verdict": "...",
  "conversation_history": [ {"role": "ai/user", "content": "..."}, ... ]
}
```

---

## Prompts

Prompts are defined as string templates in the code and can be customized. The repository includes separate prompts for:

- `FOR_PROMPT`
- `FOR_REVISION_PROMPT`
- `AGAINST_PROMPT`
- `AGAINST_REVISION_PROMPT`
- `FACT_CHECK_PROMPT`
- `MEDIATOR_PROMPT`

Adjust phrasing, length, or instructions to tune agent behavior.

---

## Customization

- **Rounds**: Modify the logic in `check_rounds_after_for` and `check_rounds_after_fact` to change how many rounds occur before the mediator runs.
- **Memory**: `ConversationBufferMemory(return_messages=True, memory_key="chat_history")` can be tuned (`k` parameter) to store more/less context.
- **Models**: Replace `gemini-2.0-flash-lite` with another compatible model or swap to a different provider by refactoring the `model.generate_content` calls.

---

## Security & Best Practices

- Keep API keys and secrets out of source control. Use environment variables or a secrets manager.
- Rate-limit calls to the GenAI API if running at scale.
- Validate and sanitize user-provided topic strings if exposing this to untrusted users.

---

## Troubleshooting

- If the app fails to call the model, confirm `GENAI_API_KEY` is set and valid.
- If memory grows unexpectedly, ensure you are not appending unbounded messages into `memory.chat_memory` without limits.
- For model response latency, consider smaller models or asynchronous job queues for heavy workloads.

---

## Contributing

Contributions welcome. Suggested workflow:

1. Fork the repo
2. Create a feature branch
3. Add tests for new features
4. Open a pull request with a clear description

---

## License

This project is provided under the MIT License. See `LICENSE` for details.

---

## Acknowledgements

- Google Generative AI (Gemini)
- LangChain
- LangGraph

---

If you want any specific sections added (example screenshots, Dockerfile, CI, tests, or a downloadable ZIP) tell me which and I will add them.

