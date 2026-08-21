# 06 — Kafka & Streaming Handbook
# Chapter 1: Apache Kafka — Core Concepts

> Real-time streaming is tested at senior level. You need to explain Kafka's
> architecture clearly, know the difference between batch and streaming,
> and understand how Spark Structured Streaming connects to Kafka.

---

## 🏗️ Kafka Architecture

```
Producers → Kafka Cluster → Consumers
               |
        ┌──────┴──────┐
        │   Broker 1  │  Broker 2  │  Broker 3
        │   Topic A   │  Topic A   │  Topic A
        │   Part 0    │  Part 1    │  Part 2
        └─────────────┘
                |
           ZooKeeper / KRaft (metadata)
```

**Interview Q:** *"Explain Kafka's architecture end to end."*

```
Producer    → application that writes (publishes) records to Kafka
Broker      → a Kafka server that stores and serves records
              Cluster = multiple brokers for fault tolerance
Topic       → logical channel for records (like a database table name)
Partition   → physical unit of a topic; ordered, immutable log of records
              More partitions = more parallelism
Offset      → unique sequential ID of a record within a partition
Consumer    → application that reads records from Kafka
Consumer Group → multiple consumers sharing work; each partition → one consumer
ZooKeeper   → manages cluster metadata (being replaced by KRaft in newer Kafka)
```

---

## 📦 Topics, Partitions & Offsets

**Interview Q:** *"How does Kafka guarantee message ordering?"*

Kafka guarantees ordering **within a partition**, NOT across partitions.

```
Topic: "user_events"
  Partition 0:  [msg0] [msg1] [msg4] [msg7]   ← user_id % 3 == 0
  Partition 1:  [msg2] [msg5] [msg8]          ← user_id % 3 == 1
  Partition 2:  [msg3] [msg6] [msg9]          ← user_id % 3 == 2
```

- All events for a given user_id go to the same partition (via partition key)
- Within that partition, events are ordered by arrival time
- A consumer assigned to Partition 0 reads messages in order

**Interview Q:** *"How many partitions should a topic have?"*

Rule of thumb: `partitions ≥ number of consumers in the group`.
Too few partitions → bottleneck (consumers sit idle).
Too many → coordination overhead, more files, complex rebalancing.

---

## ✍️ Producers

```
Key concepts:
  - Records = key + value + timestamp + headers
  - Partition key → same key always goes to same partition (message ordering per key)
  - Acknowledgments (acks):
      acks=0   → fire and forget (fastest, may lose data)
      acks=1   → leader confirms (moderate, loses data on leader crash)
      acks=all → all replicas confirm (slowest, no data loss) ← production standard
  - Batching → producer groups records and sends in batches for throughput
  - Compression → snappy/lz4/zstd reduces network I/O
```

**Interview Q:** *"What are the delivery semantics in Kafka?"*

| Semantic | Description | Risk |
|---|---|---|
| At-most-once | Messages may be lost | Data loss |
| At-least-once | Messages may be duplicated | Duplicates |
| Exactly-once | No loss, no duplicates | Complex, higher overhead |

Exactly-once requires: idempotent producers + transactional API + compatible consumers.

---

## 📖 Consumers & Consumer Groups

**Interview Q:** *"How does a consumer group work? What happens when a consumer dies?"*

```
Consumer Group "payments-processor" reading "transactions" topic (3 partitions):

Initially:
  Consumer A → Partition 0
  Consumer B → Partition 1
  Consumer C → Partition 2

Consumer B dies → Kafka triggers REBALANCE:
  Consumer A → Partition 0, 1
  Consumer C → Partition 2
```

- Each partition is consumed by exactly ONE consumer in a group
- Multiple consumer groups can read the same topic independently (each gets all messages)
- Offset is committed per consumer group — each group tracks its own position

```
Topic: "orders"
  Consumer Group "billing" → reads from offset 100
  Consumer Group "shipping" → reads from offset 95 (different pace)
```

**Interview Q:** *"What is consumer lag?"*

The difference between the latest offset in a partition and the consumer's current offset.
High lag = consumer is falling behind. Monitor with `kafka-consumer-groups.sh --describe`.

---

## 💾 Retention, Compaction & Replication

**Interview Q:** *"How long does Kafka keep messages? What is log compaction?"*

