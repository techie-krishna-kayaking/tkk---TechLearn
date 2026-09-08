"""
=====================================================================
FILE: 91_Python_Master_Concepts_Interview_QA_Solutions.py
PURPOSE: Comprehensive Python practice for QA Engineers
         Covers Data Testing, ETL, API Testing, ML/AI QA, Automation
AUDIENCE: Senior QA Engineers (7+ years) testing data platforms
STRUCTURE: 120+ Interview Questions with Solutions
=====================================================================
"""

# =====================================================================
# SECTION 1: PYTHON FUNDAMENTALS FOR QA (Questions 1-20)
# =====================================================================

# ---------------------------------------------------------------------
# Q1: Basic data type validation
# Concept: Type checking, assertions
# ---------------------------------------------------------------------
def test_data_types():
    """Validate data types in test data"""
    customer_id = 12345
    customer_name = "John Doe"
    order_amount = 99.99
    is_active = True
    
    # Type assertions
    assert isinstance(customer_id, int), f"customer_id should be int, got {type(customer_id)}"
    assert isinstance(customer_name, str), f"customer_name should be str, got {type(customer_name)}"
    assert isinstance(order_amount, (int, float)), "order_amount should be numeric"
    assert isinstance(is_active, bool), "is_active should be bool"
    
    print("✓ All data types valid")


# ---------------------------------------------------------------------
# Q2: List operations for test data
# Concept: List comprehension, filtering
# ---------------------------------------------------------------------
def test_list_operations():
    """Filter and transform test data lists"""
    order_amounts = [100, 250, 50, 300, 75, 500, 25]
    
    # Filter orders > $100
    large_orders = [amt for amt in order_amounts if amt > 100]
    assert large_orders == [250, 300, 500], f"Expected [250, 300, 500], got {large_orders}"
    
    # Apply 10% discount
    discounted = [amt * 0.9 for amt in order_amounts]
    assert len(discounted) == len(order_amounts), "Discount list length mismatch"
    
    # Sum total
    total = sum(order_amounts)
    assert total == 1300, f"Expected total 1300, got {total}"
    
    print("✓ List operations validated")


# ---------------------------------------------------------------------
# Q3: Dictionary validation
# Concept: Dict operations, key existence
# ---------------------------------------------------------------------
def test_dictionary_validation():
    """Validate API response dictionaries"""
    api_response = {
        "status": "success",
        "data": {
            "customer_id": 123,
            "name": "Alice",
            "email": "alice@example.com"
        },
        "timestamp": "2024-01-15T10:30:00Z"
    }
    
    # Required keys validation
    required_keys = ["status", "data", "timestamp"]
    for key in required_keys:
        assert key in api_response, f"Missing required key: {key}"
    
    # Nested key validation
    assert "customer_id" in api_response["data"], "Missing customer_id in data"
    
    # Value validation
    assert api_response["status"] == "success", "API call failed"
    
    print("✓ Dictionary structure validated")


# ---------------------------------------------------------------------
# Q4: String manipulation for data cleaning
# Concept: strip, replace, split, join
# ---------------------------------------------------------------------
def test_string_cleaning():
    """Clean and normalize string data"""
    raw_data = "  John  Doe  ,  alice@EXAMPLE.com  , 123-456-7890  "
    
    # Clean whitespace
    cleaned = raw_data.strip()
    assert not cleaned.startswith(" "), "Leading whitespace not removed"
    
    # Normalize email
    parts = [p.strip() for p in raw_data.split(",")]
    email = parts[1].lower()
    assert email == "alice@example.com", f"Email normalization failed: {email}"
    
    # Format phone (remove dashes)
    phone = parts[2].replace("-", "")
    assert phone == "1234567890", f"Phone formatting failed: {phone}"
    
    print("✓ String cleaning validated")


# ---------------------------------------------------------------------
# Q5: Date/time handling
# Concept: datetime module, formatting, arithmetic
# ---------------------------------------------------------------------
from datetime import datetime, timedelta

def test_date_operations():
    """Validate date calculations"""
    order_date = datetime(2024, 1, 15, 10, 30, 0)
    ship_date = datetime(2024, 1, 17, 14, 0, 0)
    
    # Date difference
    time_to_ship = ship_date - order_date
    assert time_to_ship.days == 2, f"Expected 2 days, got {time_to_ship.days}"
    
    # Date formatting
    formatted = order_date.strftime("%Y-%m-%d")
    assert formatted == "2024-01-15", f"Date format incorrect: {formatted}"
    
    # Future date calculation
    expected_delivery = order_date + timedelta(days=7)
    assert expected_delivery.day == 22, "Expected delivery date incorrect"
    
    print("✓ Date operations validated")


# ---------------------------------------------------------------------
# Q6: File I/O - Reading test data
# Concept: Reading files, context managers
# ---------------------------------------------------------------------
def test_file_reading():
    """Read and validate file contents"""
    # Create test file
    test_file = "test_data.txt"
    test_content = "Order 1: $100\nOrder 2: $200\nOrder 3: $300"
    
    with open(test_file, "w") as f:
        f.write(test_content)
    
    # Read and validate
    with open(test_file, "r") as f:
        lines = f.readlines()
    
    assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}"
    assert "$100" in lines[0], "First order amount not found"
    
    # Cleanup
    import os
    os.remove(test_file)
    
    print("✓ File I/O validated")


