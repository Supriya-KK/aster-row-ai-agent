from src.orders import lookup_order


def test_valid_order():
    result=lookup_order("ORD-1001")
    assert result["found"] is True
    assert result["order_id"]=="ORD-1001"
    assert result["status"]=="pending"


def test_lowercase_and_spaces():
    result=lookup_order(" ord-1001 ")
    assert result["found"] is True
    assert result["order_id"]=="ORD-1001"


def test_unknown_order():
    result=lookup_order("ORD-9999")
    assert result["found"] is False
    assert result["reason"]=="order_not_found"


def test_invalid_order_id():
    result=lookup_order("hello")
    assert result["found"] is False
    assert result["reason"]=="invalid_order_id"


def test_private_fields_are_not_exposed():
    result=lookup_order("ORD-1001")
    result_text=str(result)

    assert "email" not in result_text
    assert "shipping_address" not in result_text
    assert "risk_score" not in result_text
    assert "warehouse_note" not in result_text
    assert "support_tags" not in result_text


def test_pending_order_has_no_fake_delivery_date():
    result=lookup_order("ORD-1001")

    assert result["status"]=="pending"
    assert "estimated_delivery" not in result