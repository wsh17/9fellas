import os
import json
from threading import Thread
import time
from time import sleep
from flask import Flask, json, render_template, request
import redis
from collections import OrderedDict
import requests

from Queue import Queue

REGISTRAR_URL = 'http://9fellas.cfapps.io/update'

app = Flask(__name__)
port = int(os.getenv("PORT"))
vcap = json.loads(os.environ['VCAP_SERVICES'])
svc = vcap['rediscloud'][0]['credentials']

db = redis.StrictRedis(host=svc["hostname"], port=svc["port"], password=svc["password"],db=0)

application_name = json.loads(os.environ['VCAP_APPLICATION'])['application_name']

class Producer(Thread):
    """
    Background thread for fetching instance info
    """
    def __init__(self,queue):
        """
        Constructor
        """
        Thread.__init__(self)
        self.queue = queue
    def run(self):
        """
        This is the run implementation of the background thread , which fetchs the instaces info.
        """
        while True :
            try:
                instance_id = os.getenv("CF_INSTANCE_INDEX")
                mydict = db.hgetall(application_name)
                if instance_id not in mydict :
                    self.queue.put(instance_id)
            except :
                pass
            finally:
                pass
class Consumer(Thread):
    """
    Backgrdound thread for fetching from Queue and updating redis
    """
    def __init__(self,queue):
        """
        Constrcutor
        """
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        """
        Run method for background thread which updates redis
        """
        while True :
            try :
                instance_id = self.queue.get()
                db.hset(application_name,instance_id,1)
            except:
                pass
            finally:
                pass

class MasterUpdater(Thread):
    """
    This background thread will update the aggregator/registrar app at provided url
    """
    def __init__(self,db,appname):
        """
        Constructor
        """
        Thread.__init__(self)
        self.db = db
        self.appname = appname
    def run(self):
        """
        Run implementation of background thread which updates the aggregator
        """
        while True :
            try:
                appinfo = self.db.hgetall(self.appname)
                appinfo_str = json.dumps(appinfo)
                data = {'applicationname':self.appname,'appinfo':appinfo_str}
                response = requests.post(REGISTRAR_URL, data=data)
                time.sleep(2)
            except :
                pass
def init_workers():
    """
    This method is for starting all worker threads.
    We are using three workers right now .
    1. One for fetching latest instances info and adds to Queue
    2. One for fetching from Queue and updating Redis
    3. For updating the aggregator app , about this applications info.
    All are deamon threads.
    """
    party_queue = Queue()
    p = Producer(party_queue)
    p.daemon = True
    c = Consumer(party_queue)
    c.deamon= True
    m = MasterUpdater(db,application_name)
    m.deamon = True
    p.start()
    c.start()
    m.start()

@app.template_filter()
def env_override(value, key):
    return os.getenv(key, value)

@app.route('/addthread')
def addthread():
    """
        This endpoint is for adding threads to the application.
        Loadbalancer decids to go for which instances and based on that thread is added to it.
    """
    instance_id = os.getenv("CF_INSTANCE_INDEX")
    print 'Instance Id ****************%s'%instance_id
    thread_count = int(db.hget(application_name,instance_id))
    thread_count+=1
    print 'Threadcount ****************%s'%thread_count
    result = db.hset(application_name,str(instance_id),str(thread_count))
    print 'HSET result %s'%result
    print db.hgetall(application_name)
    return json.dumps({'message':'success'})
@app.route('/deletethread')
def deletethread():
    """
        This endpoint is for deleting threads to the application.
    """
    instance_id = os.getenv("CF_INSTANCE_INDEX")
    print 'Instance Id **************%s'%instance_id
    thread_count = int(db.hget(application_name,instance_id))
    thread_count-=1
    db.hset(application_name,instance_id,thread_count)

    return json.dumps({'message':'success'})

@app.route('/update',methods=['POST'])
def update():
    """
    This is the entry point for updating the aggregator info
    Each of the invidividual apps will call this endpoint with their latest info
    """
    appname = request.form['applicationname']
    appdetails = request.form['appinfo']
    obj = json.loads(appdetails)
    if appname and obj:
        db.hset('applications', appname, appdetails)
    return json.dumps({'message':'success'})


@app.route('/applicationsdetails')
def applicationsdetails():
    """
    This is the endpoint for providing all info about the applications
    This is an internal method for registrator through which index.html loads all info
    """
    appdicts = db.hgetall('applications')
    finaldict = OrderedDict()
    for appname in sorted(appdicts):
        instances = json.loads(appdicts.get(appname))
        finaldict.__setitem__(appname,instances)
    return render_template('animals_squared.html', appdicts=finaldict)

@app.route('/instances')
def instances():
    """
        This will list out all the instances and threads per application.
        An application can see only it's threads and instances.
    """
    mydict = db.hgetall(application_name)
    ordered = OrderedDict()
    for key in sorted(mydict):
        ordered.__setitem__(key,mydict.get(key))
    mylist = []
    return render_template('animals.html', mydict=ordered)


@app.route('/')
def index():
    """
    Main entry point
    """
    return render_template('index.html')

if __name__ == "__main__":
    init_workers()
    app.run(host='0.0.0.0', port=port, debug=True)
