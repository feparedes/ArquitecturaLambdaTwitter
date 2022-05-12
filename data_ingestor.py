import tweepy, pymongo, json
from kafka import KafkaProducer
import utils

# Defining a Kafka Producer and its topic
producer = KafkaProducer(bootstrap_servers='localhost:9092')
topic_name = 'tweets'

# Connect to MongoDB as a client with root user and example password 
# CLIENT = pymongo.MongoClient('mongodb://root:example@127.0.0.1')
CLIENT = pymongo.MongoClient('localhost', 27017)

# Connect to ADSI2122 Database
DATABASE = CLIENT.ADSI2122

class DataIngestor(tweepy.Stream):
    def on_status(self, status):

        # Map tweets as JSON
        tweets = status._json

        # Serialize JSONs tweets
        serialized_tweet = json.dumps(tweets)

        print(status.created_at, '-', status.text)
        
        # Insert JSON tweets into MongoDB
        DATABASE.tweets.insert_one(tweets)

        # Kafka producer sends serialized JSON tweets to Kafka cluster with 'tweets' as a topic
        producer.send(topic_name, serialized_tweet.encode('UTF-8'))

if __name__ == '__main__':

    # Declaring credetentials to Twitter API access
    consumer_key = utils.CONSUMER_KEY
    consumer_secret = utils.CONSUMER_SECRET
    access_token = utils.ACCESS_TOKEN
    access_secret = utils.ACCESS_SECRET

    # Create DataIngestor instance to query Twitter API with Tweepy
    data_ingestor = DataIngestor( consumer_key, consumer_secret, access_token, access_secret)

    # Filter to get spanish tweets
    data_ingestor.filter(track="Tweepy",languages=['es'])

