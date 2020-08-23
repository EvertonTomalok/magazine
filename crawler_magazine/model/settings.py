from os import getenv

MONGODB_SETTINGS = {
    "url": getenv("MONGO_URL", "mongodb://magazine:magazine@localhost:27017")
}
