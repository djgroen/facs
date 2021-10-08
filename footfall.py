import facs.readers.read_age_csv as r
import sys
import numpy as np

ages = r.read_age_csv(sys.argv[1])

age = range(0, len(ages))

number_of_visits = int(sys.argv[2])

duration = 60

times = [9,10,11,12,13,14,15,16,17,18,19]

time_probabilities = np.array([1,2,3,4,4,4,4,4,3,2,1])
time_weights = time_probabilities / np.sum(time_probabilities)

print("index,age [years],time [H],duration [minutes]")

for i in range(0, number_of_visits):
  print("{},{},{},{}".format(i,np.random.choice(age, p=ages), np.random.choice(times, p=time_weights),int(np.random.poisson(duration))))
