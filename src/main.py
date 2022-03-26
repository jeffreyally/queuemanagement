"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
from datastructure import Queue  
from sms import send  
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#instance of Queue class
DinnerLine = Queue()

#adds a new person to the queue
@app.route('/new', methods=['POST'])
def addtoqueue():
    guest = request.json
    LineSize = DinnerLine.size()
    DinnerLine.enqueue(guest)
    
    #send customer a message he is added and how many are in line

    response_body = {
        "msg": f"{guest['name']} You have been added to the queue. There are {LineSize} in front of you"
    }

    return jsonify(response_body), 200
#this endpoint handles the next person to be seated
@app.route('/next', methods=['GET'])
def nextinline():
    #checks if the DinnerLine exists. If list size is more than 0, this is "truthy"
    if DinnerLine.size():

        removed = DinnerLine.dequeue()
        send(body='Table is ready',to=+17862670046)
        response_body = {
            "msg": f"Table is ready {removed['name']}, and they are contacted"
        }
    # an empty list is a "falsey" hence we return the msg No one in queue
    else:
        response_body = {
            "msg": "No one in queue"
        }


    return jsonify(response_body), 200

#this endpoint gets entire queue
@app.route('/wholequeue', methods=['GET'])
def wholeline():
    DinnerLine.get_queue()
    #this can be removed and return just the value of msg with 200....I think
    response_body = {
        "msg": "Total in line: " + str(len(DinnerLine.get_queue()))
    }

    return jsonify(response_body), 200



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


#add token and sid to env file
#from_=
# to=