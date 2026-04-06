import json
from flask import Flask, render_template, request, jsonify, session
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# ===============================
# Load environment variables
# ===============================
load_dotenv()  # loads variables from .env file

MONGO_URI = os.getenv("MONGO_URI")  # Mongo URI now comes from .env

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")  # optional secret key from .env

# ===============================
# MongoDB Setup
# ===============================
try:
    client = MongoClient(MONGO_URI)
    db = client["retail_chatbot"]
    orders_collection = db["orders"]
    print("MongoDB connection established successfully!")
except Exception as e:
    orders_collection = None
    print("MongoDB connection failed:", e)

# ===============================
# Load intents
# ===============================
with open('intents.json', 'r') as f:
    intents = json.load(f)['intents']

# ===============================
# Products
# ===============================
PRODUCTS = {
    "shirts": {"price": 25, "types": ["formal", "casual", "t-shirt"], "aliases": ["shirt", "shirts"]},
    "trousers": {"price": 40, "types": ["jeans", "chinos"], "aliases": ["trouser", "trousers"]},
    "jackets": {"price": 60, "types": ["leather", "denim", "hoodie"], "aliases": ["jacket", "jackets"]}
}

# ===============================
# Routes
# ===============================
@app.route("/")
def home():
    session.clear()
    return render_template("index.html")


@app.route("/get", methods=["POST"])
def chat():
    user_msg = request.json.get("msg", "").lower().strip()
    print(f"DEBUG: Stage={session.get('stage', 'None')}, User={user_msg}")

    # --- 1. Restart greeting ---
    if user_msg in ["hello", "hi", "hey"]:
        session.clear()
        session["stage"] = "product"
        prod_str = ", ".join([f"{p} (£{PRODUCTS[p]['price']})" for p in PRODUCTS])
        return jsonify({"msg": f"Hello! 👋 Welcome to RetailChatBot. What would you like to order? ({prod_str})"})

    # --- 2. Handle goodbyes/thanks ---
    if any(b in user_msg for b in ["bye", "goodbye", "thank"]):
        session.clear()
        return jsonify({"msg": "Goodbye! Have a great day and thank you for shopping!"})

    stage = session.get("stage", "product")

    # --- Product selection ---
    if stage == "product":
        for product_name, product_info in PRODUCTS.items():
            if any(alias in user_msg for alias in product_info["aliases"]):
                session["product"] = product_name
                session["stage"] = "type"
                session.modified = True
                return jsonify({"msg": f"Great! You selected {product_name}. Types available: {', '.join(product_info['types'])}"})
        return jsonify({"msg": "Please select from: shirts, trousers, or jackets."})

    # --- Type selection ---
    elif stage == "type":
        product = session.get("product")
        if product and user_msg in PRODUCTS[product]['types']:
            session["type"] = user_msg
            session["stage"] = "quantity"
            session.modified = True
            return jsonify({"msg": "How many would you like to purchase?"})
        return jsonify({"msg": f"Please choose from: {', '.join(PRODUCTS[product]['types'])}"})

    # --- Quantity selection ---
    elif stage == "quantity":
        if user_msg.isdigit():
            session["qty"] = int(user_msg)
            session["stage"] = "payment"
            session.modified = True
            return jsonify({"msg": "Items added to cart! Please enter your payment method (paypal, debit card, credit card)."})
        return jsonify({"msg": "Please enter a valid number (1, 2, 3, etc.)."})

    # --- Payment processing ---
    elif stage == "payment":
        product = session.get("product")
        ptype = session.get("type")
        qty = session.get("qty")

        if not all([product, ptype, qty]):
            return jsonify({"msg": "Error: Missing order details. Please start over with 'hello'."})

        total = qty * PRODUCTS[product]['price']

        # Save to MongoDB if available
        if orders_collection is not None:
            try:
                order_data = {
                    "product": product,
                    "type": ptype,
                    "quantity": qty,
                    "total": total,
                    "payment_method": user_msg
                }
                orders_collection.insert_one(order_data)
                print("Order saved to MongoDB successfully!")
            except Exception as e:
                print(f"MongoDB save error: {e}")

        receipt = [{"item": f"{qty}x {ptype} {product}", "total": total}]
        session.clear()

        return jsonify({
            "msg": f"Payment accepted! Total paid: £{total} for {qty} {ptype} {product}(s). Thank you for shopping! Type 'hello' for a new order.",
            "receipt_popup": True,
            "receipt": receipt,
            "total": total
        })

    return jsonify({"msg": "Please type 'hello' to start shopping."})


if __name__ == "__main__":
    app.run(debug=True, port=5050)