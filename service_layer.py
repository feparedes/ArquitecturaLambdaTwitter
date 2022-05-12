import pymongo, json 
from bson.objectid import ObjectId
from flask import Flask,render_template,url_for,request,redirect, make_response
from time import time
import numpy as np

# Create Flask App
app = Flask(__name__)

# Connect to MongoDB as a client with root user and example password 
# CLIENT = pymongo.MongoClient('mongodb://root:example@127.0.0.1')
CLIENT = pymongo.MongoClient('localhost', 27017)

# Connect to ADSI2122 DDBB
DATABASE = CLIENT.ADSI2122

# Make a Javascript response
def get_response(res):
    response = make_response(json.dumps(res))
    response.content_type = 'application/json'
    return response

def get_online_data():

    # Get last offline document in offline collection from MongoDB
    last_document = DATABASE.offline.find().sort('_id',-1).limit(1)[0]
    
    # Get online hashtag whose date is higher than last document date
    filtered_documents = DATABASE.online.find({'_id': {'$gt': ObjectId(last_document['_id'])}})

    # Get hashtags and its frequency from online collection (process online data)
    hashtags=dict()
    for document in filtered_documents:
        for hashtag in document:
            if hashtag!='_id' and hashtag in hashtags:
                hashtags[hashtag] += document[hashtag]
            elif hashtag!='_id' and hashtag not in hashtags:
                hashtags[hashtag] = document[hashtag]
    
    return hashtags

def get_offline_data():

    # Get last offline document in offline collection from MongoDB
    last_document = DATABASE.offline.find().sort('_id',-1).limit(1)[0]

    return last_document

def get_merged_data():

    # Get last offline document in offline collection from MongoDB
    last_document = get_offline_data()
    
    # Get online hashtag whose date is higher than last document date
    filtered_documents = get_online_data()

    # Updating offline last document with online data
    for hashtag in filtered_documents:
        if hashtag in last_document:
            last_document[hashtag] += filtered_documents[hashtag]
        else:
            last_document[hashtag] = filtered_documents[hashtag]

    return last_document

@app.route('/online_data', methods=["GET", "POST"])
def get_online_data_response():

    # Get online data
    hashtags = get_online_data()

    # Transform hashtags data in order to show it as a chart
    data = [[key, hashtags[key]] for key in hashtags if key != '_id']

    # Sort data from higher to lower
    data.sort(key=lambda x: x[1] , reverse=True)

    # Return a javascript response 
    return get_response(data)

@app.route('/offline_data', methods=["GET", "POST"])
def get_offline_data_response():

    # Get offline data
    last_document = get_offline_data()

    # Transform hashtags data in order to show it as a chart
    data = [[key, last_document[key]] for key in last_document if key != '_id']

    # Sort data from higher to lower
    data.sort(key=lambda x: x[1] , reverse=True)

    # Return a javascript response 
    return get_response(data)

@app.route('/lambda_data', methods=["GET", "POST"])
def get_lambda_data_response():
    
    # Get merged data
    hashtags = get_merged_data()

    # Transform hashtags data in order to show it as a chart
    data = [[key, hashtags[key]] for key in hashtags if key != '_id']

    # Sort data from higher to lower
    data.sort(key=lambda x: x[1] , reverse=True)

    # Return a javascript response 
    return get_response(data)

@app.route('/lambda_live_data', methods=["GET", "POST"])
def get_lambda_live_data():

    # Get merged data
    hashtags = get_merged_data()

    # Transform hashtags data in order to show it as a chart
    data = [[key, hashtags[key]] for key in hashtags if key != '_id']

    # Sort data from higher to lower
    data.sort(key=lambda x: x[1] , reverse=True)

    res = [par[1] for par in data]
    data = [ [time() * 1000, frecuencia] for frecuencia in res]

    # Return a javascript response 
    return get_response(data)

@app.route('/lambda_live_data_tags', methods=["GET", "POST"])
def get_lambda_live_data_tags():

    # Get merged data
    hashtags = get_merged_data()

    # Transform hashtags data in order to show it as a chart
    data = [[key, hashtags[key]] for key in hashtags if key != '_id']

    # Sort data from higher to lower
    data.sort(key=lambda x: x[1] , reverse=True)

    res = [par[0] for par in data]
    data = [frecuencia for frecuencia in res]

    # Return a javascript response 
    return get_response(data)

# Lambda model - Speed layer
@app.route('/online')
def online():
    return render_template('online.html')

# Lambda model - Batch layer
@app.route('/offline')
def offline():
    return render_template('offline.html')


# Lambda model merging data

# Bar chart
@app.route('/lambda_bar')
def lambda_bar_model():
    return render_template('lambda_bar.html')

# Pie chart
@app.route('/lambda_pie')
def lambda_pie_model():
    return render_template('lambda_pie.html')

# Bubble chart
@app.route('/lambda_bubble')
def lambda_bubble_model():
    return render_template('lambda_bubble.html')

# Live chart
@app.route('/lambda_live')
def lambda_live_model():
    return render_template('lambda_live.html')

# Home
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    
    # Run flask app
    app.run()