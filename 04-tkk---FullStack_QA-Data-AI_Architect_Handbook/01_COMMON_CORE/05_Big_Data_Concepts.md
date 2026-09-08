# Big Data Concepts

## Executive Summary

Big Data systems process massive volumes, high-velocity streams, and diverse varieties of data at scale. From a **QA perspective**, testing big data platforms requires understanding distributed computing, streaming architectures, eventual consistency, fault tolerance, and performance at petabyte scale.

**Target Audience**: Senior QA engineers (7+ years) testing big data platforms (Hadoop, Spark, Kafka, cloud data lakes).

---

## Why This Matters in Enterprise

### Business Impact
- **Big data analytics generates $189B annually** (IDC 2025)
- **Real-time processing enables**: Fraud detection ($5M saved/year), personalized recommendations (+15% revenue), predictive maintenance (-30% downtime)
- **Competitive advantage**: 53% of enterprises cite big data as critical to strategy (Forbes)

### Technical Imperative
- **Data volume explosion**: 90% of world's data created in last 2 years
- **Streaming requirements**: IoT, clickstream, financial transactions demand sub-second latency
- **Distributed complexity**: Testing across clusters (10-1000 nodes) introduces new failure modes

### Career Value
- **High-demand skillset**: 64% of organizations struggle to hire big data QA talent (Dice 2025)
- **Salary premium**: Big data QA engineers earn 25-35% more than traditional QA
- **Future-proof**: Skills transfer to cloud, AI/ML, real-time analytics domains

---

## Scope and Boundaries

### In Scope
- Big data characteristics (Volume, Velocity, Variety, Veracity)
- Distributed computing concepts (MapReduce, Spark, parallel processing)
- Streaming architectures (Kafka, event processing, windowing)
- Data lake patterns (raw, curated, analytical zones)
- NoSQL databases (key-value, document, column-family, graph)
- Big data testing strategies (sampling, data generation, performance at scale)

### Out of Scope
- Platform-specific implementations (Databricks, EMR covered in stack files)
- ML/AI on big data (covered in [07_ML_Concepts_QA_Perspective.md](./07_ML_Concepts_QA_Perspective.md))
- Cloud-specific services (covered in Azure/AWS/GCP stack files)

---

## Big Data Characteristics (4 V's + 2)

### 1. Volume (Scale)
**Definition**: Data size exceeds traditional database capacity (terabytes to petabytes).

**Examples**:
- **Walmart**: 2.5 petabytes of customer transaction data
- **Facebook**: 300 petabytes of photos
- **Netflix**: 1 petabyte of user viewing data

**QA Implications**:
- Cannot test with full production data (too expensive)
- Sample-based testing (statistically significant samples)
- Performance testing at scale (distributed load generation)

**Test Strategy**:
    ```python
    # Generate 1TB test dataset (synthetic)
    import pandas as pd
    from faker import Faker
    
    fake = Faker()
    
    def generate_clickstream_batch(batch_size=1_000_000):
        return pd.DataFrame({
            'user_id': [fake.uuid4() for _ in range(batch_size)],
            'timestamp': [fake.date_time_this_year() for _ in range(batch_size)],
            'page_url': [fake.url() for _ in range(batch_size)],
            'session_id': [fake.uuid4() for _ in range(batch_size // 10)] * 10,
            'device': [fake.random_element(['mobile', 'desktop', 'tablet']) for _ in range(batch_size)]
        })
    
    # Generate 1,000 batches = 1B records ≈ 100GB compressed
    for i in range(1000):
        batch = generate_clickstream_batch()
        batch.to_parquet(f's3://test-data/clickstream/batch_{i}.parquet')
    ```

### 2. Velocity (Speed)
**Definition**: Data arrives at high speed, requiring real-time or near-real-time processing.

**Examples**:
- **Twitter**: 6,000 tweets/second (peak: 143,000/sec)
- **Stock exchanges**: Millions of trades/second
- **IoT sensors**: Billions of events/day

**QA Implications**:
- Latency testing (end-to-end event processing time)
- Throughput testing (events processed/second)
- Backpressure handling (system overload scenarios)

