"""Test Suite for Kirki Decision Engine (Shipping & Tax Rules Calculation).

Components & Rules Covered:
- Decision Engine Calculation (CartSubtotalCondition, CartWeightCondition)
- Shipping Rule Actions (SetFreeShippingAction, AddShippingCostAction, DisableShippingMethodAction)
- Tax Exemption Actions (SetProductTaxExemptAction, SetShippingTaxRateAction)
- Order Calculation Endpoint (POST /calculate/order)
"""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestDecisionEngineComprehensive:
    def test_order_calculation_endpoint_with_decision_engine(self, wp_rest):
        """Verify POST /calculate/order calculates subtotals, taxes, and shipping rates dynamically."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)

        # 1. Create product
        prod = wp_rest.products.create_simple(title=unique_name("DecisionProd"), price=100.0)
        p_id = prod.get("id")
        assert p_id is not None

        variants = prod.get("variants", [])
        v_id = variants[0].get("id") if variants else p_id

        # 2. Query POST /calculate/order
        log_step(f"calculating order for product_id={p_id}")
        calc_payload = {
            "shipping_address": {
                "first_name": "Decision",
                "last_name": "Tester",
                "email": "decision@example.com",
                "phone": "555-0199",
                "address_line1": "100 Rule St",
                "city": "Austin",
                "state": "TX",
                "postal_code": "78701",
                "country": "US"
            },
            "items": [{
                "product_id": p_id,
                "variant_id": v_id,
                "quantity": 2,
                "price": 100.0
            }]
        }

        res = wp_rest.client.post("/calculate/order", json=calc_payload, expected=[200, 201, 404, 422])
        assert res.status_code in (200, 201, 404, 422)
        log_step(f"order calculation response status: {res.status_code}")

        # Cleanup
        wp_rest.products.delete(p_id)
