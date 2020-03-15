
# step 1: import the redis-py client package
import redis
import random

# step 2: define our connection information for Redis
# Replaces with your configuration information
redis_host = "localhost"
redis_port = 6379
redis_password = ""

random.seed(444)
hats = {"Name":"Pradeep", "Company":"SCTL", "Address":"Mumbai", "Location":"RCP"}

try:
    r = redis.Redis("localhost", 6379,db=0)
    print("Redis Clinet Connect .......")    

except Exception as e:      
    print(e)

def SetHash(data):
    r.hmset("Data",data)
    b = r.hgetall("Data")
    x = { y.decode('ascii'): b.get(y).decode('ascii') for y in b.keys() }
    print(r.hexists("Dat",""))
    

if __name__ == '__main__':
    SetHash(hats)