**Test Strategy**:
    ```python
    # Kafka load testing (simulate 100K events/sec)
    from kafka import KafkaProducer
    import json
    import time
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    def generate_event():
        return {
            'event_id': fake.uuid4(),
            'timestamp': time.time(),
            'user_id': fake.random_int(1, 1000000),
            'action': fake.random_element(['click', 'view', 'purchase'])
        }
    
    # Send 100K events/sec for 60 seconds
    start = time.time()
    for _ in range(6_000_000):  # 100K * 60
        producer.send('test-topic', generate_event())
        if _ % 100000 == 0:
            print(f"Sent {_} events, elapsed: {time.time() - start:.2f}s")
    ```

### 3. Variety (Diversity)
**Definition**: Data comes in multiple formats (structured, semi-structured, unstructured).

**Examples**:
- **Structured**: Relational tables (CSV, Parquet)
- **Semi-structured**: JSON, XML, Avro
- **Unstructured**: Text, images, video, audio

**QA Implications**:
- Schema evolution testing (backwards/forwards compatibility)
- Multi-format validation (CSV vs. JSON vs. Parquet)
- Data type mapping (JSON string → SQL timestamp)

**Test Strategy**:
    ```python
    # Validate schema evolution (Avro example)
    from avro.schema import parse
    import avro.io
    
    schema_v1 = parse('''
    {
      "type": "record",
      "name": "User",
      "fields": [
        {"name": "user_id", "type": "string"},
        {"name": "email", "type": "string"}
      ]
    }
    ''')
    
    schema_v2 = parse('''
    {
      "type": "record",
      "name": "User",
      "fields": [
        {"name": "user_id", "type": "string"},
        {"name": "email", "type": "string"},
        {"name": "phone", "type": ["null", "string"], "default": null}  // New optional field
      ]
    }
    ''')
    
    # Test: v1 data can be read with v2 schema (backward compatible)
    # Test: v2 data can be read with v1 schema (forward compatible - ignores phone)
    ```

### 4. Veracity (Quality)
**Definition**: Data trustworthiness varies (noise, outliers, missing values).

**QA Implications**:
- Data quality validation at ingestion (reject/quarantine bad data)
- Outlier detection (statistical anomalies)
- Missing value handling (imputation vs. exclusion)

**Test Strategy**:
    ```sql
    -- Detect outliers in streaming data (Spark SQL)
    WITH stats AS (
        SELECT 
            AVG(transaction_amount) AS mean,
            STDDEV(transaction_amount) AS stddev
        FROM transactions
        WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL 1 HOUR
    )
    SELECT t.transaction_id, t.transaction_amount
    FROM transactions t, stats s
    WHERE t.transaction_amount > s.mean + 3 * s.stddev  -- 3 sigma outliers
       OR t.transaction_amount < s.mean - 3 * s.stddev;
    ```

### 5. Value (Business Outcome)
**Definition**: Ability to extract actionable insights from data.

**QA Focus**: Validate analytics produce correct business metrics (revenue, churn rate, conversion).

### 6. Variability (Inconsistency)
**Definition**: Data meaning changes over time (schema drift, semantic shifts).

**QA Focus**: Monitor schema changes, validate backward compatibility.

---

## Distributed Computing Concepts

### MapReduce Paradigm

    ```mermaid
    graph LR
        A[Input Data] --> B[Map: Process Each Record]
        B --> C[Shuffle: Group by Key]
        C --> D[Reduce: Aggregate Groups]
        D --> E[Output]
        
        style B fill:#e1f5ff
        style D fill:#ffe1f5
    ```

**Example (Word Count)**:
    ```python
    # Map phase: Emit (word, 1) for each word
    def map_function(line):
        for word in line.split():
            emit(word, 1)
    
    # Reduce phase: Sum counts for each word
    def reduce_function(word, counts):
        emit(word, sum(counts))
    
    # Input:  ["hello world", "hello spark"]
    # Map:    [("hello", 1), ("world", 1), ("hello", 1), ("spark", 1)]
    # Shuffle: [("hello", [1, 1]), ("world", [1]), ("spark", [1])]
    # Reduce: [("hello", 2), ("world", 1), ("spark", 1)]
    ```

