# Aster & Row AI Customer Support Agent

A Python-based customer support agent that uses the Aster & Row knowledge base to answer customer questions and can also look up order information.

## Features

* Answers questions using the knowledge base
* Handles return and TrailPlus policies
* Looks up order status from JSON data
* Supports order follow-up questions
* Handles invalid and unknown order IDs
* Does not invent information when the knowledge base has no answer
* Handles API errors and quota issues
* Includes automated tests

## Technologies

* Python
* Google Gemini API
* RAG-style knowledge retrieval
* JSON
* Pytest
* Git & GitHub

## Project Structure

```text
aster-row-ai-agent/
├── data/
├── evaluation/
├── knowledge-base/
├── src/
│   ├── agent.py
│   ├── orders.py
│   └── rag.py
├── tests/
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

Clone the repository and enter the project:

```bash
git clone https://github.com/Supriya-KK/aster-row-ai-agent.git
cd aster-row-ai-agent
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and add your Gemini API key:

```text
GEMINI_API_KEY=your_api_key_here
```

Run the application:

```bash
python main.py
```

## Example

```text
Customer: Where is order ORD-1001?

Agent: We received the order and it has not entered processing yet.
```

```text
Customer: What is the standard return window?

Agent: The standard return window is 30 calendar days from delivery.
```

```text
Customer: What is Aster & Row's policy for moon travel?

Agent: I do not have enough information regarding Aster & Row's policy on moon travel.
```

The last example shows that the agent does not make up an answer when the required information is not available in the knowledge base.


## Testing

Run:

```bash
pytest -q
```

Current result:

```text
18 passed
```

The tests cover order lookup, follow-up questions, return policies, invalid orders, unknown information, API errors, and cancellation requests.

## Note

Orders are currently stored in a local JSON file, so actions such as cancelling an order are not actually performed.