# ---------------------------------------------------------------------
# Q7: Exception handling in tests
# Concept: try/except, custom exceptions
# ---------------------------------------------------------------------
def test_exception_handling():
    """Handle expected errors gracefully"""
    
    def divide(a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
    # Test valid case
    result = divide(10, 2)
    assert result == 5, "Division failed"
    
    # Test exception case
    try:
        divide(10, 0)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Cannot divide by zero", "Wrong error message"
    
    print("✓ Exception handling validated")


# ---------------------------------------------------------------------
# Q8: List comprehension vs filter/map
# Concept: Functional programming patterns
# ---------------------------------------------------------------------
def test_functional_patterns():
    """Compare list comprehension and functional approaches"""
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # List comprehension
    evens_comp = [n for n in numbers if n % 2 == 0]
    
    # Filter + lambda
    evens_filter = list(filter(lambda n: n % 2 == 0, numbers))
    
    # Both should produce same result
    assert evens_comp == evens_filter, "Filtering methods differ"
    assert evens_comp == [2, 4, 6, 8, 10], "Wrong even numbers"
    
    # Map example (square numbers)
    squared = list(map(lambda n: n**2, numbers))
    assert squared[0] == 1 and squared[-1] == 100, "Mapping failed"
    
    print("✓ Functional patterns validated")


# ---------------------------------------------------------------------
# Q9: Set operations for data comparison
# Concept: Sets, intersection, difference
# ---------------------------------------------------------------------
def test_set_operations():
    """Compare datasets using sets"""
    source_customers = {1, 2, 3, 4, 5, 6}
    target_customers = {4, 5, 6, 7, 8}
    
    # Customers in source but not target (missing)
    missing = source_customers - target_customers
    assert missing == {1, 2, 3}, f"Missing customers: {missing}"
    
    # Customers in both (common)
    common = source_customers & target_customers
    assert common == {4, 5, 6}, f"Common customers: {common}"
    
    # Customers in either (union)
    all_customers = source_customers | target_customers
    assert all_customers == {1, 2, 3, 4, 5, 6, 7, 8}, "Union incorrect"
    
    print("✓ Set operations validated")


# ---------------------------------------------------------------------
# Q10: Tuple unpacking
# Concept: Multiple assignment, tuple usage
# ---------------------------------------------------------------------
def test_tuple_unpacking():
    """Validate tuple unpacking in test data"""
    
    def get_customer_info():
        return ("John Doe", "john@example.com", 35)
    
    # Unpack tuple
    name, email, age = get_customer_info()
    
    assert name == "John Doe", "Name mismatch"
    assert email == "john@example.com", "Email mismatch"
    assert age == 35, "Age mismatch"
    
    # Swap values
    a, b = 10, 20
    a, b = b, a
    assert a == 20 and b == 10, "Swap failed"
    
    print("✓ Tuple unpacking validated")


# ---------------------------------------------------------------------
# Q11: Enumerate for indexed iteration
# Concept: enumerate() function
# ---------------------------------------------------------------------
def test_enumerate_usage():
    """Use enumerate to track position in test validation"""
    test_cases = ["test1", "test2", "test3"]
    expected_order = ["test1", "test2", "test3"]
    
    for index, test_case in enumerate(test_cases):
        assert test_case == expected_order[index], \
            f"Order mismatch at position {index}: {test_case} != {expected_order[index]}"
    
    print("✓ Enumerate validated")


# ---------------------------------------------------------------------
# Q12: Zip for parallel iteration
# Concept: zip() function
# ---------------------------------------------------------------------
def test_zip_usage():
    """Compare two lists element by element"""
    actual_values = [100, 200, 300]
    expected_values = [100, 200, 300]
    
    for actual, expected in zip(actual_values, expected_values):
        assert actual == expected, f"Mismatch: {actual} != {expected}"
    
    # Zip with different lengths (stops at shortest)
    list1 = [1, 2, 3]
    list2 = ['a', 'b']
    zipped = list(zip(list1, list2))
    assert len(zipped) == 2, "Zip should stop at shortest list"
    
    print("✓ Zip validated")


# ---------------------------------------------------------------------
# Q13: Default dict for counting
# Concept: defaultdict from collections
# ---------------------------------------------------------------------
from collections import defaultdict

def test_defaultdict_counting():
    """Count occurrences using defaultdict"""
    events = ['login', 'logout', 'login', 'purchase', 'login', 'logout']
    
    # Count events
    event_counts = defaultdict(int)
    for event in events:
        event_counts[event] += 1
    
    assert event_counts['login'] == 3, "Login count incorrect"
    assert event_counts['logout'] == 2, "Logout count incorrect"
    assert event_counts['purchase'] == 1, "Purchase count incorrect"
    
    print("✓ Defaultdict counting validated")


# ---------------------------------------------------------------------
# Q14: Counter for frequency analysis
# Concept: Counter from collections
# ---------------------------------------------------------------------
from collections import Counter

def test_counter_usage():
    """Analyze data frequency"""
    statuses = ['success', 'success', 'failed', 'success', 'failed', 'success']
    
    status_counts = Counter(statuses)
    
    assert status_counts['success'] == 4, "Success count wrong"
    assert status_counts['failed'] == 2, "Failed count wrong"
    
    # Most common
    most_common = status_counts.most_common(1)
    assert most_common[0] == ('success', 4), "Most common incorrect"
    
    print("✓ Counter validated")


# ---------------------------------------------------------------------
# Q15: Named tuple for structured data
# Concept: namedtuple from collections
# ---------------------------------------------------------------------
from collections import namedtuple

def test_namedtuple():
    """Use named tuples for test data"""
    Customer = namedtuple('Customer', ['id', 'name', 'email'])
    
    customer = Customer(id=123, name='Alice', email='alice@example.com')
    
    assert customer.id == 123, "Customer ID mismatch"
    assert customer.name == 'Alice', "Customer name mismatch"
    assert customer[2] == 'alice@example.com', "Email access by index failed"
    
    print("✓ Named tuple validated")


# ---------------------------------------------------------------------
# Q16: Lambda functions for quick operations
# Concept: Anonymous functions
# ---------------------------------------------------------------------
def test_lambda_functions():
    """Use lambdas for test data transformations"""
    orders = [
        {'id': 1, 'amount': 100},
        {'id': 2, 'amount': 250},
        {'id': 3, 'amount': 75}
    ]
    
    # Sort by amount
    sorted_orders = sorted(orders, key=lambda x: x['amount'], reverse=True)
    assert sorted_orders[0]['amount'] == 250, "Sorting failed"
    
    # Filter using lambda
    high_value = list(filter(lambda x: x['amount'] > 100, orders))
    assert len(high_value) == 1, "Filter failed"
    
    print("✓ Lambda functions validated")


# ---------------------------------------------------------------------
# Q17: Any and All for validation
# Concept: any(), all() built-in functions
# ---------------------------------------------------------------------
def test_any_all():
    """Validate conditions across collections"""
    test_results = [True, True, True, True]
    
    # All tests passed
    assert all(test_results), "Not all tests passed"
    
    # At least one test failed
    test_results_2 = [True, False, True]
    assert not all(test_results_2), "All should be False"
    assert any(test_results_2), "Any should be True"
    
    # Check if any value is negative
    values = [10, 20, 30, 40]
    has_negative = any(v < 0 for v in values)
    assert not has_negative, "Should have no negative values"
    
    print("✓ Any/All validated")


# ---------------------------------------------------------------------
# Q18: Regular expressions for pattern matching
# Concept: re module
# ---------------------------------------------------------------------
import re

def test_regex_validation():
    """Validate data formats using regex"""
    email = "test.user@example.com"
    phone = "123-456-7890"
    
    # Email pattern
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    assert re.match(email_pattern, email), "Email format invalid"
    
    # Phone pattern
    phone_pattern = r'^\d{3}-\d{3}-\d{4}$'
    assert re.match(phone_pattern, phone), "Phone format invalid"
    
    # Extract numbers from string
    text = "Order 12345 total $99.99"
    numbers = re.findall(r'\d+', text)
    assert numbers == ['12345', '99', '99'], f"Number extraction failed: {numbers}"
    
    print("✓ Regex validation passed")


# ---------------------------------------------------------------------
# Q19: JSON parsing for API testing
# Concept: json module
# ---------------------------------------------------------------------
import json

def test_json_operations():
    """Parse and validate JSON responses"""
    json_string = '{"customer_id": 123, "name": "Alice", "orders": [1, 2, 3]}'
    
    # Parse JSON
    data = json.loads(json_string)
    
    assert data['customer_id'] == 123, "Customer ID mismatch"
    assert len(data['orders']) == 3, "Order count mismatch"
    
    # Convert to JSON
    test_data = {'status': 'success', 'count': 5}
    json_output = json.dumps(test_data)
    assert 'success' in json_output, "JSON serialization failed"
    
    print("✓ JSON operations validated")


# ---------------------------------------------------------------------
# Q20: Path operations for file testing
# Concept: pathlib module
# ---------------------------------------------------------------------
from pathlib import Path

def test_path_operations():
    """Work with file paths"""
    # Create path
    data_dir = Path("test_data")
    file_path = data_dir / "orders.csv"
    
    assert str(file_path) == "test_data/orders.csv" or str(file_path) == "test_data\\orders.csv", \
        "Path construction failed"
    
    # Check file extension
    assert file_path.suffix == ".csv", "Extension check failed"
    
    # Get filename without extension
    assert file_path.stem == "orders", "Stem extraction failed"
    
    print("✓ Path operations validated")


# =====================================================================
# SECTION 2: DATA TESTING WITH PYTHON (Questions 21-50)
# =====================================================================

# ---------------------------------------------------------------------
# Q21: CSV file validation
# Concept: csv module
# ---------------------------------------------------------------------
import csv

def test_csv_validation():
    """Validate CSV file structure and content"""
    # Create test CSV
    csv_file = "test_orders.csv"
    test_data = [
        ['order_id', 'customer_id', 'amount'],
        ['1', '101', '100.00'],
        ['2', '102', '250.50']
    ]
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(test_data)
    
    # Read and validate
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) == 2, f"Expected 2 data rows, got {len(rows)}"
    assert rows[0]['order_id'] == '1', "First order ID mismatch"
    assert float(rows[1]['amount']) == 250.50, "Second amount mismatch"
    
    # Cleanup
    import os
    os.remove(csv_file)
    
    print("✓ CSV validation passed")


# ---------------------------------------------------------------------
# Q22: Pandas DataFrame basics
# Concept: pandas library
# ---------------------------------------------------------------------
import pandas as pd
import numpy as np

def test_pandas_basics():
    """Basic pandas operations for data testing"""
    # Create DataFrame
    df = pd.DataFrame({
        'customer_id': [1, 2, 3, 4, 5],
        'order_amount': [100, 250, 75, 300, 150],
        'status': ['completed', 'completed', 'pending', 'completed', 'cancelled']
    })
    
    # Shape validation
    assert df.shape == (5, 3), f"DataFrame shape incorrect: {df.shape}"
    
    # Column validation
    expected_columns = ['customer_id', 'order_amount', 'status']
    assert list(df.columns) == expected_columns, "Columns mismatch"
    
    # Data type validation
    assert df['customer_id'].dtype == np.int64, "customer_id type incorrect"
    assert df['status'].dtype == 'object', "status type incorrect"
    
    print("✓ Pandas basics validated")


# ---------------------------------------------------------------------
# Q23: Pandas data filtering
# Concept: Boolean indexing
# ---------------------------------------------------------------------
def test_pandas_filtering():
    """Filter data using pandas"""
    df = pd.DataFrame({
        'product': ['A', 'B', 'C', 'D', 'E'],
        'price': [10, 25, 50, 75, 100],
        'category': ['Electronics', 'Clothing', 'Electronics', 'Home', 'Electronics']
    })
    
    # Filter products > $50
    expensive = df[df['price'] > 50]
    assert len(expensive) == 2, f"Expected 2 expensive products, got {len(expensive)}"
    
    # Filter by category
    electronics = df[df['category'] == 'Electronics']
    assert len(electronics) == 3, "Electronics count incorrect"
    
    # Multiple conditions
    high_value_electronics = df[(df['category'] == 'Electronics') & (df['price'] > 25)]
    assert len(high_value_electronics) == 2, "Combined filter failed"
    
    print("✓ Pandas filtering validated")


# ---------------------------------------------------------------------
# Q24: Pandas aggregations
# Concept: groupby, sum, mean, count
# ---------------------------------------------------------------------
def test_pandas_aggregations():
    """Aggregate data for validation"""
    df = pd.DataFrame({
        'category': ['Electronics', 'Clothing', 'Electronics', 'Clothing', 'Home'],
        'sales': [1000, 500, 1500, 300, 700]
    })
    
    # Group by category
    grouped = df.groupby('category')['sales'].sum()
    
    assert grouped['Electronics'] == 2500, "Electronics sales incorrect"
    assert grouped['Clothing'] == 800, "Clothing sales incorrect"
    
    # Multiple aggregations
    agg_result = df.groupby('category')['sales'].agg(['sum', 'mean', 'count'])
    assert agg_result.loc['Electronics', 'count'] == 2, "Electronics count wrong"
    
    print("✓ Pandas aggregations validated")


# ---------------------------------------------------------------------
# Q25: Pandas null value handling
# Concept: isnull, fillna, dropna
# ---------------------------------------------------------------------
def test_pandas_null_handling():
    """Handle missing data"""
    df = pd.DataFrame({
        'customer_id': [1, 2, 3, 4, 5],
        'email': ['a@ex.com', None, 'c@ex.com', 'd@ex.com', None],
        'age': [25, 30, None, 40, 35]
    })
    
    # Check for nulls
    null_counts = df.isnull().sum()
    assert null_counts['email'] == 2, "Email null count wrong"
    assert null_counts['age'] == 1, "Age null count wrong"
    
    # Fill nulls
    df_filled = df.fillna({'email': 'unknown@example.com', 'age': 0})
    assert df_filled['email'].isnull().sum() == 0, "Nulls not filled"
    
    # Drop rows with nulls
    df_dropped = df.dropna()
    assert len(df_dropped) == 2, "Dropped rows count incorrect"
    
    print("✓ Null handling validated")


# ---------------------------------------------------------------------
# Q26: Pandas merge (JOIN)
# Concept: merge, join operations
# ---------------------------------------------------------------------
def test_pandas_merge():
    """Join DataFrames like SQL JOIN"""
    customers = pd.DataFrame({
        'customer_id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie']
    })
    
    orders = pd.DataFrame({
        'order_id': [101, 102, 103],
        'customer_id': [1, 1, 2],
        'amount': [100, 150, 200]
    })
    
    # Inner join
    merged = pd.merge(customers, orders, on='customer_id', how='inner')
    assert len(merged) == 3, "Merge row count incorrect"
    assert 'name' in merged.columns, "Name column missing after merge"
    
    # Left join
    left_merged = pd.merge(customers, orders, on='customer_id', how='left')
    assert len(left_merged) == 3, "Left join should keep all customers"
    
    print("✓ Pandas merge validated")


