import numpy as np
import matplotlib.pyplot as plt
import time


services = []
with open("result_services.txt") as f: 
     for line in f:
          splitted = line.split(" ")
          val = splitted[len(splitted)-1]
          if val.endswith("\n"): val = val[0:len(val)-1]
          val = int(val)
          services.append(val)

ind = np.arange(len(services))
width = 0.35
p1 = plt.bar(ind, services, width)

plt.ylabel('Requests')
plt.title('The amount of requests that handel each service of Load Balancer')
plt.xticks(ind, ('S1', 'S2', 'S3', 'S4'))
plt.show()


programPause = raw_input("Press the <ENTER> key to continue...")
