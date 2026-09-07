from app.database.models import Customer
from app.tools.customer_tools import create_customer_tools


def create_test_data(db):
    customer = Customer(
        customer_id="CUS_TEST_CUSTOMER_TOOL",
        name="Customer Tool Test",
        email="customertool@example.com",
        phone="2222222222",
    )

    db.add(customer)
    db.commit()


def test_get_customer_tool(db):
    create_test_data(db)

    tools = create_customer_tools(db)
    get_customer = tools[0]

    result = get_customer.invoke({
        "customer_id": "CUS_TEST_CUSTOMER_TOOL"
    })

    assert result is not None
    assert result.customer_id == "CUS_TEST_CUSTOMER_TOOL"
    assert result.name == "Customer Tool Test"
    assert result.email == "customertool@example.com"
    assert result.phone == "2222222222"