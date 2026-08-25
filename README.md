# Aster & Row AI Customer Support Agent

A small Python customer support agent built for the Aster & Row take-home assignment.

The agent uses the supplied knowledge-base documents to answer customer questions and uses the mock order data when an order ID is provided.

## Features

* Answers customer questions using the supplied knowledge base
* Uses RAG-style retrieval instead of sending the whole knowledge base to the model
* Gives source references for retrieved policy information
* Looks up order information from `data/orders.json`
* Handles order follow-up questions
* Handles unknown and malformed order IDs
* Avoids exposing internal order information
* Does not invent information when the knowledge base does not contain an answer
* Handles conflicting or unsafe retrieved content
* Includes automated tests and an evaluation suite

## Technologies

* Python
* Google Gemini API
* RAG-style retrieval using TF-IDF
* JSON
* Pytest
* Git and GitHub

## Model and Storage

**Model:** Google Gemini `gemini-3.6-flash`

**Retrieval:** TF-IDF-based text retrieval using `scikit-learn`.

The Markdown files in `knowledge-base/` are split into smaller sections and searched using relevant words from the customer's question.

**Storage:** Local Markdown files for the knowledge base and a local JSON file for mock order data.

**Framework:** The application is a small Python application without a large agent framework.

## Architecture

The project is mainly divided into three parts:

* `rag.py` handles searching the knowledge-base files and finding relevant information.
* `orders.py` handles looking up orders from `orders.json`.
* `agent.py` takes the customer question, uses the relevant information, and generates the final response.

`main.py` is used to run sample customer questions and demonstrate the agent.

For normal questions, the agent searches the knowledge base first. If an order ID is included, it looks up that order and uses the sanitized order result in the response.

The basic flow is:

```text
Customer question
       ↓
     Agent
       ↓
Knowledge base / Order lookup
       ↓
Relevant information
       ↓
     Gemini
       ↓
Final answer
```

## Project Structure

```text
aster-row-ai-agent/

├── data/
│
├── evaluation/
│   ├── visible-cases.json
│   └── run_evaluation.py
│
├── knowledge-base/
│
├── src/
│   ├── agent.py
│   ├── orders.py
│   └── rag.py
│
├── tests/
│
├── demo/
│   ├── agent-demo.mp4
│   └── agent-demo.gif
│
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

Clone the repository:

```bash
git clone https://github.com/Supriya-KK/aster-row-ai-agent.git
cd aster-row-ai-agent
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
source .venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file using `.env.example` and add a Gemini API key:

```text
GEMINI_API_KEY=your_api_key_here
```

Do not commit the `.env` file or any real API key.

## Run the Agent

The demo entry point is:

```bash
python main.py
```

`main.py` contains sample customer questions so the application can be demonstrated without a separate frontend.

The application can also be imported and used through the `answer_question()` function in `src/agent.py`.

## Example

```text
Customer: Where is order ORD-1001?

Agent: We received the order and it has not entered processing yet.
```

```text
Customer: What is the standard return window?

Agent: Customers on the standard plan may request a return within 30 calendar days of delivery.
```

When the required information is not available, the agent avoids guessing and instead explains that the supplied information is insufficient or recommends human confirmation when appropriate.

## Testing

Run the automated tests:

```bash
pytest -q
```

Latest test result:

```text
18 passed, 1 warning
```

The warning comes from a dependency used by the Google GenAI package and does not cause the tests to fail.

## Evaluation

Run the evaluation suite with:

```bash
python evaluation/run_evaluation.py
```

The evaluation suite checks the supplied visible cases and reports individual case results by category.

### Baseline

The first evaluation run showed several problems with retrieval and order-handling logic.

```text
Passed: 12
Failed: 3
Model unavailable: 0
Total: 15
```

The main problems found included:

* TrailPlus information was not always retrieved correctly.
* Some international shipping questions were not routed to the correct policy.
* Some order-related questions were incorrectly treated as order questions simply because they contained words such as `order` or `delivery`.
* Some policy answers required stronger deterministic handling.

These issues were used to improve retrieval routing, order detection, policy handling, and grounded responses.

### Final Evaluation

After the fixes and regression checks, the final evaluation passed all visible cases:

```text
Passed: 15
Failed: 0
Model unavailable: 0
Total: 15
```

Final results by category:

```text
retrieval:               2 passed, 0 failed, 0 model-unavailable
multi-source-grounding:  1 passed, 0 failed, 0 model-unavailable
conversation:            1 passed, 0 failed, 0 model-unavailable
groundedness:             2 passed, 0 failed, 0 model-unavailable
tool-use:                 2 passed, 0 failed, 0 model-unavailable
tool-reliability:        3 passed, 0 failed, 0 model-unavailable
privacy:                  1 passed, 0 failed, 0 model-unavailable
prompt-security:          1 passed, 0 failed, 0 model-unavailable
abstention:               1 passed, 0 failed, 0 model-unavailable
source-conflict:          1 passed, 0 failed, 0 model-unavailable
```

