import time
from datetime import datetime
#dt = datetime.now()
milliseconds = int(round(datetime.now().timestamp() * 1000))
print(milliseconds)