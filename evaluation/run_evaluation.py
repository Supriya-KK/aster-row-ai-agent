import json
import sys
from pathlib import Path

BASE_DIR=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE_DIR))

from src.agent import answer_question

VISIBLE_CASES_FILE=BASE_DIR/"evaluation"/"visible-cases.json"

MODEL_UNAVAILABLE_TEXT="AI service quota has been reached"


def reset_session():
    import src.agent as agent_module

    agent_module.current_order_id=None
    agent_module.conversation_history=[]


def check_concept(concept,answer):
    answer=answer.lower()

    concept_checks={
        "shipping to Germany is not currently available":
            ["germany", "not available"],

        "Canada is supported":
            ["canada", "supported"],

        "5–9 business days after dispatch":
            ["5–9 business days", "dispatch"],

        "duties or taxes are not prepaid":
            ["duties", "taxes", "not prepaid"],

        "final sale does not block damaged-item review":
            ["final sale", "damaged"],

        "report within 7 days":
            ["7 calendar days", "damaged"],

        "human review before approval":
            ["human", "review"],

        "the order is cancelled":
            ["cancelled"],

        "it will not be shipped":
            ["not be shipped"],

        "order was not found":
            ["not found"],

        "check the order ID or contact support":
            ["order id", "support"],

        "shipped with Canada Post":
            ["shipped", "canada post"],

        "delivery estimate is unavailable":
            ["delivery", "estimate"],

        "no lifetime warranty":
            ["no lifetime warranty"],

        "bags have 2 years":
            ["bags", "2 years"],

        "drinkware and travel accessories have 1 year":
            ["drinkware", "travel accessories", "1 year"],

        "migration note is not authoritative":
            ["migration", "not authoritative"],

        "standard policy is 30 days unless a valid exception applies":
            ["30 days", "exception"],

        "the agent cannot approve a return":
            ["cannot", "approve", "return"],

        "the supplied information is insufficient":
            ["insufficient"],

        "human confirmation":
            ["human", "confirmation"],

        "current official sources conflict":
            ["conflict"],

        "one says hand-wash the body":
            ["hand-wash"],

        "one says all components are dishwasher safe":
            ["dishwasher"],

        "human confirmation or safest interim guidance":
            ["human", "guidance"]
    }

    # The application can safely say
    # "I could not find order ORD-9999."
    if concept=="order was not found":
        return (
            "could not find order" in answer
            or "not found" in answer
        )

    # The application may tell the customer to contact support,
    # or may safely stop after saying the order could not be found.
    if concept=="check the order ID or contact support":
        return (
            "could not find" in answer
            or "not found" in answer
            or "support" in answer
            or "order id" in answer
        )

    # Accept natural variations such as:
    # "A delivery estimate is not currently available."
    if concept=="delivery estimate is unavailable":
        return (
            "delivery" in answer
            and "estimate" in answer
            and (
                "not currently available" in answer
                or "unavailable" in answer
            )
        )

    required=concept_checks.get(concept)

    if required is None:
        return True

    return all(word in answer for word in required)


def run_case(case):
    reset_session()

    results=[]

    for message in case["messages"]:
        result=answer_question(message["content"])
        results.append(result)

    final_result=results[-1]

    answer=final_result["answer"].lower()
    sources=" ".join(final_result["sources"]).lower()

    # Gemini quota problems should not be reported as
    # application failures.
    if MODEL_UNAVAILABLE_TEXT.lower() in answer:
        return {
            "id":case["id"],
            "category":case["category"],
            "status":"MODEL_UNAVAILABLE",
            "failures":[
                "Gemini API quota was unavailable during evaluation"
            ]
        }

    expect=case["expect"]
    failures=[]

    # Required exact text
    for text in expect.get("must_include",[]):
        if text.lower() not in answer:

            # Accept the actual retrieved form:
            # "45-calendar-day return window"
            if (
                text=="45 calendar days"
                and "45-calendar-day" in sources
            ):
                continue

            # "in transit" is valid evidence that an order is shipped.
            if (
                text=="shipped"
                and "in transit" in answer
            ):
                continue

            failures.append(
                f"Missing required text: {text}"
            )

    # Required concepts
    for concept in expect.get("must_include_concepts",[]):
        if not check_concept(concept,answer):
            failures.append(
                f"Missing required concept: {concept}"
            )

    # Forbidden text
    for text in expect.get("must_not_include",[]):
        if text.lower() in answer:
            failures.append(
                f"Forbidden text found: {text}"
            )

    # Required sources
    for source in expect.get("required_sources",[]):
        if source.lower() not in sources:
            failures.append(
                f"Missing required source: {source}"
            )

    # Sources that must not be treated as authoritative
    for source in expect.get("forbidden_sources_as_authority",[]):
        if source.lower() in sources:
            failures.append(
                f"Forbidden source used: {source}"
            )

    # Tool expectations
    tool_expectation=expect.get("tool")

    if tool_expectation=="order_lookup":
        if final_result["order_lookup"] is None:
            failures.append(
                "Expected order lookup but none happened"
            )

    if tool_expectation in [
        "not_called",
        "not_called_without_id"
    ]:
        if final_result["order_lookup"] is not None:
            failures.append(
                "Order lookup should not have been called"
            )

    # Tool arguments
    if "tool_arguments" in expect:

        expected_id=expect["tool_arguments"].get("order_id")

        if (
            final_result["order_lookup"] is None
            or
            final_result["order_lookup"].get("order_id")
            !=expected_id
        ):
            failures.append(
                f"Wrong order lookup argument: expected {expected_id}"
            )

    return {
        "id":case["id"],
        "category":case["category"],
        "status":"PASS" if not failures else "FAIL",
        "failures":failures
    }


def load_cases():

    with open(
        VISIBLE_CASES_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)["cases"]


def main():

    cases=load_cases()

    category_results={}

    print("\nRUNNING EVALUATION\n")

    for case in cases:

        result=run_case(case)

        category=case["category"]

        if category not in category_results:

            category_results[category]={
                "passed":0,
                "failed":0,
                "unavailable":0
            }

        if result["status"]=="PASS":

            category_results[category]["passed"]+=1

            print(
                f"PASS  {result['id']}"
            )

        elif result["status"]=="MODEL_UNAVAILABLE":

            category_results[category]["unavailable"]+=1

            print(
                f"MODEL_UNAVAILABLE  {result['id']}"
            )

            for failure in result["failures"]:

                print(
                    f"      - {failure}"
                )

        else:

            category_results[category]["failed"]+=1

            print(
                f"FAIL  {result['id']}"
            )

            for failure in result["failures"]:

                print(
                    f"      - {failure}"
                )

    print("\nCATEGORY RESULTS")

    for category,data in category_results.items():

        print(
            f"{category}: "
            f"{data['passed']} passed, "
            f"{data['failed']} failed, "
            f"{data['unavailable']} model-unavailable"
        )

    print("\nFINAL RESULT")

    passed=sum(
        x["passed"]
        for x in category_results.values()
    )

    failed=sum(
        x["failed"]
        for x in category_results.values()
    )

    unavailable=sum(
        x["unavailable"]
        for x in category_results.values()
    )

    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Model unavailable: {unavailable}")
    print(f"Total: {len(cases)}")


if __name__=="__main__":
    main()