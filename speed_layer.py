import os, pymongo, json, numpy as np
from pyspark.sql import SparkSession

os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 pyspark-shell'

# Connect to MongoDB as a client with root user and example password 
# CLIENT = pymongo.MongoClient('mongodb://root:example@127.0.0.1')
CLIENT = pymongo.MongoClient('localhost', 27017)

# Connect to ADSI2122 DDBB
DATABASE = CLIENT.ADSI2122

# Proccess each data of spark streaming
def process_data(df, batch_id):

    # Proccessing each rdd from spark dataframe
    tweets = df.rdd.map(lambda x: x.value).collect()

    # # for each set of tweets we decode it and insert to MongoDB with mongo_parse function 
    hashtags = ['#'+hashtag['text'] for tweet in tweets for hashtag in json.loads(tweet.decode('UTF-8'))['entities']['hashtags']]

    # If hashtags exist then store it in online collection
    if hashtags:
        print("Consumed data from Kafka using streaming spark:", hashtags)

        # Group by hashtag frequency
        unique, counts = np.unique(hashtags, return_counts=True) 
        res = [int(elem) for elem in counts]

        # Insert streaming hashtags into online collection in MongoDB
        DATABASE.online.insert_one(dict(zip(unique, res)))


if __name__ == '__main__':

    # Create a Spark Session called TwitterApp
    spark = SparkSession.builder.appName("TwitterApp")\
    .getOrCreate()

    # Set log level to ERROR (just show errors)
    spark.sparkContext.setLogLevel('ERROR')

    # Use readStream to read streaming data from kafka as a consumer
    # Select localhost:9092 as Kafka service
    # Subscribe to tweets topic of kafka
    # Get latest tweets available in Kafka cluster
    kafkaStream = spark.readStream.format("kafka")\
        .option("kafka.bootstrap.servers","localhost:9092")\
        .option("subscribe","tweets")\
        .option("startingOffsets", "latest")\
        .load()

    # Process each streaming data with process_data function
    # If it detects daata loss then stop execution
    # Start stream and wait until it finish
    query = kafkaStream.writeStream \
        .foreachBatch(process_data) \
        .option("failOnDataLoss", "true") \
        .start().awaitTermination()