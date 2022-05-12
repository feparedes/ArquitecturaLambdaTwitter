import pymongo, schedule, time, numpy as np

# Connect to MongoDB as a client with root user and example password 
# CLIENT = pymongo.MongoClient('mongodb://root:example@127.0.0.1')
CLIENT = pymongo.MongoClient('localhost', 27017)

# Connect to ADSI2122 DDBB
DATABASE = CLIENT.ADSI2122

def batch_job():

    # Get tweets from datalake
    tweets = DATABASE.tweets.find({})
    
    # Mapping tweets to get a list of hashtags
    hashtags = ['#'+hashtag['text'] for tweet in tweets for hashtag in tweet['entities']['hashtags']]
    
    # Group by hashtag frequency
    unique, counts = np.unique(hashtags, return_counts=True) 
    res = [int(elem) for elem in counts]

    # Insert processing data into offline collection
    print("Inserting ", len(unique), 'hashtags...')
    DATABASE.offline.insert_one(dict(zip(unique, res)))
    print('Inserted\n')


if __name__ == '__main__':

    # Schedule a job each 100 seconds
    schedule.every(100).seconds.do(batch_job)

    while True:
        schedule.run_pending()
        time.sleep(1)