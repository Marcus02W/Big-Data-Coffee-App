from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import IntegerType, StringType, StructType, TimestampType, StructField

dbUrl = 'jdbc:postgresql://my-app-postgres-service:5432/coffee_db'
dbOptions = {
    "user": "coffee_db_technical_user",
    "password": "coffeedb",
    "driver": "org.postgresql.Driver"
}
dbSchema = 'public'
tableName = 'coffee_types'




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
    batchDataframe.distinct().write.jdbc(dbUrl, f"{dbSchema}.{tableName}", "append", dbOptions)

# test write
schema = StructType([
    StructField("coffee_type", StringType(), nullable=False),
    StructField("size", StringType(), nullable=False)
])

# Create a batch DataFrame with a single entry
data = [("Spark coffee", "S")]
batch_df = spark.createDataFrame(data, schema)

saveToDatabase(batch_df, 1)


# Wait for termination
spark.streams.awaitAnyTermination()
