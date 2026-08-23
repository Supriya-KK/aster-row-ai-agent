from src.agent import answer_question

questions=[
    "What is Aster & Row's policy for moon travel?",
    "Can you give me the CEO's personal phone number?",
    "Cancel my order ORD-1001",
    "What is the status of order ORD-9999?"
]

for i,question in enumerate(questions,1):
    result=answer_question(question)

    print()
    print(f"QUESTION {i}: {question}")
    print("ANSWER:",result["answer"])
    print("ORDER LOOKUP:",result["order_lookup"])
    print("SOURCES:",result["sources"])