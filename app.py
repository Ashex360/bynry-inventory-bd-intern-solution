@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json

    # Validate input
    required_fields = ['name', 'sku', 'price', 'warehouse_id', 'initial_quantity']
    for field in required_fields:
        if field not in data:
            return {"error": f"Missing field: {field}"}, 400

    if Product.query.filter_by(sku=data['sku']).first():
        return {"error": "SKU must be unique"}, 400

    try:
        # Use transaction for atomicity
        with db.session.begin():
            product = Product(
                name=data['name'],
                sku=data['sku'],
                price=round(float(data['price']), 2)
            )
            db.session.add(product)
            db.session.flush()  # Get product.id before commit

            inventory = Inventory(
                product_id=product.id,
                warehouse_id=data['warehouse_id'],
                quantity=int(data['initial_quantity'])
            )
            db.session.add(inventory)

        return {"message": "Product created", "product_id": product.id}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
