from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)
client = MongoClient(os.getenv("MONGO_URI"))
db = client.github_events
collection = db.events

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event = request.headers.get('X-GitHub-Event')

    if event == 'push':
        record = {
            'author': data['pusher']['name'],
            'to_branch': data['ref'].split('/')[-1],
            'action': 'push',
            'timestamp': datetime.utcnow()
        }

    elif event == 'pull_request':
        pr = data['pull_request']
        action_type = data['action']

        if action_type == 'opened':
            record = {
                'author': pr['user']['login'],
                'from_branch': pr['head']['ref'],
                'to_branch': pr['base']['ref'],
                'action': 'pull_request',
                'timestamp': datetime.utcnow()
            }
        elif action_type == 'closed' and pr.get('merged'):
            record = {
                'author': pr['user']['login'],
                'from_branch': pr['head']['ref'],
                'to_branch': pr['base']['ref'],
                'action': 'merge',
                'timestamp': datetime.utcnow()
            }
        else:
            return '', 204  # Ignore other PR events like "closed" without merge

    else:
        return '', 204

    collection.insert_one(record)
    return '', 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events')
def events():
    events = list(collection.find().sort("timestamp", -1).limit(10))
    for event in events:
        event['_id'] = str(event['_id'])  # To make it JSON serializable
        event['timestamp'] = event['timestamp'].strftime("%d %b %Y - %I:%M %p UTC")
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True)