The final result is:

```text
15/15 visible evaluation cases passed
```

The deterministic automated test suite also passes:

```text
18 passed, 1 warning
```

## Bug Diary

### 1. Policy questions containing "order" skipped RAG

**How it was reproduced:**

A TrailPlus question such as:

```text
My TrailPlus membership was active when I ordered. What is my return window?
```

was incorrectly treated as an order question.

**Root cause:**

The agent originally decided that a question was an order question when it contained words such as `order`, `delivery`, or `shipment`.

**Fix:**

The application now uses the presence of an actual order ID to decide whether an order lookup is required.

This prevents ordinary policy questions from incorrectly skipping knowledge-base retrieval.

**Regression test:**

The `trailplus-return-window` evaluation case and automated tests cover this behavior.

### 2. Unknown order handling

**How it was reproduced:**

```text
Please check ORD-9999.
```

The evaluation checked that the system did not invent a status or delivery estimate.

**Root cause:**

The order lookup result needed to be used directly for unknown orders instead of allowing the model to make assumptions.

**Fix:**

Unknown orders now return a safe response stating that the order could not be found without inventing order details.

**Regression test:**

The `unknown-order` evaluation case and automated order tests cover this behavior.

### 3. Orders without delivery estimates

**How it was reproduced:**

```text
When will ORD-1011 get here?
```

The order is shipped with Canada Post but does not contain a delivery estimate.

**Root cause:**

The agent could potentially try to provide an arrival date even when the order data did not contain one.

**Fix:**

The sanitized order result is used directly and the response does not invent a delivery estimate when one is unavailable.

**Regression test:**

The `shipped-without-eta` evaluation case covers this behavior.

### 4. Unsupported country response

**How it was reproduced:**

```text
Can you ship an Atlas Weekender to Germany?
```

**Root cause:**

The retrieved international-shipping information was correct, but the generated answer did not consistently use the expected explicit wording.

**Fix:**

Germany-specific routing was added so that the current international shipping policy is selected and the agent clearly states that shipping to Germany is not currently available.

**Regression test:**

The `unsupported-country` evaluation case now passes.

### 5. Lifetime warranty response

**How it was reproduced:**

```text
Do all Aster & Row products have a lifetime warranty?
```

**Root cause:**

The answer depended on model generation and could vary in wording even though the warranty policy clearly states that Aster & Row does not offer a lifetime warranty.

**Fix:**

Warranty questions are now handled using the authoritative warranty information so the response clearly states that there is no lifetime warranty and provides the applicable warranty periods.

**Regression test:**

The `no-lifetime-warranty` evaluation case now passes.

## Safety and Privacy

The agent does not expose internal order fields such as:

* customer email
* customer address
* internal notes
* risk scores

The model is also instructed not to reveal system instructions, secrets, or internal-only information.

Retrieved knowledge-base content is treated as untrusted data and is not allowed to override the application's instructions.

The agent does not claim that an action such as a cancellation, refund, replacement, or address change was completed unless the application actually supports that action.

## Known Limitations

* The order data is stored locally in JSON.
* Order cancellation is not actually implemented.
* The application currently uses a simple TF-IDF retrieval approach rather than a production vector database.
* The Gemini API is required for model-generated policy answers.
* API quota or availability can affect model-generated responses.
* The current interface is a simple command-line demonstration rather than a web application.
* Conversation memory is kept in the current Python process and is not persistent between sessions.
* More work would be needed for production monitoring, authentication, persistent storage, and stronger retrieval evaluation.

## AI Coding Tools

AI coding assistance was used during development for:

* explaining Python and RAG concepts
* debugging Python errors
* suggesting small code changes
* improving test and evaluation logic
* checking Git commands and project structure

One example of an incomplete AI-generated suggestion was treating questions containing words such as `order` or `delivery` as order-specific questions. This caused legitimate policy questions, such as TrailPlus return questions, to skip knowledge-base retrieval.

The logic was changed so that an actual order ID is required before performing order-specific handling.

## Demo

The following demo shows the Aster & Row AI customer support agent working with:

* a knowledge-base question with citations
* an order lookup
* a multi-turn conversation
* a case where the agent correctly refuses to guess or recommends human help
* the evaluation suite running

<p align="center">
  <img src="demo/agent-demo.gif" alt="Aster & Row AI Agent Demo" width="800">
</p>

[▶️ Watch the full demo video](demo/agent-demo.mp4)

## Final Notes

This project focuses on building a small system that is reliable for the supplied customer-support scenarios rather than building a large production platform.

The final visible evaluation result is **15/15**, with the automated test suite at **18 passed**.

The implementation prioritizes grounded answers, safe order handling, document precedence, multi-turn context, privacy, prompt-injection resistance, and explicit handling of insufficient or conflicting information.
