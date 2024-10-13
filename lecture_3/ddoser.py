from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from faker import Faker

faker = Faker()
existing_items = []

def create_empty_cart():
    response = requests.post("http://localhost:8080/cart")
    # print(response.text)

def get_cart(cart_id):
    response = requests.get(f"http://localhost:8080/cart/{cart_id}")
    # print(response.text)
    
def get_carts(query):
    response = requests.get("http://localhost:8080/cart", params=query)
    # print(response.text)

def create_item():
    item = {
        "name": "Тестовый товар",
        "price": faker.pyfloat(min_value=10.0, max_value=100.0),
    }
    response = requests.post("http://localhost:8080/item", json=item)
    # print(response.text)
    item_id = response.json()["id"]
    existing_items.append(item_id)
    return item_id
    
def get_item(item_id):
    response = requests.get(f"http://localhost:8080/item/{item_id}")
    # print(response.text)
    
def delete_item(item_id):
    response = requests.delete(f"http://localhost:8080/item/{item_id}")
    # print(response.text)
    existing_items.remove(item_id)

def create_not_empty_carts(existing_items):
    for _ in range(100):
        cart_id = requests.post("http://localhost:8080/cart").json()["id"]
        for item_id in faker.random_elements(existing_items, unique=False, length=random.randint(1, len(existing_items))):
            requests.post(f"http://localhost:8080/cart/{cart_id}/add/{item_id}")
        # print(f"Created cart with ID: {cart_id}")

with ThreadPoolExecutor() as executor:
    futures = {executor.submit(create_item): f"create-item-{i}" for i in range(500)}

    for i in range(500):
        futures[executor.submit(create_empty_cart)] = f"create-cart-{i}"

    for i in range(500):
        futures[executor.submit(get_item, i)] = f"get-item-{i}"
        
    for i in range(501, 600):
        futures[executor.submit(get_item, i)] = f"get-false-item-{i}"

    for _ in range(100):
        futures[executor.submit(create_not_empty_carts, existing_items)] = "create-not-empty-carts"

    for _ in range(100):
        futures[executor.submit(create_empty_cart)] = "create-empty-cart"
    for i in range(500):
        futures[executor.submit(get_cart, i)] = "get-cart"
    for i in range(501, 700):
        futures[executor.submit(get_cart, i)] = "get-false-cart"

    for _ in range(50):
        futures[executor.submit(get_carts, {})] = "get-carts-default"
        
    futures[executor.submit(get_carts, {"offset": 1, "limit": 2})] = "get-carts-offset-limit"
    futures[executor.submit(get_carts, {"min_price": 1000.0})] = "get-carts-min-price"
    futures[executor.submit(get_carts, {"max_price": 20.0})] = "get-carts-max-price"
    futures[executor.submit(get_carts, {"min_quantity": 1})] = "get-carts-min-quantity"
    futures[executor.submit(get_carts, {"max_quantity": 0})] = "get-carts-max-quantity"
    futures[executor.submit(get_carts, {"offset": -1})] = "get-carts-negative-offset"
    futures[executor.submit(get_carts, {"limit": 0})] = "get-carts-zero-limit"
    futures[executor.submit(get_carts, {"limit": -1})] = "get-carts-negative-limit"
    futures[executor.submit(get_carts, {"min_price": -1.0})] = "get-carts-negative-min-price"
    futures[executor.submit(get_carts, {"max_price": -1.0})] = "get-carts-negative-max-price"
    futures[executor.submit(get_carts, {"min_quantity": -1})] = "get-carts-negative-min-quantity"
    futures[executor.submit(get_carts, {"max_quantity": -1})] = "get-carts-negative-max-quantity"

    for _ in range(100):
        new_item_id = create_item()
        futures[executor.submit(get_item, new_item_id)] = "get-item"
        futures[executor.submit(delete_item, new_item_id)] = "delete-item"
    print("finished")
