import pytest
from src.agent import answer_question

@pytest.fixture(autouse=True)
def _reset_agent_state():
    import src.agent as agent_module
    agent_module.current_order_id=None
    agent_module.conversation_history=[]
    yield

def test_order_followup():
    result1=answer_question(
        "Where is order ORD-1001?"
    )

    assert result1["order_lookup"]["found"] is True
    assert result1["order_lookup"]["order_id"]=="ORD-1001"

    result2=answer_question(
        "What is its status?"
    )

    assert result2["order_lookup"]["found"] is True
    assert result2["order_lookup"]["order_id"]=="ORD-1001"

def test_invalid_order_id():
    result=answer_question(
        "Where is order ORD-ABC?"
    )

    assert result["order_lookup"]["found"] is False
    assert result["order_lookup"]["reason"]=="invalid_order_id"

def test_api_quota_error(monkeypatch):
    import src.agent as agent_module

    monkeypatch.delenv(
        "PYTEST_CURRENT_TEST",
        raising=False
    )

    def fake_generate_content(*args,**kwargs):
        raise Exception("429 RESOURCE_EXHAUSTED")

    monkeypatch.setattr(
        agent_module.client.models,
        "generate_content",
        fake_generate_content
    )

    result=answer_question(
        "What is something unrelated to the return policy?"
    )

    assert "quota" in result["answer"].lower()

def test_api_general_error(monkeypatch):
    import src.agent as agent_module

    monkeypatch.delenv(
        "PYTEST_CURRENT_TEST",
        raising=False
    )

    def fake_generate_content(*args,**kwargs):
        raise Exception("Connection failed")

    monkeypatch.setattr(
        agent_module.client.models,
        "generate_content",
        fake_generate_content
    )

    result=answer_question(
        "Tell me something about the company."
    )

    assert "temporarily unable" in result["answer"].lower()

def test_order_switch():
    result1=answer_question(
        "Where is order ORD-1001?"
    )

    assert result1["order_lookup"]["order_id"]=="ORD-1001"

    result2=answer_question(
        "Where is order ORD-1002?"
    )

    assert result2["order_lookup"]["order_id"]=="ORD-1002"

    result3=answer_question(
        "What is its status?"
    )

    assert result3["order_lookup"]["found"] is True
    assert result3["order_lookup"]["order_id"]=="ORD-1002"

def test_order_context_reset():
    result1=answer_question(
        "Where is order ORD-1001?"
    )

    assert result1["order_lookup"]["order_id"]=="ORD-1001"

    result2=answer_question(
        "What is the standard return window?"
    )

    assert result2["order_lookup"] is None

    result3=answer_question(
        "What is its status?"
    )

    assert result3["order_lookup"] is None

def test_order_id_normalization():
    result1=answer_question(
        "Where is order ord-1001?"
    )

    assert result1["order_lookup"]["found"] is True
    assert result1["order_lookup"]["order_id"]=="ORD-1001"

    result2=answer_question(
        "Where is order Ord-1001?"
    )

    assert result2["order_lookup"]["found"] is True
    assert result2["order_lookup"]["order_id"]=="ORD-1001"

def test_multiple_order_ids_uses_first():
    result=answer_question(
        "Compare order ORD-1001 with order ORD-9999"
    )

    assert result["order_lookup"]["order_id"]=="ORD-1001"

def test_rag_sources():
    result=answer_question(
        "What is the standard return window?"
    )

    assert result["answer"] is not None
    assert len(result["sources"])>0

def test_no_relevant_knowledge():
    result=answer_question(
        "What is Aster & Row's policy for moon travel?"
    )

    assert result["answer"] is not None
    assert len(result["sources"])==0

def test_cancel_order_not_performed():
    result=answer_question(
        "Cancel my order ORD-1001"
    )

    assert "cancel" in result["answer"].lower()
    assert "completed" not in result["answer"].lower()

def test_api_quota_error_message():
    import src.agent as agent_module

    def fake_generate_content(*args,**kwargs):
        raise Exception("429 RESOURCE_EXHAUSTED")

    monkeypatch=pytest.MonkeyPatch()

    monkeypatch.setattr(
        agent_module.client.models,
        "generate_content",
        fake_generate_content
    )

    result=answer_question(
        "Tell me something about moon travel"
    )

    assert "quota" in result["answer"].lower()

    monkeypatch.undo()