**QA Tests**:
    ```python
    # Unit test for map function
    def test_map():
        result = list(map_function("hello world"))
        assert result == [("hello", 1), ("world", 1)]
    
    # Integration test for MapReduce job
    def test_word_count_job():
        input_data = ["hello world", "hello spark"]
        expected = [("hello", 2), ("world", 1), ("spark", 1)]
        
        result = run_mapreduce_job(input_data, map_function, reduce_function)
        assert sorted(result) == sorted(expected)
    ```

### Apache Spark (In-Memory Processing)

**Advantages over MapReduce**:
- 100x faster (in-memory vs. disk I/O)
- DAG optimization (combines multiple stages)
- Rich APIs (SQL, ML, Streaming, Graph)

**QA Focus**:
    ```python
    # Spark job testing (PySpark example)
    from pyspark.sql import SparkSession
    
    def test_sales_aggregation():
        spark = SparkSession.builder.master("local[*]").getOrCreate()
        
        # Create test data
        test_data = [
            ("2024-09-08", "ProductA", 100),
            ("2024-09-08", "ProductB", 200),
            ("2024-09-08", "ProductA", 150)
        ]
        df = spark.createDataFrame(test_data, ["date", "product", "amount"])
        
        # Run aggregation
        result = df.groupBy("date", "product").sum("amount")
        
        # Validate
        assert result.filter("product = 'ProductA'").collect()[0]['sum(amount)'] == 250
        assert result.filter("product = 'ProductB'").collect()[0]['sum(amount)'] == 200
    ```

### Partitioning and Parallelism

**Concept**: Split data into partitions, process in parallel across cluster nodes.

    ```python
    # Spark partitioning
    df = spark.read.parquet("s3://data/transactions")  # 1TB data
    df = df.repartition(1000)  # Split into 1000 partitions (1GB each)
    
    # Each partition processed on separate executor
    result = df.groupBy("customer_id").sum("amount")  # Parallel aggregation
    ```

**QA Tests**:
    ```python
    # Validate partition count
    assert df.rdd.getNumPartitions() == 1000
    
    # Validate data distribution (no skew)
    partition_sizes = df.rdd.mapPartitions(lambda it: [sum(1 for _ in it)]).collect()
    avg_size = sum(partition_sizes) / len(partition_sizes)
    
    # Check no partition is >2x average (indicates skew)
    for size in partition_sizes:
        assert size < 2 * avg_size, f"Partition skew detected: {size} vs avg {avg_size}"
    ```

---

## Streaming Architectures

### Event Streaming (Kafka)

    ```mermaid
    graph LR
        A[Producers] -->|Publish| B[Kafka Broker]
        B -->|Partition 0| C[Consumer Group 1]
        B -->|Partition 1| C
        B -->|Partition 2| C
        C --> D[Processing App]
        
        style B fill:#ffe1f5
        style C fill:#e1f5ff
    ```

**Key Concepts**:
- **Topic**: Logical data stream (e.g., "user-clicks", "transactions")
- **Partition**: Physical segment for parallelism (ordered within partition)
- **Consumer Group**: Multiple consumers share load (each partition to one consumer)

**QA Tests**:
    ```python
    # Test: Events maintain order within partition
    from kafka import KafkaConsumer
    
    consumer = KafkaConsumer(
        'test-topic',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest'
    )
    
    events = []
    for msg in consumer:
        events.append(msg.value)
        if len(events) >= 100:
            break
    
    # Validate timestamps are ascending within partition
    for i in range(1, len(events)):
        assert events[i]['timestamp'] >= events[i-1]['timestamp'], "Order violation"
    ```

### Stream Processing (Spark Structured Streaming)

**Windowing Operations**:
    ```python
    # Tumbling window (5-minute non-overlapping)
    from pyspark.sql.functions import window
    
    stream = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "clickstream") \
        .load()
    
    # Count clicks per 5-minute window
    windowed = stream.groupBy(
        window("timestamp", "5 minutes"),
        "page_url"
    ).count()
    
    # Write to console for testing
    query = windowed.writeStream.outputMode("complete").format("console").start()
    ```

**QA Tests**:
    ```python
    # Test: Late-arriving events handled correctly
    def test_late_events():
        # Send events out of order
        send_event(timestamp="2024-09-08 10:00:00")  # On time
        send_event(timestamp="2024-09-08 10:04:00")  # On time
        send_event(timestamp="2024-09-08 10:01:00")  # Late (1 min old)
        
        # Validate all 3 events counted in 10:00-10:05 window
        result = get_window_count("2024-09-08 10:00:00")
        assert result == 3
    ```

