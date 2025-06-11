from people_api.models.asaas import AnuityType, PaymentChoice
from people_api.services.member_onboarding import calculate_payment_value


def test_get_payment_options(test_client):
    response = test_client.get("/onboarding/payment_options")
    assert response.status_code == 200
    options = response.json()
    expected = []
    for option in AnuityType:
        calc = calculate_payment_value(PaymentChoice(anuityType=option, externalReference=""))
        expected.append(
            {
                "name": option.value,
                "text": option.text,
                "price": calc.payment_value,
                "expiration_date": calc.expiration_date.strftime("%Y-%m-%d"),
            }
        )
    assert options == expected
