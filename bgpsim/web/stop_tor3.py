import os
os.popen("ps aux | grep 'tor3.py' | awk '{print $2}' | xargs kill")
