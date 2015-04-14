import os
import redis
app = Flask(__name__)
db = redis.StrictRedis(host="localhost", port="6789", password="",db=0)
db.hmset(instances,('instance_id',"1"))
