import logging

from flask import Flask, jsonify

from crawler_magazine.model.db import Database

logger = logging.getLogger(__name__)

app = Flask(__name__)

with Database() as db:
    db._ensure_indexes()


@app.route("/")
def root():
    return "<h1>Magazine Crawler!</h1>"


@app.route("/health")
def health():
    return "I'm fine!"


@app.route("/find-ean/<ean>")
def find_ean_endpoint(ean):
    with Database() as db:
        ean = db.find_ean(ean)
    return jsonify(ean)


@app.route("/find-sku/<sku>")
def find_sku_endpoint(sku):
    with Database() as db:
        sku = db.find_sku(sku)
    return jsonify(sku)


@app.route("/count-items-by-brand/<brand>")
def brand_endpoint(brand):
    with Database() as db:
        brand = db.count_product_by_brand(brand)
    return jsonify(brand)


@app.route("/available-items")
def available_endpoint():
    with Database() as db:
        available = db.count_available_rupture_products()
    return jsonify(available)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
