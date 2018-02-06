from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
from redis import Redis, RedisError
import os
import socket
import logging
import signal
import sys

optionA = "Futbol"
optionB = "Soccer"
name = optionA + " VS " + optionB

redis = Redis(host="redis", db=0)
app = Flask(__name__)


@app.route("/", methods=['POST','GET'])
def hello():
    try:
        votesB = redis.get(optionB) or 0
        votesA = redis.get(optionA) or 0
    except RedisError:
        votesB = "<i>cannot connect to Redis, counter disabled</i>"
        votesA = "<i>cannot connect to Redis, counter disabled</i>"
    if request.method == 'POST':
        if request.form['option'] == 'optionA':
            try:
                votesA = redis.incr(optionA)
                if int(votesB) > 0 and 'optionB' == request.cookies.get('vote'):
                    votesB = redis.decr(optionB);
                redis.publish('pubsub', '{"'+optionA+'":'+str(votesA)+', "'+optionB+'":'+str(votesB)+'}')
            except Exception as e:
                print e
                votesA = "<i>An error occured</i>"
            resp = make_response(render_template('index.html', name=os.getenv('NAME', name), hostname=socket.gethostname(), optionA=optionA, optionB=optionB))
            resp.set_cookie('vote', 'optionA')
            return resp
        if request.form['option'] == 'optionB':
            try:
                votesB = redis.incr(optionB)
                if int(votesA) > 0 and 'optionA' == request.cookies.get('vote'):
                    votesA = redis.decr(optionA);
                redis.publish('pubsub', '{"'+optionA+'":'+str(votesA)+', "'+optionB+'":'+str(votesB)+'}')
            except Exception as e:
                print e
                votesB = "<i>An error occured</i>"
            resp = make_response(render_template('index.html', name=os.getenv('NAME', name), hostname=socket.gethostname(), optionA=optionA, optionB=optionB))
            resp.set_cookie('vote', 'optionB')
            return resp
        else:
            return render_template('index.html', name=os.getenv('NAME', name), hostname=socket.gethostname(), optionA=optionA, optionB=optionB)
    elif request.method == 'GET':
        return render_template('index.html', name=os.getenv('NAME', name), hostname=socket.gethostname(), optionA=optionA, optionB=optionB)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, sys.exit)
    app.run(host='0.0.0.0', port=80)
