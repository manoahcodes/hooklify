from paddle_billing import Client, Environment, Options
from paddle_billing.Resources.Customers.Operations import CreateCustomer, UpdateCustomer, ListCustomers
from decouple import config

PADDLE_SECRET_KEY = config('PADDLE_SECRET_TEST_KEY', default="", cast=str)
paddle = Client(PADDLE_SECRET_KEY, options=Options(Environment.SANDBOX))

# PADDLE CUSTOMER SECTION
# def create_customers(raw=False, name="", email="", custom_data={}):
#     reponse = paddle.customers.create(CreateCustomer(
#         name=name,
#         email=email,
#         custom_data=custom_data
#     ))

#     if raw:
#         return reponse
#     customer = reponse.id
#     return customer

email = "minorissuesmanoah@gmail.com"

customers = paddle.customers.list()
customers_list = list(customers)
matching_customer = next(
    (customer for customer in customers_list if customer.email == email),
    None
)

# print(matching_customer)
# if customers_list:
#     existing_customer = customers_list[0]
#     paddle_id = existing_customer.id
#     response = paddle.customers.update(customer_id=paddle_id, operation=UpdateCustomer(
#             email="admin@manark.store",
#             name="Mano"
#         )
#     )

#     print(response)