# ---------------------------------------------------------------------
# Q27: Pandas data validation with assertions
# Concept: Custom validation functions
# ---------------------------------------------------------------------
def test_pandas_data_validation():
    """Validate data quality in DataFrame"""
    df = pd.DataFrame({
        'order_id': [1, 2, 3, 4, 5],
        'amount': [100, 250, 75, 300, 150],
        'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', 
                                 '2024-01-04', '2024-01-05'])
    })
    
    # No duplicates in order_id
    assert df['order_id'].duplicated().sum() == 0, "Duplicate order IDs found"
    
    # All amounts positive
    assert (df['amount'] > 0).all(), "Negative amounts found"
    
    # Dates in ascending order
    assert df['date'].is_monotonic_increasing, "Dates not in order"
    
    # Amount within expected range
    assert df['amount'].between(0, 1000).all(), "Amounts out of range"
    
    print("✓ Data validation passed")


# ---------------------------------------------------------------------
# Q28: Pandas date operations
# Concept: Datetime handling
# ---------------------------------------------------------------------
def test_pandas_datetime():
    """Work with dates in pandas"""
    df = pd.DataFrame({
        'order_date': pd.to_datetime(['2024-01-15', '2024-02-20', '2024-03-10'])
    })
    
    # Extract date components
    df['year'] = df['order_date'].dt.year
    df['month'] = df['order_date'].dt.month
    df['day'] = df['order_date'].dt.day
    
    assert df.loc[0, 'year'] == 2024, "Year extraction failed"
    assert df.loc[1, 'month'] == 2, "Month extraction failed"
    
    # Date arithmetic
    df['delivery_date'] = df['order_date'] + pd.Timedelta(days=7)
    assert df.loc[0, 'delivery_date'].day == 22, "Date arithmetic failed"
    
    print("✓ Datetime operations validated")


# ---------------------------------------------------------------------
# Q29: Pandas row iteration (use sparingly)
# Concept: iterrows, apply
# ---------------------------------------------------------------------
def test_pandas_iteration():
    """Iterate over DataFrame rows"""
    df = pd.DataFrame({
        'value': [1, 2, 3, 4, 5]
    })
    
    # Using apply (vectorized, preferred)
    df['squared'] = df['value'].apply(lambda x: x**2)
    assert df.loc[2, 'squared'] == 9, "Apply failed"
    
    # Using iterrows (slower, avoid if possible)
    total = 0
    for idx, row in df.iterrows():
        total += row['value']
    assert total == 15, "Iterrows summation failed"
    
    print("✓ Iteration methods validated")


# ---------------------------------------------------------------------
# Q30: Pandas pivot tables
# Concept: Pivot, cross-tabulation
# ---------------------------------------------------------------------
def test_pandas_pivot():
    """Create pivot tables for analysis"""
    df = pd.DataFrame({
        'category': ['A', 'B', 'A', 'B', 'A'],
        'region': ['East', 'East', 'West', 'West', 'East'],
        'sales': [100, 150, 200, 250, 300]
    })
    
    # Pivot table
    pivot = df.pivot_table(values='sales', index='category', columns='region', aggfunc='sum')
    
    assert pivot.loc['A', 'East'] == 400, "Pivot calculation incorrect"
    assert pivot.loc['B', 'West'] == 250, "Pivot value wrong"
    
    print("✓ Pivot table validated")


# ---------------------------------------------------------------------
# Q31: NumPy array operations
# Concept: numpy basics
# ---------------------------------------------------------------------
def test_numpy_operations():
    """Basic numpy operations for numerical testing"""
    arr = np.array([1, 2, 3, 4, 5])
    
    # Array operations
    assert arr.sum() == 15, "Sum incorrect"
    assert arr.mean() == 3.0, "Mean incorrect"
    assert arr.std() == np.std([1, 2, 3, 4, 5]), "Std deviation incorrect"
    
    # Element-wise operations
    doubled = arr * 2
    assert doubled[0] == 2 and doubled[-1] == 10, "Multiplication failed"
    
    # Comparison
    greater_than_3 = arr > 3
    assert greater_than_3.sum() == 2, "Comparison failed"
    
    print("✓ NumPy operations validated")


# ---------------------------------------------------------------------
# Q32: Database connection testing (SQLite example)
# Concept: sqlite3 module
# ---------------------------------------------------------------------
import sqlite3

