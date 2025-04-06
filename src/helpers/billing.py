from paddle_billing import Client, Environment, Options
from paddle_billing.Resources.Customers.Operations import CreateCustomer, UpdateCustomer, ListCustomers
from paddle_billing.Resources.Products.Operations import CreateProduct, UpdateProduct, ListProducts
from paddle_billing.Resources.Prices.Operations import CreatePrice, UpdatePrice, ListPrices
from paddle_billing.Entities.Shared.TaxCategory   import TaxCategory
from paddle_billing.Entities.Shared.Money         import Money


from decouple import config

PADDLE_SECRET_KEY = config('PADDLE_SECRET_TEST_KEY', default="", cast=str)
paddle = Client(PADDLE_SECRET_KEY, options=Options(Environment.SANDBOX))

# PADDLE CUSTOMER SECTION
def create_customers(raw=False, name="", email="", metadata={}):
    reponse = paddle.customers.create(CreateCustomer(
        name=name,
        email=email,
        custom_data=metadata
    ))

    if raw:
        return reponse
    customer = reponse.id
    return customer

# PADDLE PRODUCT SECTION
def create_product(raw=False, name=str, metadata={}):
    response = paddle.products.create(CreateProduct(
        name=name,
        custom_data=metadata,
        tax_category = TaxCategory.Standard
    ))

    if raw:
        return response
    product = response.id
    return product


# PADDLE PRODUCT PRICE SECTION
def create_price(raw=False, desc="", product_id="", amount="", currency_code="", interval="month", metadata=None):
    if metadata is None:
        metadata = {}

    response = paddle.prices.create(CreatePrice(
        description=desc,
        product_id=product_id,
        unit_price=Money(
            amount=str(amount),
            currency_code=currency_code,
            ),
        billing_cycle={
            "interval": interval,
            "frequency": 1
        },
        custom_data=metadata
    ))

    if raw:
        return response
    return response.id


def update_price(raw=False, desc="", product_id="", amount="", currency_code="", interval="month", metadata=None):
    if metadata is None:
        metadata = {}

    response = paddle.prices.update(UpdatePrice(
        description=desc,
        product_id=product_id,
        unit_price=Money(
            amount=str(amount),
            currency_code=currency_code,
            ),
        billing_cycle={
            "interval": interval,
            "frequency": 1
        },
        custom_data=metadata
    ))

    if raw:
        return response
    return response.id