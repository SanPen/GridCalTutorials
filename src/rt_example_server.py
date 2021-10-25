#
# GridCal Tutorials
# real time example - server
#
# (c) Santiago Peñate-Vera, 2021
import os
import uvicorn
import numpy as np
from fastapi import Body, FastAPI, Request, Response
import GridCal.Engine as gce

app = FastAPI()

__grids_dir__ = os.path.join('..', 'data')


@app.get('/')
def home():
    return 'hey!'


@app.get('/availableGrids')
def available_grids():
    """
    Get the filenames of the available grids
    """
    file_names = next(os.walk(__grids_dir__), (None, None, []))[2]
    return file_names


@app.get('/loads', status_code=200)
def get_loads(file_name, request: Request):
    """
    Get the loads data
    :param file_name: grid file name
    :return: loads' data
    """
    path = os.path.join(__grids_dir__, file_name)
    request.app.circuit = gce.FileOpen(path).open()
    loads = request.app.circuit.get_loads()
    data = [{'id': elm.idtag, 'name': elm.name, 'P': elm.P, 'Q': elm.Q} for elm in loads]
    return data


@app.post('/powerFlow', status_code=200)
async def power_flow(file_name, request: Request):
    """
    Run power flow
    :param file_name: grid file name
    :param request: Request data
    :return: Power flow results
    """
    data = await request.json()

    # path = os.path.join(__grids_dir__, file_name)
    # circuit = gce.FileOpen(path).open()

    loads = request.app.circuit.get_loads()

    if len(loads) == len(data):

        # copy the incoming data to the load objects
        for datum, load in zip(data, loads):
            load.P = datum['P']
            load.Q = datum['Q']

    driver = gce.PowerFlowDriver(grid=request.app.circuit,
                                 options=gce.PowerFlowOptions())
    driver.run()

    return {'converged': driver.results.converged.tolist(),
            'voltage': np.abs(driver.results.voltage).tolist(),
            'flows': driver.results.Sf.real.tolist()}


if __name__ == "__main__":
  uvicorn.run(app, host='127.0.0.1', port=3000, debug=True)
