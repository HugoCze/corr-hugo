############################################################
# SECTION 1: INITIALIZATION AND CONFIGURATION
############################################################
# Multiple ways to initialize Spark based on your needs
from pyspark.sql import SparkSession

# Basic local development setup
spark_local = SparkSession.builder \
    .appName("LocalDev") \
    .master("local[*]") \
    .getOrCreate()

# Production setup with detailed configuration
spark_prod = SparkSession.builder \
    .appName("ProductionApp") \
    .master("yarn") \
    .config("spark.executor.memory", "4g") \
    .config("spark.executor.cores", "2") \
    .config("spark.driver.memory", "2g") \
    .config("spark.driver.cores", "2") \
    .config("spark.default.parallelism", "100") \
    .config("spark.sql.shuffle.partitions", "100") \
    .config("spark.memory.fraction", "0.6") \
    .config("spark.memory.storageFraction", "0.5") \
    .config("spark.speculation", "true") \
    .enableHiveSupport() \
    .getOrCreate()

# Configuration for handling large JSON files
spark_json = SparkSession.builder \
    .appName("JSONProcessor") \
    .config("spark.sql.files.maxPartitionBytes", "128MB") \
    .config("spark.sql.files.openCostInBytes", "4194304") \
    .config("spark.sql.broadcastTimeout", "600") \
    .getOrCreate()

############################################################
# SECTION 2: DATABASE CONNECTIONS
############################################################
# JDBC Connection Examples for different databases

# PostgreSQL Connection
postgres_df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5432/dbname") \
    .option("dbtable", "schema.table") \
    .option("user", "username") \
    .option("password", "password") \
    .option("fetchsize", "10000") \
    .load()

# MongoDB Connection using mongo-spark-connector
mongodb_df = spark.read \
    .format("com.mongodb.spark.sql.DefaultSource") \
    .option("uri", "mongodb://username:password@host:port/database.collection") \
    .option("pipeline", """[
        {"$match": {"status": "active"}},
        {"$project": {"_id": 1, "name": 1, "value": 1}}
    ]""") \
    .load()

# Cassandra Connection
cassandra_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .option("table", "table_name") \
    .option("keyspace", "keyspace_name") \
    .option("spark.cassandra.connection.host", "localhost") \
    .option("spark.cassandra.connection.port", "9042") \
    .load()

############################################################
# SECTION 3: OPTIMIZED READING STRATEGIES
############################################################
# Reading large CSV files efficiently
large_csv_df = spark.read \
    .format("csv") \
    .option("header", "true") \
    .option("maxFilesPerTrigger", 1) \
    .option("cleanSource", "archive") \
    .option("mode", "DROPMALFORMED") \
    .option("maxCharsPerColumn", 4096) \
    .schema(defined_schema) \  # Always define schema for large files
    .load("path/to/csv")

# Reading Parquet with predicate pushdown
filtered_parquet = spark.read \
    .parquet("path/to/parquet") \
    .filter(F.col("date") > "2024-01-01") \  # Pushdown to Parquet scan
    .select("id", "value")  # Column pruning