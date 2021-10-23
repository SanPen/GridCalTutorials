#
# GridCal Tutorials
# real time example - client
#
# (c) Santiago Peñate-Vera, 2021

import requests
import time
import random

main_url = 'http://localhost:3000'

# Get the available grids
api_url = main_url + "/availableGrids"
response = requests.get(api_url)
available_grids = response.json()

# get the available loads
api_url = main_url + "/loads?file_name=" + available_grids[0]
response = requests.get(api_url)
loads = response.json()
print(loads)


api_url = main_url + "/powerFlow?file_name=" + available_grids[0]
delta = 200  # max range of active power to modify per each load
while True:

    # modify the loads
    for load in loads:
        load['P'] += -(0.5 * delta) + random.random() * delta  # vary +- delta/2 MW

    # run power flow
    response = requests.post(api_url, json=loads)
    power_flow = response.json()
    print(power_flow)
    time.sleep(1)



