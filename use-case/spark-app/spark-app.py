from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import IntegerType, StringType, StructType, TimestampType

dbUrl = 'jdbc:mysql://my-app-mariadb-service:3306'
dbOptions = {"user": "root", "password": "mysecretpw", "driver": "com.mysql.jdbc.Driver","isolationLevel": "READ_COMMITTED"}
dbSchema = 'popular'
tableName = 'popular'

windowDuration = '1 minute'
slidingDuration = '1 minute'

# Example Part 1
# Create a spark session
spark = SparkSession.builder \
    .appName("Use Case").getOrCreate()

# Set log level
spark.sparkContext.setLogLevel('WARN')

# Example Part 2
# Read messages from Kafka
kafkaMessages = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers",
            "my-cluster-kafka-bootstrap:9092") \
    .option("subscribe", "tracking-data") \
    .option("startingOffsets", "earliest") \
    .load()

# Define schema of tracking data
trackingMessageSchema = StructType() \
    .add("mission", StringType()) \
    .add("timestamp", IntegerType())

# Example Part 3
# Convert value: binary -> JSON -> fields + parsed timestamp
trackingMessages = kafkaMessages.select(
    # Extract 'value' from Kafka message (i.e., the tracking data)
    from_json(
        column("value").cast("string"),
        trackingMessageSchema
    ).alias("json")
).select(
    # Convert Unix timestamp to TimestampType
    from_unixtime(column('json.timestamp'))
    .cast(TimestampType())
    .alias("parsed_timestamp"),

    # Select all JSON fields
    column("json.*")
) \
    .withColumnRenamed('json.mission', 'mission') \
    .withWatermark("parsed_timestamp", windowDuration)

# Example Part 4
# Compute most popular slides
popular = trackingMessages.groupBy(
    window(
        column("parsed_timestamp"),
        windowDuration,
        slidingDuration
    ),
    column("mission")
).count() \
 .withColumnRenamed('window.start', 'window_end') \
 .withColumnRenamed('window.end', 'window_start') \

# Example Part 5
# Start running the query; print running counts to the console
# consoleDump = popular \
#     .writeStream \
#     .outputMode("update") \
#     .format("console") \
#     .start()

# Example Part 6
def saveToDatabase(batchDataframe, batchId):
    global dbUrl, dbSchema, dbOptions
    print(f"Writing batchID {batchId} to database @ {dbUrl}")
    batchDataframe.distinct().write.jdbc(dbUrl, f"{dbSchema}.{tableName}", "overwrite", dbOptions)


# Example Part 7
dbInsertStream = popular \
    .select(column('mission'), column('count')) \
    .writeStream \
    .outputMode("complete") \
    .foreachBatch(saveToDatabase) \
    .start()

# Wait for termination
spark.streams.awaitAnyTermination()
