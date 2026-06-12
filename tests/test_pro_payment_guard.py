"""Guards against activating Pro without manual wallet payment."""

from routers.billing.pro_helpers import is_manual_wallet_pro_payment_link


def test_manual_wallet_link_yape():
    assert is_manual_wallet_pro_payment_link("yape:S/144.30")


def test_manual_wallet_link_plin():
    assert is_manual_wallet_pro_payment_link("plin:S/99.00")


def test_mp_wallet_note_not_manual():
    assert not is_manual_wallet_pro_payment_link("yape:mercadopago:pending")


def test_paypal_url_not_manual():
    assert not is_manual_wallet_pro_payment_link(
        "https://www.paypal.com/billing/subscriptions?ba_token=x"
    )


def test_mercadopago_url_not_manual():
    assert not is_manual_wallet_pro_payment_link(
        "https://www.mercadopago.com.pe/checkout/v1/redirect?pref_id=abc"
    )