### Exactly-Once Semantics

**Challenge**: Distributed systems risk duplicates (network retries) or data loss (node failures).

**Solutions**:
- **Idempotent writes**: Same event written multiple times produces same result
- **Transactional writes**: Atomic commit across multiple partitions
- **Deduplication**: Track processed event IDs

**QA Tests**:
    ```python
    # Test: Duplicate events handled idempotently
    def test_idempotency():
        event_id = "evt_12345"
        
        # Send same event twice
        process_event({"event_id": event_id, "amount": 100})
        process_event({"event_id": event_id, "amount": 100})
        
        # Validate amount counted only once
        result = get_total_amount()
        assert result == 100, f"Expected 100, got {result} (duplicate counted)"
    ```

---

## Data Lake Patterns

### Zone Architecture

    ```mermaid
    graph LR
        A[Sources] -->|Ingest| B[Raw Zone]
        B -->|Cleanse| C[Curated Zone]
        C -->|Model| D[Analytical Zone]
        D --> E[BI/ML Consumption]
        
        style B fill:#ffe1e1
        style C fill:#fff4e1
        style D fill:#e1f5ff
    ```

**Raw Zone (Bronze)**:
- Exact copy of source data (immutable)
- Formats: Avro, JSON, Parquet
- Schema: Schema-on-read (flexible)
- Retention: Long-term (years)

**Curated Zone (Silver)**:
- Cleansed, validated, deduplicated
- Formats: Parquet (columnar, compressed)
- Schema: Enforced (data quality rules)
- Retention: Medium-term (months)

**Analytical Zone (Gold)**:
- Business-level aggregates (star schema)
- Formats: Delta Lake, Iceberg (ACID transactions)
- Schema: Dimensional model
- Retention: Based on business needs

**QA Tests**:
    ```python
    # Validate data lineage across zones
    def test_data_lineage():
        # Raw zone: 1M records
        raw_count = spark.read.parquet("s3://lake/raw/transactions").count()
        assert raw_count == 1_000_000
        
        # Curated zone: 950K (50K duplicates removed)
        curated_count = spark.read.parquet("s3://lake/curated/transactions").count()
        assert curated_count == 950_000
        
        # Analytical zone: Aggregated to 10K daily summaries
        analytical_count = spark.read.parquet("s3://lake/analytical/daily_sales").count()
        assert analytical_count == 10_000
    ```

### Delta Lake (ACID on Data Lakes)

**Features**:
- ACID transactions (atomicity, consistency, isolation, durability)
- Schema evolution (add/modify columns)
- Time travel (query historical versions)
- Upserts and deletes (MERGE operations)

**QA Tests**:
    ```python
    # Test: ACID transaction (all-or-nothing)
    from delta.tables import DeltaTable
    
    def test_transaction_atomicity():
        delta_table = DeltaTable.forPath(spark, "s3://lake/customers")
        
        # Start transaction: Update 1M records
        try:
            delta_table.update(
                condition="customer_type = 'PREMIUM'",
                set={"discount_rate": "0.20"}
            )
            raise Exception("Simulated failure")  # Force rollback
        except:
            pass
        
        # Validate: No partial updates (transaction rolled back)
        df = spark.read.format("delta").load("s3://lake/customers")
        premium_discounts = df.filter("customer_type = 'PREMIUM'").select("discount_rate").distinct().collect()
        
        assert len(premium_discounts) == 1, "Partial update detected (ACID violated)"
        assert premium_discounts[0]['discount_rate'] != 0.20, "Transaction should have rolled back"
    ```

---

## NoSQL Databases

### Key-Value Stores (Redis, DynamoDB)

**Use Case**: Session storage, caching, real-time leaderboards

**QA Tests**:
    ```python
    # Test: TTL (time-to-live) expiration
    import redis
    import time
    
    r = redis.Redis(host='localhost', port=6379)
    
    def test_ttl():
        r.setex('session_12345', 60, 'user_data')  # Expire in 60 seconds
        
        assert r.get('session_12345') == b'user_data'  # Exists immediately
        
        time.sleep(61)
        
        assert r.get('session_12345') is None  # Expired after 60s
    ```

