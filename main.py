from src.agent import answer_question


print("=" * 60)
print("ASTER & ROW AI CUSTOMER SUPPORT AGENT DEMO")
print("=" * 60)


# --------------------------------------------------
# 1. KNOWLEDGE-BASE QUESTION
# --------------------------------------------------

print("\n--- 1. KNOWLEDGE-BASE QUESTION ---")

question = "What is the standard return window?"

result = answer_question(question)

print("Customer:", question)
print("Agent:", result["answer"])
print("Sources:", result["sources"])


# --------------------------------------------------
# 2. ORDER LOOKUP
# --------------------------------------------------

print("\n--- 2. ORDER LOOKUP ---")

question = "What is the status of order ORD-1007?"

result = answer_question(question)

print("Customer:", question)
print("Agent:", result["answer"])
print("Order Lookup:", result["order_lookup"])


# --------------------------------------------------
# 3. MULTI-TURN CONVERSATION
# --------------------------------------------------

print("\n--- 3. MULTI-TURN CONVERSATION ---")

question = "Where is order ORD-1007?"

result = answer_question(question)

print("Customer:", question)
print("Agent:", result["answer"])


question = "When will it arrive?"

result = answer_question(question)

print("Customer:", question)
print("Agent:", result["answer"])
print("Order Lookup:", result["order_lookup"])


# --------------------------------------------------
# 4. SAFE REFUSAL / HUMAN HELP
# --------------------------------------------------

print("\n--- 4. SAFE REFUSAL / HUMAN HELP ---")

question = "What is Aster & Row's policy for moon travel?"

result = answer_question(question)

print("Customer:", question)
print("Agent:", result["answer"])
print("Sources:", result["sources"])


# --------------------------------------------------
# 5. UNKNOWN ORDER
# --------------------------------------------------

print("\n--- 5. UNKNOWN ORDER ---")

question = "What is the status of order ORD-9999?"

result = answer_question(question)

print("Customer:", question)
print("Agent:", result["answer"])
print("Order Lookup:", result["order_lookup"])


# --------------------------------------------------
# COMPLETE
# --------------------------------------------------

print("\n" + "=" * 60)
print("DEMO COMPLETE")
print("=" * 60)
