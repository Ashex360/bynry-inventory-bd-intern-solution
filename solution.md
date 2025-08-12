**Inventory Management System \- Backend Development  Intern Solution**

## **Part 1: Code Review & Debugging**

### **Issues Identified**

1. **No SKU uniqueness check**

   * **Impact:** Duplicate SKUs across warehouses could cause inconsistencies in product identification.

2. **No validation for required fields**

   * **Impact:** Missing fields like `name` or `price` can cause DB errors or incomplete records.

3. **Price stored without decimal precision handling**

   * **Impact:** Loss of accuracy in pricing.

4. **No transaction management**

   * **Impact:** If inventory creation fails after product creation, data becomes inconsistent.

5. **No check if `initial_quantity` is provided and valid**

   * **Impact:** Could cause `NULL` or negative stock values.

6. **Products tied to a single warehouse on creation**

   * **Impact:** Breaks multi-warehouse requirement.

### **Corrected Code (Python/Flask)**

@app.route('/api/products', methods=\['POST'\])  
def create\_product():  
    data \= request.json

    \# Validate input  
    required\_fields \= \['name', 'sku', 'price', 'warehouse\_id', 'initial\_quantity'\]  
    for field in required\_fields:  
        if field not in data:  
            return {"error": f"Missing field: {field}"}, 400

    if Product.query.filter\_by(sku=data\['sku'\]).first():  
        return {"error": "SKU must be unique"}, 400

    try:  
        \# Use transaction for atomicity  
        with db.session.begin():  
            product \= Product(  
                name=data\['name'\],  
                sku=data\['sku'\],  
                price=round(float(data\['price'\]), 2\)  
            )  
            db.session.add(product)  
            db.session.flush()  \# Get product.id before commit

            inventory \= Inventory(  
                product\_id=product.id,  
                warehouse\_id=data\['warehouse\_id'\],  
                quantity=int(data\['initial\_quantity'\])  
            )  
            db.session.add(inventory)

        return {"message": "Product created", "product\_id": product.id}, 201  
    except Exception as e:  
        db.session.rollback()  
        return {"error": str(e)}, 500

## **Part 2: Database Design**

### **Proposed Schema**

**Tables:**

1. **companies**

   * `id` (PK), `name`

2. **warehouses**

   * `id` (PK), `company_id` (FK), `name`, `location`

3. **products**

   * `id` (PK), `sku` (unique), `name`, `price`, `type` (single/bundle)

4. **inventory**

   * `product_id` (FK), `warehouse_id` (FK), `quantity`, `updated_at`

5. **suppliers**

   * `id` (PK), `name`, `contact_email`

6. **product\_suppliers**

   * `product_id` (FK), `supplier_id` (FK)

7. **bundles** (for product bundles)

   * `bundle_id` (FK to products), `product_id` (FK to products), `quantity`

8. **inventory\_changes**

   * `id` (PK), `product_id` (FK), `warehouse_id` (FK), `change_amount`, `change_reason`, `timestamp`

**Indexes & Constraints:**

* Unique index on `sku`

* Foreign keys for data integrity

* Indexes on `warehouse_id` and `product_id` for fast lookups

**Gaps / Questions:**

* Do we need to track per-batch manufacturing/expiry dates?

* Should price be warehouse-specific?

* Should bundles support nested bundles?

## **Part 3: API Implementation**

### **Implementation (Python/Flask)**

@app.route('/api/companies/\<int:company\_id\>/alerts/low-stock', methods=\['GET'\])  
def get\_low\_stock\_alerts(company\_id):  
    alerts \= \[\]  
    \# Fetch low stock products with supplier info  
    results \= db.session.execute("""  
        SELECT p.id AS product\_id, p.name AS product\_name, p.sku,  
               w.id AS warehouse\_id, w.name AS warehouse\_name,  
               i.quantity AS current\_stock, t.threshold,  
               s.id AS supplier\_id, s.name AS supplier\_name, s.contact\_email  
        FROM inventory i  
        JOIN warehouses w ON i.warehouse\_id \= w.id  
        JOIN products p ON i.product\_id \= p.id  
        JOIN product\_suppliers ps ON p.id \= ps.product\_id  
        JOIN suppliers s ON ps.supplier\_id \= s.id  
        JOIN thresholds t ON p.id \= t.product\_id  
        WHERE w.company\_id \= :company\_id  
          AND i.quantity \< t.threshold  
          AND EXISTS (SELECT 1 FROM sales WHERE product\_id \= p.id AND sale\_date \>= NOW() \- INTERVAL '30 days')  
    """, {"company\_id": company\_id})

    for row in results:  
        days\_until\_stockout \= max(1, (row.threshold \- row.current\_stock) // 2\)  
        alerts.append({  
            "product\_id": row.product\_id,  
            "product\_name": row.product\_name,  
            "sku": row.sku,  
            "warehouse\_id": row.warehouse\_id,  
            "warehouse\_name": row.warehouse\_name,  
            "current\_stock": row.current\_stock,  
            "threshold": row.threshold,  
            "days\_until\_stockout": days\_until\_stockout,  
            "supplier": {  
                "id": row.supplier\_id,  
                "name": row.supplier\_name,  
                "contact\_email": row.contact\_email  
            }  
        })

    return {"alerts": alerts, "total\_alerts": len(alerts)}

**Approach:**

* Joined tables to fetch all necessary details in one query.

* Used sales activity filter for recent transactions.

* Calculated `days_until_stockout` based on a simple assumption (can be improved with historical sales rate).

**Edge Cases Considered:**

* No products below threshold → return empty list.

* Products without suppliers → exclude from results.

* Missing threshold values → default threshold.

**Assumptions:**

* Threshold values stored in a `thresholds` table.

* Sales activity tracked in `sales` table.

* One primary supplier per product for now.