def test_database_connection():
    """Test database connectivity and queries"""
    # Create in-memory database
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            amount REAL
        )
    ''')
    
    # Insert test data
    test_data = [(1, 101, 100.0), (2, 102, 250.5), (3, 101, 75.0)]
    cursor.executemany('INSERT INTO orders VALUES (?, ?, ?)', test_data)
    conn.commit()
    
    # Query and validate
    cursor.execute('SELECT COUNT(*) FROM orders')
    count = cursor.fetchone()[0]
    assert count == 3, f"Expected 3 orders, got {count}"
    
    # Sum by customer
    cursor.execute('SELECT customer_id, SUM(amount) FROM orders GROUP BY customer_id')
    results = cursor.fetchall()
    assert len(results) == 2, "Customer count incorrect"
    
    conn.close()
    print("✓ Database operations validated")


# ---------------------------------------------------------------------
# Q33: API response validation
# Concept: requests library simulation
# ---------------------------------------------------------------------
def test_api_response_structure():
    """Validate API response structure"""
    # Simulated API response
    response_data = {
        "status": 200,
        "headers": {"Content-Type": "application/json"},
        "body": {
            "success": True,
            "data": [
                {"id": 1, "name": "Product A"},
                {"id": 2, "name": "Product B"}
            ],
            "count": 2
        }
    }
    
    # Validate status code
    assert response_data["status"] == 200, "Status code not 200"
    
    # Validate content type
    assert response_data["headers"]["Content-Type"] == "application/json", \
        "Content-Type incorrect"
    
    # Validate body structure
    body = response_data["body"]
    assert body["success"] is True, "Success flag not True"
    assert body["count"] == len(body["data"]), "Count mismatch"
    
    print("✓ API response structure validated")


# ---------------------------------------------------------------------
# Q34: Data reconciliation between source and target
# Concept: Comparing datasets
# ---------------------------------------------------------------------
def test_data_reconciliation():
    """Reconcile data between two systems"""
    source_df = pd.DataFrame({
        'id': [1, 2, 3, 4],
        'value': [100, 200, 300, 400]
    })
    
    target_df = pd.DataFrame({
        'id': [1, 2, 3, 4],
        'value': [100, 200, 300, 400]
    })
    
    # Compare DataFrames
    comparison = source_df.equals(target_df)
    assert comparison, "DataFrames don't match"
    
    # Detailed comparison
    merged = source_df.merge(target_df, on='id', suffixes=('_source', '_target'))
    merged['match'] = merged['value_source'] == merged['value_target']
    
    assert merged['match'].all(), "Values don't match"
    
    print("✓ Data reconciliation passed")


# ---------------------------------------------------------------------
# Q35: Performance timing for tests
# Concept: time module
# ---------------------------------------------------------------------
import time

def test_performance_timing():
    """Measure execution time"""
    start = time.time()
    
    # Simulate some work
    result = sum(range(1000000))
    
    end = time.time()
    duration = end - start
    
    assert duration < 1.0, f"Operation too slow: {duration:.3f}s"
    print(f"✓ Performance check passed ({duration:.3f}s)")


# ---------------------------------------------------------------------
# Q36: Memory usage validation
# Concept: sys.getsizeof
# ---------------------------------------------------------------------
import sys

def test_memory_usage():
    """Check memory usage of objects"""
    small_list = [1, 2, 3]
    large_list = list(range(100000))
    
    small_size = sys.getsizeof(small_list)
    large_size = sys.getsizeof(large_list)
    
    assert large_size > small_size, "Memory size comparison failed"
    assert large_size < 10 * 1024 * 1024, "Object using >10MB"  # 10MB limit
    
    print(f"✓ Memory usage validated (small: {small_size}B, large: {large_size}B)")


# ---------------------------------------------------------------------
# Q37: Fuzzy string matching for data quality
# Concept: difflib library
# ---------------------------------------------------------------------
from difflib import SequenceMatcher

def test_fuzzy_matching():
    """Match similar strings"""
    string1 = "John Doe"
    string2 = "Jon Doe"  # Typo
    
    # Calculate similarity
    similarity = SequenceMatcher(None, string1, string2).ratio()
    
    # Allow 90% similarity for near-matches
    assert similarity >= 0.90, f"Similarity too low: {similarity:.2%}"
    
    print(f"✓ Fuzzy matching validated (similarity: {similarity:.2%})")


# ---------------------------------------------------------------------
# Q38: Checksum validation
# Concept: hashlib module
# ---------------------------------------------------------------------
import hashlib

def test_checksum_validation():
    """Validate file integrity with checksums"""
    data = b"This is test data for checksum validation"
    
    # Calculate MD5 checksum
    md5_hash = hashlib.md5(data).hexdigest()
    
    # Recalculate and compare
    recalculated = hashlib.md5(data).hexdigest()
    assert md5_hash == recalculated, "Checksums don't match"
    
    # SHA256 (more secure)
    sha256_hash = hashlib.sha256(data).hexdigest()
    assert len(sha256_hash) == 64, "SHA256 hash wrong length"
    
    print("✓ Checksum validation passed")


# ---------------------------------------------------------------------
# Q39: Retry logic for flaky tests
# Concept: Decorators, retry pattern
# ---------------------------------------------------------------------
def retry(max_attempts=3, delay=1):
    """Decorator to retry flaky operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.1)
def flaky_operation():
    """Simulated flaky operation"""
    import random
    if random.random() < 0.5:  # 50% failure rate
        raise Exception("Random failure")
    return "Success"

def test_retry_logic():
    """Test retry mechanism"""
    # Should eventually succeed due to retries
    result = flaky_operation()
    assert result == "Success", "Retry logic failed"
    
    print("✓ Retry logic validated")


# ---------------------------------------------------------------------
# Q40: Parameterized testing
# Concept: Test multiple inputs
# ---------------------------------------------------------------------
def validate_email(email):
    """Simple email validation"""
    return '@' in email and '.' in email.split('@')[1]

def test_parameterized():
    """Test with multiple parameters"""
    test_cases = [
        ("valid@example.com", True),
        ("invalid.email.com", False),
        ("another@test.co.uk", True),
        ("missing@domain", False)
    ]
    
    for email, expected in test_cases:
        result = validate_email(email)
        assert result == expected, f"Email validation failed for {email}"
    
    print("✓ Parameterized testing passed")


# ---------------------------------------------------------------------
# Q41: Data sampling for large datasets
# Concept: Random sampling
# ---------------------------------------------------------------------
import random

def test_data_sampling():
    """Sample data for testing large datasets"""
    large_dataset = list(range(1000000))
    
    # Random sample (10%)
    sample = random.sample(large_dataset, k=100000)
    
    assert len(sample) == 100000, "Sample size incorrect"
    assert len(set(sample)) == 100000, "Sample has duplicates"
    
    # Statistical validation on sample
    sample_mean = np.mean(sample)
    expected_mean = np.mean(large_dataset)
    
    # Sample mean should be close to population mean
    tolerance = 0.05 * expected_mean  # 5% tolerance
    assert abs(sample_mean - expected_mean) < tolerance, "Sample not representative"
    
    print("✓ Data sampling validated")


# ---------------------------------------------------------------------
# Q42: Outlier detection
# Concept: IQR method
# ---------------------------------------------------------------------
def test_outlier_detection():
    """Detect outliers in data"""
    data = [10, 12, 14, 15, 16, 18, 20, 22, 25, 100]  # 100 is outlier
    
    # IQR method
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    outliers = [x for x in data if x < lower_bound or x > upper_bound]
    
    assert 100 in outliers, "Outlier not detected"
    assert len(outliers) == 1, "Too many outliers detected"
    
    print("✓ Outlier detection validated")


# ---------------------------------------------------------------------
# Q43: Data type coercion
# Concept: Type conversion validation
# ---------------------------------------------------------------------
def test_type_coercion():
    """Validate data type conversions"""
    df = pd.DataFrame({
        'id': ['1', '2', '3'],  # Strings that should be integers
        'amount': ['100.50', '200.75', '300.25']  # Strings that should be floats
    })
    
    # Convert types
    df['id'] = df['id'].astype(int)
    df['amount'] = df['amount'].astype(float)
    
    assert df['id'].dtype == np.int64, "ID not converted to int"
    assert df['amount'].dtype == np.float64, "Amount not converted to float"
    
    # Validate values after conversion
    assert df.loc[0, 'id'] == 1, "Converted value incorrect"
    assert df.loc[1, 'amount'] == 200.75, "Converted amount incorrect"
    
    print("✓ Type coercion validated")


# ---------------------------------------------------------------------
# Q44: Data deduplication
# Concept: Removing duplicates
# ---------------------------------------------------------------------
def test_deduplication():
    """Remove duplicate records"""
    df = pd.DataFrame({
        'customer_id': [1, 2, 2, 3, 3, 3],
        'email': ['a@ex.com', 'b@ex.com', 'b@ex.com', 'c@ex.com', 'c@ex.com', 'c@ex.com'],
        'created_date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', 
                                         '2024-01-04', '2024-01-05', '2024-01-06'])
    })
    
    # Remove duplicates, keep last
    deduped = df.drop_duplicates(subset=['customer_id'], keep='last')
    
    assert len(deduped) == 3, "Deduplication failed"
    assert deduped[deduped['customer_id'] == 3]['created_date'].iloc[0] == pd.to_datetime('2024-01-06'), \
        "Wrong record kept after deduplication"
    
    print("✓ Deduplication validated")


# ---------------------------------------------------------------------
# Q45: Schema validation
# Concept: Validate DataFrame schema
# ---------------------------------------------------------------------
def test_schema_validation():
    """Validate DataFrame schema matches expected"""
    df = pd.DataFrame({
        'order_id': [1, 2, 3],
        'customer_id': [101, 102, 103],
        'amount': [100.0, 250.5, 75.0]
    })
    
    # Expected schema
    expected_schema = {
        'order_id': np.int64,
        'customer_id': np.int64,
        'amount': np.float64
    }
    
    # Validate
    for col, expected_type in expected_schema.items():
        assert col in df.columns, f"Missing column: {col}"
        assert df[col].dtype == expected_type, \
            f"Column {col} type mismatch: expected {expected_type}, got {df[col].dtype}"
    
    print("✓ Schema validation passed")


# ---------------------------------------------------------------------
# Q46: Row count validation
# Concept: Count reconciliation
# ---------------------------------------------------------------------
def test_row_count_validation():
    """Validate row counts match expected"""
    source_count = 1000
    
    df = pd.DataFrame({'id': range(1000)})
    
    assert len(df) == source_count, f"Row count mismatch: {len(df)} != {source_count}"
    
    # After filtering
    filtered = df[df['id'] >= 500]
    expected_filtered_count = 500
    
    assert len(filtered) == expected_filtered_count, \
        f"Filtered count mismatch: {len(filtered)} != {expected_filtered_count}"
    
    print("✓ Row count validation passed")


# ---------------------------------------------------------------------
# Q47: Column value range validation
# Concept: Range checks
# ---------------------------------------------------------------------
def test_range_validation():
    """Validate values within expected ranges"""
    df = pd.DataFrame({
        'age': [25, 30, 35, 40, 45],
        'salary': [50000, 60000, 70000, 80000, 90000]
    })
    
    # Age range (18-100)
    assert (df['age'] >= 18).all() and (df['age'] <= 100).all(), \
        "Age values out of range"
    
    # Salary range (positive)
    assert (df['salary'] > 0).all(), "Negative salaries found"
    
    print("✓ Range validation passed")


# ---------------------------------------------------------------------
# Q48: Referential integrity validation
# Concept: Foreign key validation
# ---------------------------------------------------------------------
def test_referential_integrity():
    """Validate foreign key relationships"""
    customers = pd.DataFrame({
        'customer_id': [1, 2, 3]
    })
    
    orders = pd.DataFrame({
        'order_id': [101, 102, 103, 104],
        'customer_id': [1, 1, 2, 99]  # 99 is orphan
    })
    
    # Find orphan records
    orphans = orders[~orders['customer_id'].isin(customers['customer_id'])]
    
    assert len(orphans) == 1, "Orphan detection failed"
    assert orphans.iloc[0]['customer_id'] == 99, "Wrong orphan identified"
    
    print("✓ Referential integrity check passed (1 orphan found as expected)")


# ---------------------------------------------------------------------
# Q49: Date range validation
# Concept: Validate dates within expected range
# ---------------------------------------------------------------------
def test_date_range_validation():
    """Validate dates fall within expected range"""
    df = pd.DataFrame({
        'order_date': pd.to_datetime(['2024-01-15', '2024-02-20', '2024-03-10'])
    })
    
    min_date = pd.to_datetime('2024-01-01')
    max_date = pd.to_datetime('2024-12-31')
    
    # All dates in range
    in_range = (df['order_date'] >= min_date) & (df['order_date'] <= max_date)
    assert in_range.all(), "Dates out of expected range"
    
    print("✓ Date range validation passed")


# ---------------------------------------------------------------------
# Q50: Data distribution testing
# Concept: Statistical distribution validation
# ---------------------------------------------------------------------
from scipy import stats

def test_data_distribution():
    """Validate data follows expected distribution"""
    # Generate normal distribution
    data = np.random.normal(loc=100, scale=15, size=1000)
    
    # Test normality (Shapiro-Wilk test)
    statistic, p_value = stats.shapiro(data)
    
    # p > 0.05 indicates normal distribution
    assert p_value > 0.05, f"Data not normally distributed (p={p_value:.4f})"
    
    # Validate mean and std
    assert abs(data.mean() - 100) < 5, "Mean too far from expected"
    assert abs(data.std() - 15) < 3, "Std deviation too far from expected"
    
    print("✓ Distribution testing passed")


# =====================================================================
# SECTION 3: ADVANCED TESTING PATTERNS (Questions 51-80)
# =====================================================================

# ---------------------------------------------------------------------
# Q51: Fixture pattern for test data
# Concept: Test fixtures, setup/teardown
# ---------------------------------------------------------------------
class TestFixtureExample:
    """Example of fixture pattern"""
    
    @classmethod
    def setup_class(cls):
        """Run once before all tests"""
        cls.test_data = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [100, 200, 300]
        })
        print("\n✓ Fixture setup complete")
    
    @classmethod
    def teardown_class(cls):
        """Run once after all tests"""
        del cls.test_data
        print("✓ Fixture teardown complete")
    
    def test_using_fixture(self):
        """Test using class fixture"""
        assert len(self.test_data) == 3, "Fixture data incorrect"


# ---------------------------------------------------------------------
# Q52: Mock external dependencies
# Concept: unittest.mock
# ---------------------------------------------------------------------
from unittest.mock import Mock, patch

def test_mocking_external_service():
    """Mock external API call"""
    
    def fetch_user_data(user_id):
        # In real code, this would call external API
        # For testing, we'll mock it
        pass
    
    # Mock the function
    with patch(__name__ + '.fetch_user_data') as mock_fetch:
        mock_fetch.return_value = {'id': 123, 'name': 'Alice'}
        
        result = mock_fetch(123)
        assert result['name'] == 'Alice', "Mock failed"
        mock_fetch.assert_called_once_with(123)
    
    print("✓ Mocking validated")


# ---------------------------------------------------------------------
# Q53: Context manager for resource management
# Concept: with statement, __enter__, __exit__
# ---------------------------------------------------------------------
class DatabaseConnection:
    """Example context manager"""
    def __enter__(self):
        print("  Opening connection...")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("  Closing connection...")
        return False
    
    def query(self, sql):
        return f"Results for: {sql}"

def test_context_manager():
    """Test context manager"""
    with DatabaseConnection() as db:
        result = db.query("SELECT * FROM orders")
        assert "SELECT" in result, "Query failed"
    
    print("✓ Context manager validated")


# ---------------------------------------------------------------------
# Q54: Decorator for test timing
# Concept: Function decorators
# ---------------------------------------------------------------------
def timing_decorator(func):
    """Decorator to measure function execution time"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"  Function {func.__name__} took {duration:.4f}s")
        return result
    return wrapper

@timing_decorator
def test_with_timing():
    """Test with automatic timing"""
    time.sleep(0.1)  # Simulate work
    assert True, "Test passed"
    
test_with_timing()
print("✓ Decorator validated")


# ---------------------------------------------------------------------
# Q55: Generator for memory-efficient testing
# Concept: yield, generators
# ---------------------------------------------------------------------
def large_dataset_generator(n):
    """Generate data without loading all into memory"""
    for i in range(n):
        yield {'id': i, 'value': i * 10}

def test_generator():
    """Test using generator for large datasets"""
    gen = large_dataset_generator(1000000)
    
    # Process first 10 items
    first_10 = [next(gen) for _ in range(10)]
    
    assert len(first_10) == 10, "Generator failed"
    assert first_10[5]['value'] == 50, "Generated value incorrect"
    
    print("✓ Generator validated")


# ---------------------------------------------------------------------
# Q56: Property-based testing concept
# Concept: Test properties, not specific examples
# ---------------------------------------------------------------------
def test_property_based():
    """Test invariant properties"""
    
    def sort_function(lst):
        return sorted(lst)
    
    # Property: sorted list length equals original length
    for _ in range(100):
        original = [random.randint(1, 100) for _ in range(10)]
        sorted_list = sort_function(original)
        assert len(sorted_list) == len(original), "Length property violated"
    
    # Property: sorted list is actually sorted
    for _ in range(100):
        original = [random.randint(1, 100) for _ in range(10)]
        sorted_list = sort_function(original)
        assert sorted_list == sorted(sorted_list), "Sorted property violated"
    
    print("✓ Property-based testing validated")


# ---------------------------------------------------------------------
# Q57: State machine testing
# Concept: Test state transitions
# ---------------------------------------------------------------------
class OrderStateMachine:
    """Simple state machine"""
    def __init__(self):
        self.state = 'pending'
    
    def confirm(self):
        if self.state == 'pending':
            self.state = 'confirmed'
        else:
            raise ValueError(f"Cannot confirm from state {self.state}")
    
    def ship(self):
        if self.state == 'confirmed':
            self.state = 'shipped'
        else:
            raise ValueError(f"Cannot ship from state {self.state}")
    
    def deliver(self):
        if self.state == 'shipped':
            self.state = 'delivered'
        else:
            raise ValueError(f"Cannot deliver from state {self.state}")

def test_state_machine():
    """Test state transitions"""
    order = OrderStateMachine()
    
    assert order.state == 'pending', "Initial state incorrect"
    
    order.confirm()
    assert order.state == 'confirmed', "Confirm transition failed"
    
    order.ship()
    assert order.state == 'shipped', "Ship transition failed"
    
    order.deliver()
    assert order.state == 'delivered', "Deliver transition failed"
    
    # Test invalid transition
    order2 = OrderStateMachine()
    try:
        order2.ship()  # Cannot ship from pending
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("✓ State machine validated")


# ---------------------------------------------------------------------
# Q58: Concurrent testing with threading
# Concept: Threading module
# ---------------------------------------------------------------------
import threading

def test_concurrent_access():
    """Test thread-safe operations"""
    counter = 0
    lock = threading.Lock()
    
    def increment():
        nonlocal counter
        for _ in range(1000):
            with lock:
                counter += 1
    
    # Create 10 threads
    threads = [threading.Thread(target=increment) for _ in range(10)]
    
    # Start all threads
    for t in threads:
        t.start()
    
    # Wait for completion
    for t in threads:
        t.join()
    
    # With lock, counter should be exactly 10,000
    assert counter == 10000, f"Thread safety issue: counter={counter}"
    
    print("✓ Concurrent testing validated")


# ---------------------------------------------------------------------
# Q59: Async testing concept
# Concept: asyncio basics
# ---------------------------------------------------------------------
import asyncio

async def async_fetch_data(delay):
    """Simulated async data fetch"""
    await asyncio.sleep(delay)
    return f"Data fetched after {delay}s"

def test_async_operations():
    """Test async functions"""
    
    async def run_async_test():
        result = await async_fetch_data(0.1)
        assert "Data fetched" in result, "Async fetch failed"
    
    # Run async test
    asyncio.run(run_async_test())
    
    print("✓ Async operations validated")


# ---------------------------------------------------------------------
# Q60: Memory profiling
# Concept: tracemalloc module
# ---------------------------------------------------------------------
import tracemalloc

def test_memory_profiling():
    """Profile memory usage"""
    tracemalloc.start()
    
    # Allocate memory
    large_list = [i for i in range(100000)]
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Validate memory usage is reasonable
    assert peak < 10 * 1024 * 1024, f"Peak memory {peak} exceeds 10MB"
    
    print(f"✓ Memory profiling validated (peak: {peak / 1024:.1f} KB)")


# ---------------------------------------------------------------------
# Q61: Custom assertion messages
# Concept: Descriptive assertion failures
# ---------------------------------------------------------------------
def test_custom_assertions():
    """Use descriptive assertion messages"""
    actual_total = 150
    expected_total = 150
    
    assert actual_total == expected_total, \
        f"Revenue mismatch: Expected ${expected_total}, got ${actual_total}. " \
        f"Difference: ${abs(actual_total - expected_total)}"
    
    print("✓ Custom assertions validated")


# ---------------------------------------------------------------------
# Q62: Soft assertions (continue after failure)
# Concept: Collect all failures before raising
# ---------------------------------------------------------------------
class SoftAssert:
    """Collect assertion failures"""
    def __init__(self):
        self.errors = []
    
    def check(self, condition, message):
        if not condition:
            self.errors.append(message)
    
    def assert_all(self):
        if self.errors:
            raise AssertionError("\n".join(self.errors))

def test_soft_assertions():
    """Test with soft assertions"""
    soft = SoftAssert()
    
    soft.check(1 + 1 == 2, "Math broken")
    soft.check(len("hello") == 5, "Length wrong")
    soft.check(True is True, "Boolean broken")
    
    soft.assert_all()
    print("✓ Soft assertions validated")


# ---------------------------------------------------------------------
# Q63: Data-driven testing from CSV
# Concept: Read test cases from file
# ---------------------------------------------------------------------
def test_data_driven():
    """Test with data from CSV"""
    # Create test data CSV
    csv_content = """input,expected_output
2,4
3,9
4,16
5,25"""
    
    with open("test_cases.csv", "w") as f:
        f.write(csv_content)
    
    # Read and execute tests
    test_df = pd.read_csv("test_cases.csv")
    
    for _, row in test_df.iterrows():
        result = row['input'] ** 2
        assert result == row['expected_output'], \
            f"Failed for input {row['input']}: {result} != {row['expected_output']}"
    
    import os
    os.remove("test_cases.csv")
    
    print("✓ Data-driven testing validated")


# ---------------------------------------------------------------------
# Q64: Screenshot comparison for UI testing
# Concept: Image comparison (concept only)
# ---------------------------------------------------------------------
def test_screenshot_comparison_concept():
    """Concept: Compare screenshots"""
    # In real testing, use libraries like:
    # - Pillow for image operations
    # - imagehash for perceptual hashing
    # - pytest-selenium for web screenshots
    
    # Pseudo-code:
    # baseline = Image.open('baseline.png')
    # current = capture_screenshot()
    # diff = ImageChops.difference(baseline, current)
    # assert diff.getbbox() is None, "Screenshots differ"
    
    print("✓ Screenshot comparison concept validated")


# ---------------------------------------------------------------------
# Q65: Test coverage measurement
# Concept: coverage.py (concept)
# ---------------------------------------------------------------------
def test_coverage_concept():
    """Concept: Measure test coverage"""
    # Run tests with coverage:
    # coverage run -m pytest test_file.py
    # coverage report
    # coverage html
    
    # Target: >80% code coverage
    # Focus on critical paths first
    
    print("✓ Coverage concept validated")


# ---------------------------------------------------------------------
# Q66: Mutation testing concept
# Concept: Test the tests
# ---------------------------------------------------------------------
def test_mutation_concept():
    """Concept: Mutation testing validates test quality"""
    # Tools: mutmut, cosmic-ray
    # Introduce bugs (mutations) in code
    # If tests still pass, tests are weak
    
    # Example mutation:
    # Original: if x > 0:
    # Mutated:  if x >= 0:
    # Should fail tests if tests are good
    
    print("✓ Mutation testing concept validated")


# ---------------------------------------------------------------------
# Q67: Contract testing for APIs
# Concept: Consumer-driven contracts
# ---------------------------------------------------------------------
def test_api_contract():
    """Validate API contract"""
    # Expected contract
    expected_contract = {
        "endpoint": "/api/users/{id}",
        "method": "GET",
        "response_schema": {
            "id": "integer",
            "name": "string",
            "email": "string"
        },
        "status_code": 200
    }
    
    # Simulated response
    actual_response = {
        "id": 123,
        "name": "Alice",
        "email": "alice@example.com"
    }
    
    # Validate contract
    for field, expected_type in expected_contract["response_schema"].items():
        assert field in actual_response, f"Missing field: {field}"
        
        actual_type = type(actual_response[field]).__name__
        if expected_type == "integer":
            assert isinstance(actual_response[field], int), \
                f"Field {field} type mismatch"
    
    print("✓ API contract validated")


# ---------------------------------------------------------------------
# Q68: Chaos engineering concept
# Concept: Test system resilience
# ---------------------------------------------------------------------
def test_chaos_engineering_concept():
    """Concept: Introduce failures intentionally"""
    
    def unreliable_service():
        """Simulate unreliable service"""
        if random.random() < 0.3:  # 30% failure rate
            raise Exception("Service unavailable")
        return "Success"
    
    def resilient_caller():
        """Call with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return unreliable_service()
            except Exception:
                if attempt == max_retries - 1:
                    return "Fallback response"
                time.sleep(0.1)
    
    result = resilient_caller()
    assert result in ["Success", "Fallback response"], "Resilience logic broken"
    
    print("✓ Chaos engineering concept validated")


# ---------------------------------------------------------------------
# Q69: A/B test validation
# Concept: Statistical significance testing
# ---------------------------------------------------------------------
def test_ab_test_validation():
    """Validate A/B test results"""
    # Variant A: 100 conversions out of 1000 users
    # Variant B: 120 conversions out of 1000 users
    
    from scipy.stats import chi2_contingency
    
    observed = np.array([
        [100, 900],  # A: conversions, non-conversions
        [120, 880]   # B: conversions, non-conversions
    ])
    
    chi2, p_value, dof, expected = chi2_contingency(observed)
    
    # p < 0.05 indicates significant difference
    if p_value < 0.05:
        print(f"✓ A/B test shows significant difference (p={p_value:.4f})")
    else:
        print(f"✓ A/B test shows no significant difference (p={p_value:.4f})")


# ---------------------------------------------------------------------
# Q70: Load testing concept
# Concept: Simulate high traffic
# ---------------------------------------------------------------------
def test_load_testing_concept():
    """Concept: Load testing"""
    # Tools: locust, JMeter, k6
    
    # Pseudo-code:
    # for user in range(1000):
    #     spawn_thread(lambda: api_call())
    # measure_response_times()
    # assert p95_latency < 500ms
    
    print("✓ Load testing concept validated")


# ---------------------------------------------------------------------
# Q71: Smoke testing suite
# Concept: Quick sanity checks
# ---------------------------------------------------------------------
def test_smoke_suite():
    """Minimal smoke tests"""
    # Critical path checks only
    
    # 1. Database connectivity
    # (simulated)
    db_connected = True
    assert db_connected, "Database not reachable"
    
    # 2. API health check
    api_healthy = True
    assert api_healthy, "API not responding"
    
    # 3. Basic data retrieval
    data_available = True
    assert data_available, "No data available"
    
    print("✓ Smoke tests passed")


# ---------------------------------------------------------------------
# Q72: Regression test suite organization
# Concept: Test categorization
# ---------------------------------------------------------------------
def test_regression_suite_concept():
    """Organize regression tests"""
    # Categories:
    # - Critical: Run on every commit
    # - Standard: Run before release
    # - Extended: Run weekly
    
    # Use markers (pytest):
    # @pytest.mark.critical
    # @pytest.mark.regression
    # @pytest.mark.slow
    
    print("✓ Regression suite concept validated")


# ---------------------------------------------------------------------
# Q73: Test data factory pattern
# Concept: Generate test data programmatically
# ---------------------------------------------------------------------
class CustomerFactory:
    """Factory to generate test customers"""
    @staticmethod
    def create(customer_id=None, name=None, email=None):
        return {
            'customer_id': customer_id or random.randint(1000, 9999),
            'name': name or f"Customer_{random.randint(1, 100)}",
            'email': email or f"test{random.randint(1, 100)}@example.com"
        }

def test_factory_pattern():
    """Test factory pattern"""
    customer = CustomerFactory.create()
    
    assert 'customer_id' in customer, "Missing customer_id"
    assert customer['customer_id'] >= 1000, "Invalid customer_id"
    
    # Create with specific values
    custom_customer = CustomerFactory.create(customer_id=9999, name="Alice")
    assert custom_customer['customer_id'] == 9999, "Custom ID not applied"
    assert custom_customer['name'] == "Alice", "Custom name not applied"
    
    print("✓ Factory pattern validated")


# ---------------------------------------------------------------------
# Q74: Page Object Model concept (for UI testing)
# Concept: Separate page structure from tests
# ---------------------------------------------------------------------
class LoginPage:
    """Page Object for login page"""
    def __init__(self, driver):
        self.driver = driver
        self.username_input = "username_field_id"
        self.password_input = "password_field_id"
        self.submit_button = "submit_button_id"
    
    def login(self, username, password):
        # In real code: self.driver.find_element(...)
        # For concept:
        return username == "valid_user" and password == "valid_pass"

def test_page_object_model():
    """Test using Page Object Model"""
    page = LoginPage(driver=None)  # Simulated
    
    result = page.login("valid_user", "valid_pass")
    assert result is True, "Login failed"
    
    print("✓ Page Object Model concept validated")


# ---------------------------------------------------------------------
# Q75: Test doubles (stubs, mocks, fakes)
# Concept: Different types of test doubles
# ---------------------------------------------------------------------
def test_test_doubles_concept():
    """Understand test double types"""
    
    # Stub: Returns hard-coded values
    class EmailServiceStub:
        def send(self, to, subject, body):
            return True  # Always succeeds
    
    # Mock: Records interactions
    class EmailServiceMock:
        def __init__(self):
            self.calls = []
        def send(self, to, subject, body):
            self.calls.append((to, subject, body))
            return True
    
    # Fake: Working implementation (simpler)
    class EmailServiceFake:
        def __init__(self):
            self.sent_emails = []
        def send(self, to, subject, body):
            self.sent_emails.append({'to': to, 'subject': subject})
            return True
    
    # Test with mock
    mock_email = EmailServiceMock()
    mock_email.send("test@example.com", "Test", "Body")
    
    assert len(mock_email.calls) == 1, "Mock didn't record call"
    assert mock_email.calls[0][0] == "test@example.com", "Wrong recipient"
    
    print("✓ Test doubles concept validated")


# ---------------------------------------------------------------------
# Q76: Test isolation (each test independent)
# Concept: No shared state between tests
# ---------------------------------------------------------------------
def test_isolation_example():
    """Tests should be independent"""
    
    # Bad: Shared state
    # global_counter = 0
    # def test1(): global_counter += 1
    # def test2(): assert global_counter == 0  # Fails if test1 runs first
    
    # Good: Each test has own state
    def test1():
        counter = 0
        counter += 1
        assert counter == 1
    
    def test2():
        counter = 0
        assert counter == 0
    
    test1()
    test2()
    
    print("✓ Test isolation validated")


# ---------------------------------------------------------------------
# Q77: Boundary value testing
# Concept: Test edge cases
# ---------------------------------------------------------------------
def test_boundary_values():
    """Test boundary conditions"""
    
    def validate_age(age):
        return 0 <= age <= 150
    
    # Boundary test cases
    boundaries = [
        (-1, False),   # Just below minimum
        (0, True),     # Minimum valid
        (1, True),     # Just above minimum
        (149, True),   # Just below maximum
        (150, True),   # Maximum valid
        (151, False)   # Just above maximum
    ]
    
    for age, expected in boundaries:
        result = validate_age(age)
        assert result == expected, \
            f"Boundary test failed for age {age}: expected {expected}, got {result}"
    
    print("✓ Boundary value testing validated")


# ---------------------------------------------------------------------
# Q78: Equivalence partitioning
# Concept: Test representative values from each partition
# ---------------------------------------------------------------------
def test_equivalence_partitioning():
    """Test using equivalence partitions"""
    
    def categorize_age(age):
        if age < 18:
            return "minor"
        elif age < 65:
            return "adult"
        else:
            return "senior"
    
    # Partitions: <18, 18-64, >=65
    # Test one value from each partition
    assert categorize_age(10) == "minor", "Minor partition failed"
    assert categorize_age(30) == "adult", "Adult partition failed"
    assert categorize_age(70) == "senior", "Senior partition failed"
    
    print("✓ Equivalence partitioning validated")


# ---------------------------------------------------------------------
# Q79: Decision table testing
# Concept: Test all combinations of conditions
# ---------------------------------------------------------------------
def test_decision_table():
    """Test using decision table"""
    
    def calculate_shipping(order_value, is_member, weight):
        if order_value > 100:
            return 0  # Free shipping
        elif is_member:
            return 5  # Member discount
        elif weight < 5:
            return 10  # Light package
        else:
            return 15  # Standard
    
    # Decision table test cases
    test_cases = [
        # (order_value, is_member, weight, expected_shipping)
        (150, False, 10, 0),   # High value
        (50, True, 10, 5),     # Member
        (50, False, 3, 10),    # Light
        (50, False, 10, 15)    # Standard
    ]
    
    for order_val, member, wt, expected in test_cases:
        result = calculate_shipping(order_val, member, wt)
        assert result == expected, \
            f"Shipping calculation failed: {result} != {expected}"
    
    print("✓ Decision table testing validated")


# ---------------------------------------------------------------------
# Q80: Pairwise testing concept
# Concept: Test all pairs of parameters
# ---------------------------------------------------------------------
def test_pairwise_concept():
    """Concept: Pairwise (all-pairs) testing"""
    # Instead of testing all combinations (exhaustive):
    # Browser × OS × Language = 3 × 3 × 3 = 27 tests
    
    # Pairwise covers all pairs with fewer tests:
    # Tools: pairwise, allpairspy
    
    # Example pairwise set (covers all browser-OS pairs, OS-language pairs, etc.):
    # (Chrome, Windows, English)
    # (Firefox, Mac, Spanish)
    # (Safari, Linux, French)
    # ...
    
    print("✓ Pairwise testing concept validated")


# =====================================================================
# SECTION 4: ML/AI TESTING WITH PYTHON (Questions 81-100)
# =====================================================================

# ---------------------------------------------------------------------
# Q81: Model accuracy testing
# Concept: Validate ML model performance
# ---------------------------------------------------------------------
from sklearn.metrics import accuracy_score, precision_score, recall_score

def test_model_accuracy():
    """Test ML model accuracy"""
    # Simulated predictions
    y_true = [0, 1, 1, 0, 1, 0, 1, 1, 0, 0]
    y_pred = [0, 1, 1, 0, 1, 0, 0, 1, 0, 1]
    
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    
    # Validate metrics meet requirements
    assert accuracy >= 0.70, f"Accuracy {accuracy:.2%} below 70% threshold"
    assert precision >= 0.70, f"Precision {precision:.2%} below threshold"
    assert recall >= 0.70, f"Recall {recall:.2%} below threshold"
    
    print(f"✓ Model metrics validated (Accuracy: {accuracy:.2%})")


# ---------------------------------------------------------------------
# Q82: Confusion matrix validation
# Concept: Validate prediction distribution
# ---------------------------------------------------------------------
from sklearn.metrics import confusion_matrix

def test_confusion_matrix():
    """Validate confusion matrix"""
    y_true = [0, 0, 1, 1, 0, 1, 0, 1]
    y_pred = [0, 0, 1, 0, 0, 1, 1, 1]
    
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    # False positive rate should be low
    fpr = fp / (fp + tn)
    assert fpr < 0.30, f"False positive rate {fpr:.2%} too high"
    
    print(f"✓ Confusion matrix validated (FPR: {fpr:.2%})")


# ---------------------------------------------------------------------
# Q83: ROC AUC validation
# Concept: Validate classification performance
# ---------------------------------------------------------------------
from sklearn.metrics import roc_auc_score

def test_roc_auc():
    """Validate ROC AUC score"""
    y_true = [0, 1, 1, 0, 1, 0, 1, 1, 0, 0]
    y_scores = [0.1, 0.9, 0.8, 0.2, 0.95, 0.3, 0.7, 0.85, 0.15, 0.4]
    
    auc = roc_auc_score(y_true, y_scores)
    
    assert auc >= 0.80, f"AUC {auc:.3f} below 0.80 threshold"
    
    print(f"✓ ROC AUC validated ({auc:.3f})")


# ---------------------------------------------------------------------
# Q84: Model reproducibility testing
# Concept: Same inputs → same outputs
# ---------------------------------------------------------------------
from sklearn.ensemble import RandomForestClassifier

def test_model_reproducibility():
    """Validate model reproducibility"""
    X = [[1, 2], [3, 4], [5, 6], [7, 8]]
    y = [0, 1, 0, 1]
    
    # Train model 1
    model1 = RandomForestClassifier(random_state=42)
    model1.fit(X, y)
    pred1 = model1.predict([[2, 3]])
    
    # Train model 2 (same random state)
    model2 = RandomForestClassifier(random_state=42)
    model2.fit(X, y)
    pred2 = model2.predict([[2, 3]])
    
    assert pred1[0] == pred2[0], "Models not reproducible"
    
    print("✓ Model reproducibility validated")


# ---------------------------------------------------------------------
# Q85: Data leakage detection
# Concept: Ensure no test data in training
# ---------------------------------------------------------------------
def test_data_leakage():
    """Detect data leakage"""
    train_indices = {0, 1, 2, 3, 4}
    test_indices = {5, 6, 7, 8, 9}
    
    # Check for overlap
    overlap = train_indices & test_indices
    
    assert len(overlap) == 0, f"Data leakage detected: {overlap}"
    
    print("✓ No data leakage detected")


# ---------------------------------------------------------------------
# Q86: Feature importance validation
# Concept: Validate important features make sense
# ---------------------------------------------------------------------
def test_feature_importance():
    """Validate feature importance"""
    from sklearn.ensemble import RandomForestClassifier
    
    # Simple dataset where first feature is clearly important
    X = [[1, 100], [2, 200], [3, 150], [4, 180], [5, 220]]
    y = [0, 1, 0, 1, 1]  # Correlated with first feature
    
    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)
    
    importances = model.feature_importances_
    
    # First feature should be more important
    assert importances[0] > importances[1], \
        "Feature importance doesn't match expectation"
    
    print("✓ Feature importance validated")


# ---------------------------------------------------------------------
# Q87: Model bias testing
# Concept: Detect bias in predictions
# ---------------------------------------------------------------------
def test_model_bias():
    """Detect prediction bias"""
    # Simulated predictions by gender
    male_predictions = [1, 1, 0, 1, 1]  # 80% positive
    female_predictions = [0, 0, 1, 0, 0]  # 20% positive
    
    male_positive_rate = sum(male_predictions) / len(male_predictions)
    female_positive_rate = sum(female_predictions) / len(female_predictions)
    
    bias = abs(male_positive_rate - female_positive_rate)
    
    # Allow max 20% difference
    assert bias < 0.20, f"Gender bias {bias:.2%} exceeds threshold"
    
    print(f"✓ Bias testing complete (bias: {bias:.2%})")


# ---------------------------------------------------------------------
# Q88: Model drift detection
# Concept: Detect performance degradation
# ---------------------------------------------------------------------
def test_model_drift():
    """Detect model drift"""
    # Baseline accuracy (from training)
    baseline_accuracy = 0.90
    
    # Current production accuracy
    current_accuracy = 0.85
    
    # Calculate drift
    drift = baseline_accuracy - current_accuracy
    
    # Alert if drift > 5%
    assert drift < 0.05, \
        f"Model drift {drift:.2%} exceeds 5% threshold (retrain needed)"
    
    print(f"✓ Model drift check passed ({drift:.2%})")


# ---------------------------------------------------------------------
# Q89: Prediction latency testing
# Concept: Validate inference speed
# ---------------------------------------------------------------------
def test_prediction_latency():
    """Validate model inference latency"""
    from sklearn.linear_model import LogisticRegression
    
    X = [[i, i*2] for i in range(100)]
    y = [0] * 50 + [1] * 50
    
    model = LogisticRegression()
    model.fit(X, y)
    
    # Measure prediction time
    start = time.time()
    predictions = model.predict(X)
    duration = time.time() - start
    
    # Latency SLA: <10ms for 100 predictions
    assert duration < 0.01, f"Prediction latency {duration*1000:.2f}ms exceeds 10ms SLA"
    
    print(f"✓ Prediction latency validated ({duration*1000:.2f}ms)")


# ---------------------------------------------------------------------
# Q90: Model versioning validation
# Concept: Track model versions
# ---------------------------------------------------------------------
def test_model_versioning():
    """Validate model versioning"""
    import joblib
    
    # Save model with version metadata
    model_metadata = {
        'version': '1.2.0',
        'trained_date': '2024-01-15',
        'accuracy': 0.92,
        'framework': 'sklearn'
    }
    
    # In real code: joblib.dump((model, model_metadata), 'model_v1.2.0.pkl')
    
    # Validate version format
    version = model_metadata['version']
    major, minor, patch = version.split('.')
    
    assert major.isdigit() and minor.isdigit() and patch.isdigit(), \
        "Invalid version format"
    
    print(f"✓ Model version validated ({version})")


# ---------------------------------------------------------------------
# Q91: LLM output validation
# Concept: Test GenAI responses
# ---------------------------------------------------------------------
def test_llm_output_validation():
    """Validate LLM output quality"""
    # Simulated LLM response
    llm_output = "The capital of France is Paris, which is located in the northern part of the country."
    
    # Validate response contains expected information
    assert "Paris" in llm_output, "Expected answer not in output"
    
    # Validate no hallucination markers
    hallucination_phrases = ["I don't know", "I'm not sure", "possibly"]
    for phrase in hallucination_phrases:
        assert phrase not in llm_output, f"Uncertainty detected: {phrase}"
    
    # Validate length (not too short)
    assert len(llm_output) > 20, "Response too short"
    
    print("✓ LLM output validated")


# ---------------------------------------------------------------------
# Q92: Prompt testing
# Concept: Test different prompts for same task
# ---------------------------------------------------------------------
def test_prompt_effectiveness():
    """Test prompt engineering effectiveness"""
    
    def simulate_llm(prompt):
        # Simulated LLM responses
        if "step by step" in prompt:
            return "1. First... 2. Then... 3. Finally..."
        else:
            return "The answer is X"
    
    # Basic prompt
    basic_response = simulate_llm("Solve this problem")
    
    # Improved prompt with chain-of-thought
    cot_response = simulate_llm("Solve this problem step by step")
    
    # CoT should produce more detailed response
    assert len(cot_response) > len(basic_response), \
        "Chain-of-thought prompt not more detailed"
    
    print("✓ Prompt testing validated")


# ---------------------------------------------------------------------
# Q93: Embedding similarity testing
# Concept: Validate semantic similarity
# ---------------------------------------------------------------------
def test_embedding_similarity():
    """Test text embedding similarity"""
    from sklearn.metrics.pairwise import cosine_similarity
    
    # Simulated embeddings (in real code, use sentence-transformers)
    embedding1 = np.array([[0.1, 0.2, 0.3, 0.4]])
    embedding2 = np.array([[0.11, 0.21, 0.29, 0.41]])  # Very similar
    embedding3 = np.array([[0.9, 0.8, 0.7, 0.6]])  # Different
    
    # Calculate similarity
    sim_1_2 = cosine_similarity(embedding1, embedding2)[0][0]
    sim_1_3 = cosine_similarity(embedding1, embedding3)[0][0]
    
    # Similar texts should have high similarity
    assert sim_1_2 > 0.95, f"Similar texts not similar enough: {sim_1_2:.3f}"
    
    # Different texts should have low similarity
    assert sim_1_3 < 0.50, f"Different texts too similar: {sim_1_3:.3f}"
    
    print(f"✓ Embedding similarity validated (similar: {sim_1_2:.3f}, different: {sim_1_3:.3f})")


# ---------------------------------------------------------------------
# Q94: RAG system testing
# Concept: Test retrieval + generation
# ---------------------------------------------------------------------
def test_rag_system():
    """Test RAG (Retrieval-Augmented Generation)"""
    
    # Simulated document store
    documents = [
        "Paris is the capital of France",
        "Berlin is the capital of Germany",
        "London is the capital of United Kingdom"
    ]
    
    # Simulated retrieval
    query = "capital of France"
    retrieved_doc = "Paris is the capital of France"
    
    # Validate correct document retrieved
    assert retrieved_doc in documents, "Retrieved doc not in knowledge base"
    assert "France" in retrieved_doc, "Retrieved doc doesn't match query"
    
    # Simulated generation
    llm_answer = f"Based on the document: {retrieved_doc}, the answer is Paris."
    
    # Validate answer grounded in retrieved doc
    assert "Paris" in llm_answer, "Answer not in generated response"
    assert retrieved_doc in llm_answer, "Generated answer not grounded in document"
    
    print("✓ RAG system validated")


# ---------------------------------------------------------------------
# Q95: Toxicity detection
# Concept: Validate content safety
# ---------------------------------------------------------------------
def test_toxicity_detection():
    """Detect toxic content"""
    
    def is_toxic(text):
        # Simulated toxicity detector
        toxic_words = ['hate', 'offensive', 'violent']
        return any(word in text.lower() for word in toxic_words)
    
    safe_text = "This is a helpful and friendly message"
    toxic_text = "This is a hateful message"
    
    assert not is_toxic(safe_text), "False positive: safe text flagged as toxic"
    assert is_toxic(toxic_text), "False negative: toxic text not detected"
    
    print("✓ Toxicity detection validated")


# ---------------------------------------------------------------------
# Q96: Model A/B testing
# Concept: Compare two model versions
# ---------------------------------------------------------------------
def test_model_ab_comparison():
    """A/B test two model versions"""
    # Model A metrics
    model_a_accuracy = 0.85
    model_a_latency = 50  # ms
    
    # Model B metrics
    model_b_accuracy = 0.88
    model_b_latency = 80  # ms
    
    # Model B is more accurate but slower
    accuracy_improvement = model_b_accuracy - model_a_accuracy
    latency_increase = model_b_latency - model_a_latency
    
    # Decision: Accept B if accuracy gain > 2% and latency increase < 100ms
    if accuracy_improvement > 0.02 and latency_increase < 100:
        chosen_model = "B"
    else:
        chosen_model = "A"
    
    assert chosen_model == "B", "Model selection logic incorrect"
    
    print(f"✓ Model A/B testing validated (chosen: Model {chosen_model})")


# ---------------------------------------------------------------------
# Q97: Batch prediction validation
# Concept: Test bulk inference
# ---------------------------------------------------------------------
def test_batch_prediction():
    """Validate batch predictions"""
    from sklearn.linear_model import LogisticRegression
    
    # Train model
    X_train = [[i, i*2] for i in range(100)]
    y_train = [0] * 50 + [1] * 50
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    # Batch prediction
    X_batch = [[i, i*2] for i in range(1000)]
    predictions = model.predict(X_batch)
    
    # Validate batch size
    assert len(predictions) == 1000, "Batch prediction count mismatch"
    
    # Validate prediction distribution (should be roughly balanced)
    positive_rate = sum(predictions) / len(predictions)
    assert 0.3 < positive_rate < 0.7, "Prediction distribution skewed"
    
    print(f"✓ Batch prediction validated ({len(predictions)} predictions)")


# ---------------------------------------------------------------------
# Q98: Pipeline testing
# Concept: Test end-to-end ML pipeline
# ---------------------------------------------------------------------
def test_ml_pipeline():
    """Test complete ML pipeline"""
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    
    # Create pipeline
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression())
    ])
    
    # Train
    X_train = [[1, 2], [3, 4], [5, 6], [7, 8]]
    y_train = [0, 1, 0, 1]
    pipeline.fit(X_train, y_train)
    
    # Predict
    X_test = [[2, 3]]
    prediction = pipeline.predict(X_test)
    
    # Validate pipeline components
    assert len(pipeline.steps) == 2, "Pipeline missing steps"
    assert 'scaler' in dict(pipeline.steps), "Scaler not in pipeline"
    assert 'classifier' in dict(pipeline.steps), "Classifier not in pipeline"
    
    print("✓ ML pipeline validated")


# ---------------------------------------------------------------------
# Q99: Cross-validation testing
# Concept: Validate model with k-fold CV
# ---------------------------------------------------------------------
from sklearn.model_selection import cross_val_score

def test_cross_validation():
    """Test model with cross-validation"""
    from sklearn.linear_model import LogisticRegression
    
    X = [[i, i*2] for i in range(100)]
    y = [0] * 50 + [1] * 50
    
    model = LogisticRegression()
    
    # 5-fold cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5)
    
    # Validate CV scores
    assert len(cv_scores) == 5, "Wrong number of CV folds"
    assert cv_scores.mean() > 0.80, f"CV accuracy {cv_scores.mean():.2%} too low"
    assert cv_scores.std() < 0.10, f"CV scores too variable (std: {cv_scores.std():.3f})"
    
    print(f"✓ Cross-validation validated (mean: {cv_scores.mean():.2%}, std: {cv_scores.std():.3f})")


# ---------------------------------------------------------------------
# Q100: Model explainability testing
# Concept: Validate model interpretability
# ---------------------------------------------------------------------
def test_model_explainability():
    """Test model explainability"""
    from sklearn.tree import DecisionTreeClassifier
    
    X = [[1, 2], [3, 4], [5, 6], [7, 8]]
    y = [0, 1, 0, 1]
    
    model = DecisionTreeClassifier(max_depth=2, random_state=42)
    model.fit(X, y)
    
    # Get feature importances
    importances = model.feature_importances_
    
    # Validate importances sum to 1
    assert abs(importances.sum() - 1.0) < 0.01, "Importances don't sum to 1"
    
    # Validate all importances non-negative
    assert all(imp >= 0 for imp in importances), "Negative importance detected"
    
    print(f"✓ Model explainability validated (importances: {importances})")


# =====================================================================
# BONUS SECTION: UTILITY FUNCTIONS (Questions 101-120)
# =====================================================================

# ---------------------------------------------------------------------
# Q101-120: Utility functions for QA automation
# ---------------------------------------------------------------------

def wait_for_condition(condition_func, timeout=10, poll_interval=0.5):
    """Wait for condition to become true"""
    start = time.time()
    while time.time() - start < timeout:
        if condition_func():
            return True
        time.sleep(poll_interval)
    return False

def retry_on_exception(func, max_attempts=3, exceptions=(Exception,)):
    """Retry function on exception"""
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(1)

def assert_dataframes_equal(df1, df2, check_dtype=True):
    """Compare two DataFrames"""
    pd.testing.assert_frame_equal(df1, df2, check_dtype=check_dtype)

def generate_test_data(n_rows, columns):
    """Generate random test data"""
    data = {}
    for col_name, col_type in columns.items():
        if col_type == 'int':
            data[col_name] = [random.randint(1, 100) for _ in range(n_rows)]
        elif col_type == 'str':
            data[col_name] = [f"value_{i}" for i in range(n_rows)]
        elif col_type == 'float':
            data[col_name] = [random.random() * 100 for _ in range(n_rows)]
    return pd.DataFrame(data)

def log_test_result(test_name, status, duration=None):
    """Log test execution results"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] {test_name}: {status}"
    if duration:
        message += f" (Duration: {duration:.3f}s)"
    print(message)

# Example usage of utilities
def test_utility_functions():
    """Test utility functions"""
    
    # Wait for condition
    counter = 0
    def increment_until_5():
        nonlocal counter
        counter += 1
        return counter >= 5
    
    result = wait_for_condition(increment_until_5, timeout=5, poll_interval=0.1)
    assert result is True, "Wait for condition failed"
    
    # Generate test data
    df = generate_test_data(10, {'id': 'int', 'name': 'str', 'value': 'float'})
    assert len(df) == 10, "Test data generation failed"
    assert 'id' in df.columns, "Missing column in generated data"
    
    print("✓ Utility functions validated")


# =====================================================================
# MAIN EXECUTION
# =====================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PYTHON QA TESTING - 120 INTERVIEW QUESTIONS")
    print("=" * 70)
    
    # Run all tests
    test_functions = [
        # Section 1: Fundamentals (1-20)
        test_data_types, test_list_operations, test_dictionary_validation,
        test_string_cleaning, test_date_operations, test_file_reading,
        test_exception_handling, test_functional_patterns, test_set_operations,
        test_tuple_unpacking, test_enumerate_usage, test_zip_usage,
        test_defaultdict_counting, test_counter_usage, test_namedtuple,
        test_lambda_functions, test_any_all, test_regex_validation,
        test_json_operations, test_path_operations,
        
        # Section 2: Data Testing (21-50)
        test_csv_validation, test_pandas_basics, test_pandas_filtering,
        test_pandas_aggregations, test_pandas_null_handling, test_pandas_merge,
        test_pandas_data_validation, test_pandas_datetime, test_pandas_iteration,
        test_pandas_pivot, test_numpy_operations, test_database_connection,
        test_api_response_structure, test_data_reconciliation,
        test_performance_timing, test_memory_usage, test_fuzzy_matching,
        test_checksum_validation, test_retry_logic, test_parameterized,
        test_data_sampling, test_outlier_detection, test_type_coercion,
        test_deduplication, test_schema_validation, test_row_count_validation,
        test_range_validation, test_referential_integrity,
        test_date_range_validation, test_data_distribution,
        
        # Section 3: Advanced Patterns (51-80)
        # (Some require class instantiation, skipped in simple run)
        test_context_manager, test_generator, test_property_based,
        test_state_machine, test_concurrent_access, test_async_operations,
        test_memory_profiling, test_custom_assertions, test_soft_assertions,
        test_data_driven, test_coverage_concept, test_mutation_concept,
        test_api_contract, test_chaos_engineering_concept,
        test_ab_test_validation, test_load_testing_concept, test_smoke_suite,
        test_regression_suite_concept, test_factory_pattern,
        test_page_object_model, test_test_doubles_concept,
        test_isolation_example, test_boundary_values,
        test_equivalence_partitioning, test_decision_table,
        test_pairwise_concept,
        
        # Section 4: ML/AI Testing (81-100)
        test_model_accuracy, test_confusion_matrix, test_roc_auc,
        test_model_reproducibility, test_data_leakage,
        test_feature_importance, test_model_bias, test_model_drift,
        test_prediction_latency, test_model_versioning,
        test_llm_output_validation, test_prompt_effectiveness,
        test_embedding_similarity, test_rag_system, test_toxicity_detection,
        test_model_ab_comparison, test_batch_prediction, test_ml_pipeline,
        test_cross_validation, test_model_explainability,
        
        # Utilities
        test_utility_functions
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 70)

"""
=====================================================================
END OF FILE: 91_Python_Master_Concepts_Interview_QA_Solutions.py
Total Questions: 120+
Coverage: Python Fundamentals → Data Testing → ML/AI QA
=====================================================================

RECOMMENDED NEXT STEPS FOR QA ENGINEERS:
1. Practice each section independently
2. Modify tests for your actual data/models
3. Build reusable test utilities library
4. Integrate with pytest framework
5. Add to CI/CD pipeline
6. Create custom test fixtures
7. Build data quality test suite

KEY PYTHON LIBRARIES FOR QA:
- pytest: Test framework
- pandas: Data manipulation
- numpy: Numerical operations
- requests: API testing
- selenium: UI testing
- scikit-learn: ML testing
- unittest.mock: Mocking dependencies

INTERVIEW PREPARATION:
- Understand pandas DataFrame operations (70% of data QA)
- Master pytest fixtures and parametrization
- Know ML metrics (accuracy, precision, recall, AUC)
- Practice API testing patterns
- Learn async testing for modern applications
"""