### Document Stores (MongoDB, Cosmos DB)

**Use Case**: Content management, user profiles, catalogs

**QA Tests**:
    ```python
    # Test: Nested document query
    from pymongo import MongoClient
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client['test_db']
    
    def test_nested_query():
        # Insert document with nested array
        db.orders.insert_one({
            "order_id": "O001",
            "customer_id": "C123",
            "items": [
                {"product_id": "P1", "quantity": 2, "price": 10.00},
                {"product_id": "P2", "quantity": 1, "price": 25.00}
            ]
        })
        
        # Query: Find orders with product P1
        result = db.orders.find_one({"items.product_id": "P1"})
        
        assert result is not None
        assert result['order_id'] == "O001"
    ```

### Column-Family Stores (Cassandra, HBase)

**Use Case**: Time-series data, IoT sensor data, write-heavy workloads

**QA Tests**:
    ```python
    # Test: Write throughput (Cassandra)
    from cassandra.cluster import Cluster
    
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect('test_keyspace')
    
    def test_write_throughput():
        import time
        
        start = time.time()
        
        # Insert 100K records
        for i in range(100_000):
            session.execute(
                "INSERT INTO sensor_data (sensor_id, timestamp, value) VALUES (%s, %s, %s)",
                (f"sensor_{i % 1000}", time.time(), random.random())
            )
        
        duration = time.time() - start
        throughput = 100_000 / duration
        
        assert throughput > 10_000, f"Throughput {throughput:.0f} writes/sec below target 10K"
    ```

### Graph Databases (Neo4j, Neptune)

**Use Case**: Social networks, fraud detection, recommendation engines

**QA Tests**:
    ```cypher
    -- Test: Shortest path between users (Neo4j Cypher)
    MATCH (u1:User {user_id: 'U001'}),
          (u2:User {user_id: 'U999'}),
          path = shortestPath((u1)-[:FOLLOWS*]-(u2))
    RETURN length(path) AS degrees_of_separation;
    
    -- Validate: Path length <= 6 (six degrees of separation)
    ```

---

## Big Data Testing Strategies

### Sampling Techniques

**Simple Random Sampling**:
    ```python
    # Sample 1% of 1TB dataset
    df = spark.read.parquet("s3://data/transactions")
    sample = df.sample(fraction=0.01, seed=42)  # 10GB sample
    ```

**Stratified Sampling** (maintain distribution):
    ```python
    # Sample 1% from each region (preserve regional distribution)
    sample = df.sampleBy("region", fractions={
        "US": 0.01,
        "EU": 0.01,
        "APAC": 0.01
    }, seed=42)
    ```

**Reservoir Sampling** (streaming):
    ```python
    # Maintain fixed-size sample from infinite stream
    def reservoir_sample(stream, k=1000):
        reservoir = []
        for i, item in enumerate(stream):
            if i < k:
                reservoir.append(item)
            else:
                j = random.randint(0, i)
                if j < k:
                    reservoir[j] = item
        return reservoir
    ```

### Data Generation at Scale

**Synthetic Data**:
    ```python
    # Generate 1TB clickstream data
    from pyspark.sql.functions import udf, explode, array, lit
    from pyspark.sql.types import StringType
    
    @udf(returnType=StringType())
    def random_url():
        return fake.url()
    
    # Generate 10B rows (parallelized)
    df = spark.range(10_000_000_000) \
        .withColumn("user_id", (col("id") % 1_000_000).cast("string")) \
        .withColumn("timestamp", current_timestamp()) \
        .withColumn("url", random_url()) \
        .withColumn("session_id", (col("id") % 100_000_000).cast("string"))
    
    df.write.partitionBy("date").parquet("s3://test-data/clickstream")
    ```

### Performance Testing at Scale