**Retention:**
```
Time-based:  retain for N days (default 7 days). Old records deleted.
Size-based:  retain until topic size > N bytes. Oldest records deleted.
```

**Log compaction:**
Instead of deleting by time/size, Kafka keeps only the **latest value per key**.
```
Before compaction:
  key=user1 → {"name": "Alice"}
  key=user2 → {"name": "Bob"}
  key=user1 → {"name": "Alice Smith"}   ← newer

After compaction:
  key=user2 → {"name": "Bob"}
  key=user1 → {"name": "Alice Smith"}   ← only latest kept
```
Use case: CDC (change data capture), maintaining current state of a record.

**Replication:**
```
Replication factor = number of copies of each partition across brokers.
  replication.factor=3 → 1 leader + 2 followers
  Leader handles all reads/writes
  Followers replicate from leader
  If leader dies → one follower is elected new leader (ISR = In-Sync Replicas)
```

---

## ⚡ Kafka Connect (Source & Sink Connectors)

**Interview Q:** *"What is Kafka Connect? Why is it important for data pipelines?"*

Kafka Connect is a framework for moving data INTO and OUT OF Kafka without writing code.

```
Source Connector → reads from external system → writes to Kafka
  Examples: JDBC (databases), Debezium (CDC), S3 Source, MongoDB

Sink Connector → reads from Kafka → writes to external system
  Examples: S3 Sink, Elasticsearch, Snowflake, BigQuery, JDBC Sink
```

This enables **CDC pipelines** without writing producer/consumer code:
```
PostgreSQL (Debezium CDC) → Kafka → S3 Sink Connector → S3
                                 → BigQuery Sink → BigQuery
```

---

## 🔁 Kafka Streams vs Spark Structured Streaming

**Interview Q:** *"Kafka Streams vs Spark Structured Streaming — when would you use each?"*

| Feature | Kafka Streams | Spark Structured Streaming |
|---|---|---|
| Deployment | Library (in your app) | Separate Spark cluster |
| Scale | Moderate (JVM heap) | Massive (distributed) |
| Latency | Very low (ms) | Low (seconds) |
| State | RocksDB embedded | Checkpointed to HDFS/S3 |
| Joins | Within Kafka only | Rich join support |
| Use Case | Microservice-level transformations | Large-scale stream processing |

---

## ❓ Top 10 Kafka Interview Questions

**Q1: What is the difference between a topic and a partition?**
Topic = logical category (like a table name). Partition = physical shard of that topic. One topic can have many partitions for parallelism.

**Q2: Why can't you decrease the number of partitions in a topic?**
Decreasing partitions would require rebalancing all existing data — Kafka doesn't support this. You create a new topic with fewer partitions and migrate.

**Q3: What happens to messages when a Kafka broker goes down?**
If replication factor > 1, a follower in the ISR becomes the new leader. Producers/consumers reconnect automatically. No data loss if acks=all.

**Q4: How do you ensure exactly-once processing in Kafka?**
Enable idempotent producers (enable.idempotence=true) + transactions + configure consumers to read only committed transactions (isolation.level=read_committed).

**Q5: What is a dead letter queue (DLQ) in Kafka?**
A separate topic where messages that failed processing are sent. Prevents poison pills from blocking the main consumer. Consumer catches processing exceptions and publishes to DLQ.

**Q6: How do you replay Kafka messages from the beginning?**
Reset the consumer group offset: `kafka-consumer-groups.sh --reset-offsets --to-earliest --execute`. This lets you reprocess historical data.

**Q7: What is Debezium and how does it enable CDC?**
Debezium is a Kafka Connect source connector that reads database transaction logs (MySQL binlog, PostgreSQL WAL, Oracle redo logs) and produces a change event to Kafka for every INSERT/UPDATE/DELETE.

**Q8: What is a schema registry?**
A service (usually Confluent Schema Registry) that stores Avro/JSON/Protobuf schemas. Producers register schemas; consumers validate messages against the registered schema. Prevents schema mismatches from breaking consumers.

**Q9: How many consumers can read from a single partition simultaneously?**
Only ONE consumer per partition per consumer group. If you need more parallelism, increase the number of partitions.

**Q10: How does Kafka handle backpressure?**
Consumers control their own read rate (pull model). Producers can configure `max.block.ms` and `buffer.memory`. Kafka itself doesn't push to consumers — consumers pull at their own pace, so natural backpressure is built in.
