from pymongo import MongoClient

MONGO_URI = "mongodb+srv://engrawaisawan358:cczM9vQqeKtK9u0i@cluster0.zc395b4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["retail_chatbot"]
orders_collection = db["orders"]

# Test insert
orders_collection.insert_one({"test": "connection works"})
print("MongoDB connection successful!")