**Benchmarking**:
    ```python
    # TPC-DS benchmark (industry standard for analytics)
    from pyspark.sql import SparkSession
    
    spark = SparkSession.builder \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.executor.instances", "100") \
        .config("spark.executor.memory", "16g") \
        .getOrCreate()
    
    # Run query 1 from TPC-DS (complex aggregation)
    start = time.time()
    result = spark.sql("""
        SELECT c_customer_id, SUM(ss_net_paid) AS total_spent
        FROM store_sales
        JOIN customer ON ss_customer_sk = c_customer_sk
        WHERE ss_sold_date_sk BETWEEN 2451545 AND 2451910  -- 1 year
        GROUP BY c_customer_id
        ORDER BY total_spent DESC
        LIMIT 100
    """)
    result.show()
    duration = time.time() - start
    
    print(f"Query duration: {duration:.2f}s")
    assert duration < 60, "Query exceeded 60-second SLA"
    ```

---

## Interview Questions

### Basic (0-3 years)
**Q1**: What are the 4 V's of big data?  
**A1**: Volume (scale), Velocity (speed), Variety (formats), Veracity (quality). Some add Value (business outcome) and Variability (inconsistency).

**Q2**: Difference between batch and stream processing?  
**A2**: Batch processes data in scheduled chunks (hourly, daily). Stream processes data continuously in real-time (sub-second latency). Batch = simpler, cheaper. Stream = complex, low-latency.

### Advanced (4-8 years)
**Q3**: How do you test a Spark job for data skew?  
**A3**: (1) Check partition sizes (`df.rdd.mapPartitions(lambda it: [sum(1 for _ in it)]).collect()`), (2) Identify skewed keys (GROUP BY with COUNT), (3) Validate no partition >2x average, (4) Fix with salting (add random suffix to skewed keys).

**Q4**: Explain exactly-once semantics in streaming.  
**A4**: Guarantee each event processed exactly once (no duplicates, no data loss). Achieved via: (1) Idempotent writes (same input → same output), (2) Transactional commits, (3) Deduplication (track processed event IDs). Test by sending duplicates, validating single count.

### Scenario (8-12 years)
**Q5**: Kafka consumer lag growing (events backing up). Troubleshoot?  
**A5**: (1) **Throughput issue**: Scale consumers (add to consumer group), (2) **Processing bottleneck**: Profile consumer code (optimize slow queries), (3) **Partition imbalance**: Check partition assignment (rebalance), (4) **Producer spike**: Validate producer isn't overwhelming system, (5) **Network**: Check latency between brokers/consumers.

### Architect (12+ years)
**Q6**: Design testing strategy for petabyte-scale data lake (10K datasets, 100+ pipelines)?  
**A6**: (1) **Sampling**: Test on 1% sample (statistically significant), full run on critical datasets only, (2) **Synthetic data**: Generate realistic test data (maintain distributions), (3) **Tiered testing**: Unit (Spark local), integration (10-node cluster), performance (production-scale cluster), (4) **Automated profiling**: Nightly data quality checks (volume, schema, freshness), (5) **Canary releases**: Deploy to 5% traffic, validate, scale to 100%, (6) **Observability**: Dashboards for pipeline health (latency, throughput, errors), (7) **Data contracts**: Schema validation at ingestion, quarantine bad data.

---

## Frequently Asked Questions

**Q1**: How to test distributed systems for fault tolerance?  
**A1**: (1) **Chaos engineering**: Randomly kill nodes during processing, (2) **Network partitions**: Simulate network splits, (3) **Validate recovery**: Confirm job completes after node restart, (4) **Data integrity**: No data loss or corruption after failures.

**Q2**: Difference between data lake and data warehouse?  
**A2**: **Lake**: Raw data, all formats (structured, unstructured), schema-on-read, cheap storage (S3/ADLS). **Warehouse**: Curated data, structured, schema-on-write, optimized for SQL queries. Lake = exploratory, Warehouse = production analytics.

**Q3**: How to validate Kafka message ordering?  
**A3**: (1) **Within partition**: Messages ordered by offset, (2) **Across partitions**: No ordering guarantee, (3) **Test**: Send events with timestamps, validate ascending order within partition, (4) **Use partition key**: Route related events to same partition (e.g., user_id as key).

**Q4**: Best practices for testing Spark jobs?  
**A4**: (1) **Local mode**: Test on small data (`spark.master("local[*]")`), (2) **Unit tests**: Test transformations with pytest, (3) **Integration tests**: Run on dev cluster with realistic data, (4) **Performance tests**: Benchmark on prod-scale cluster, (5) **CI/CD**: Automate tests in pipeline (GitHub Actions, Jenkins).

**Q5**: How to handle late-arriving data in streaming?  
**A5**: (1) **Watermarks**: Define max lateness (e.g., 10 min), drop events beyond watermark, (2) **Late-event table**: Quarantine late data for offline processing, (3) **Grace period**: Re-compute windows after delay to include late events, (4) **Test**: Send events out-of-order, validate handling.

**Q6**: What is data partitioning and why does it matter?  
**A6**: Splitting data into chunks (partitions) processed in parallel. Matters for: (1) **Performance**: Parallel processing reduces time, (2) **Scalability**: Add nodes to handle more partitions, (3) **Skew**: Uneven partitions cause bottlenecks. Test by validating partition sizes balanced.

**Q7**: How to test schema evolution in big data?  
**A7**: (1) **Backward compatibility**: Old readers can read new data (ignore new fields), (2) **Forward compatibility**: New readers can read old data (default values for missing fields), (3) **Test**: Write data with schema v1, read with schema v2 (and vice versa), (4) **Tools**: Avro, Protobuf, Parquet support schema evolution.

**Q8**: Difference between Parquet and ORC file formats?  
**A8**: Both columnar, compressed formats. **Parquet**: Spark/Impala ecosystem, better for nested data. **ORC**: Hive/Presto ecosystem, better compression. Choose based on query engine. QA: Test read/write performance, compression ratio.

**Q9**: How to test eventually consistent systems (e.g., Cassandra)?  
**A9**: (1) **Write then immediate read**: May not see latest value (eventual consistency), (2) **Validate convergence**: Wait (seconds), re-read, confirm latest value, (3) **Quorum reads**: Use consistency level QUORUM to read latest, (4) **Test**: Write, read from different node, validate data eventually appears.

**Q10**: What's the CAP theorem and how does it affect testing?  
**A10**: **CAP**: Can have only 2 of 3: Consistency, Availability, Partition tolerance. Distributed systems choose AP (Cassandra) or CP (HBase). **QA**: Test partition scenarios, validate system behaves per chosen tradeoff (e.g., AP system stays available during network split, may return stale data).

**Q11**: How to optimize Spark job performance?  
**A11**: (1) **Partitioning**: Repartition to match parallelism, (2) **Caching**: Cache frequently accessed DataFrames, (3) **Broadcasting**: Broadcast small lookup tables, (4) **Avoid shuffles**: Minimize groupBy/join operations, (5) **Columnar formats**: Use Parquet (skip unused columns), (6) **Test**: Profile with Spark UI (identify stages with high shuffle, skew).

**Q12**: How to test data lake access controls?  
**A12**: (1) **Authentication**: Validate only authorized users can access (IAM roles, SAS tokens), (2) **Authorization**: Test folder-level permissions (data steward vs. analyst), (3) **Encryption**: Validate data encrypted at rest (S3 SSE, ADLS encryption), (4) **Audit**: Confirm access logged (CloudTrail, Azure Monitor), (5) **Negative tests**: Verify unauthorized users denied.

**Q13**: What's data lineage and how to test it?  
**A13**: Tracking data flow from source → transformations → consumption. **Test**: (1) Trace single record across systems, (2) Validate metadata (source_system, insert_timestamp), (3) Use lineage tools (Collibra, Atlan) to visualize flow, (4) Impact analysis: Change source, confirm downstream updates.

**Q14**: How to handle time zones in distributed systems?  
**A14**: (1) **Standardize**: Store all timestamps in UTC, (2) **Convert**: Apply timezone offset at query time, (3) **Test**: Validate DST transitions (spring forward, fall back), (4) **Multi-region**: Test events from different timezones arrive in correct order.

**Q15**: Best practices for testing real-time dashboards?  
**A15**: (1) **Latency**: Measure event-to-visualization time (<5 sec target), (2) **Accuracy**: Validate metrics match source data, (3) **Refresh rate**: Confirm dashboard updates at expected interval, (4) **Load**: Test with 100+ concurrent users, (5) **Alerting**: Validate alerts trigger at correct thresholds.

**Q16**: How to test data deduplication?  
**A16**: (1) **Insert duplicates**: Send same event twice, (2) **Validate single count**: Confirm dedupe logic applied, (3) **Test keys**: Verify composite key deduplication (user_id + timestamp), (4) **Fuzzy dedup**: Test similarity-based deduplication (Levenshtein distance for names).

**Q17**: What's backpressure in streaming and how to test?  
**A17**: When producer sends events faster than consumer can process, causing buffer overflow. **Test**: (1) Send events at 2x consumer throughput, (2) Validate backpressure mechanism (Kafka broker stops accepting, Spark pauses reading), (3) Confirm no data loss, (4) Monitor lag metrics.

**Q18**: How to validate GDPR compliance in data lake?  
**A18**: (1) **Right to access**: Test user data export API, (2) **Right to erasure**: Validate hard delete (S3 object delete, Delta tombstone), (3) **Data minimization**: Audit for unnecessary PII, (4) **Retention**: Confirm old data purged per policy (90 days), (5) **Encryption**: Validate PII encrypted at rest.

**Q19**: Difference between micro-batch and true streaming?  
**A19**: **Micro-batch**: Process small batches frequently (Spark Structured Streaming: 1-sec batches). **True streaming**: Process each event individually (Flink, Storm). Micro-batch = simpler, higher throughput. True streaming = lower latency. QA: Test latency requirements.

**Q20**: How to test data recovery after disaster?  
**A20**: (1) **Backup validation**: Restore from backup, validate data integrity, (2) **RTO**: Measure time to restore (Recovery Time Objective < 4hr target), (3) **RPO**: Validate data loss window (Recovery Point Objective < 1hr), (4) **Failover**: Test regional failover (primary datacenter down), (5) **DR drill**: Annual full disaster recovery exercise.

---

## Actionable Checklists

### Big Data Testing Checklist
- [ ] Volume testing (scale to expected data size)
- [ ] Velocity testing (throughput, latency at peak load)
- [ ] Variety testing (multiple formats: CSV, JSON, Parquet)
- [ ] Data quality validation (completeness, accuracy)
- [ ] Schema evolution tested (backward/forward compatibility)
- [ ] Fault tolerance validated (node failures, network partitions)
- [ ] Partitioning verified (balanced, no skew)
- [ ] Performance benchmarked (vs. SLA)

### Streaming Pipeline Testing Checklist
- [ ] Event ordering validated (within partition)
- [ ] Exactly-once semantics verified (no duplicates)
- [ ] Late-arriving data handled (watermarks, grace period)
- [ ] Backpressure tested (producer > consumer throughput)
- [ ] Consumer lag monitored (alert thresholds)
- [ ] Windowing operations correct (tumbling, sliding, session)
- [ ] State management tested (checkpointing, recovery)
- [ ] End-to-end latency measured (event → output)

### Data Lake Quality Checklist
- [ ] Zone architecture validated (raw → curated → analytical)
- [ ] Data lineage tracked (source → transformations → consumption)
- [ ] Access controls tested (authentication, authorization)
- [ ] Encryption verified (at rest, in transit)
- [ ] Schema registry implemented (centralized schema management)
- [ ] Data catalog updated (metadata, descriptions)
- [ ] Retention policies enforced (automated purge)
- [ ] Compliance validated (GDPR, HIPAA as applicable)

---

## References

### Books
- **Designing Data-Intensive Applications** (Martin Kleppmann): Distributed systems bible
- **Streaming Systems** (Akidau, Chernyak, Lax): Streaming architecture
- **Big Data: Principles and Best Practices** (Nathan Marz): Lambda/Kappa architectures

### Standards
- **TPC-DS**: Industry benchmark for analytics (decision support)
- **TPC-H**: Benchmark for ad-hoc queries

### Tools Documentation
- **Apache Spark**: https://spark.apache.org/docs
- **Apache Kafka**: https://kafka.apache.org/documentation
- **Delta Lake**: https://docs.delta.io
- **Databricks**: https://docs.databricks.com

---

**Core References**: Platform-agnostic big data concepts  
**Stack Deltas**: See Databricks/EMR/Dataproc stack files for platform-specific implementations

**Previous**: [04_ETL_Concepts.md](./04_ETL_Concepts.md)  
**Next**: [06_AI_Concepts.md](./06_AI_Concepts.md)  
**Up**: [Master Index](../00_MASTER_INDEX.md)