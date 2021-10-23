#
# GridCal Tutorials
# Machine Learning example
#
# (c) Santiago Peñate-Vera, 2021

import os
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LinearRegression
import numpy as np
from matplotlib import pyplot as plt
import GridCal.Engine as gce


def train_ml(circuit, options):
    """
    Train "machine learning" devices with a clustering power flow execution
    :param circuit: GridCal MultiCircuit object
    :param options: GridCal PowerFlowOptions object
    :return:
    """

    driver = gce.TimeSeriesClustering(grid=circuit, options=options, cluster_number=100)
    driver.run()

    voltage_model = KNeighborsRegressor(n_neighbors=4, leaf_size=10)
    flow_model = LinearRegression()

    voltage_model.fit(X=driver.results.S.real,
                      y=np.abs(driver.results.voltage))

    flow_model.fit(X=driver.results.S.real,
                   y=driver.results.Sf.real)

    return voltage_model, flow_model


def predict_ml(circuit, voltage_model, flow_model):
    """
    Predict voltage module and branch real flow
    :param circuit: GridCal MultiCircuit object
    :param voltage_model: Voltage prediction artifact
    :param flow_model: branch flow prediction artifact
    :return: volatge prediction series, flow prediction series
    """

    # compile the circuit and predict
    nc = gce.compile_time_circuit(circuit)
    Pbus = nc.get_injections(normalize=False).real.T

    # predict voltage
    voltage_prediction = voltage_model.predict(Pbus)

    # predict branch power
    flow_prediction = flow_model.predict(Pbus)

    return voltage_prediction, flow_prediction


def plot(real, predicted, title):
    """
    Plot results
    :param real: Realistic results
    :param predicted: Predicted results using ML
    :param title: Title of the plot
    """
    fig = plt.figure(figsize=(12, 8))
    ax1 = fig.add_subplot(221)
    ax1.set_title('Newton-Raphson')
    ax1.plot(real)

    ax2 = fig.add_subplot(222)
    ax2.set_title('ML prediction')
    ax2.plot(predicted)

    ax3 = fig.add_subplot(223)
    ax3.set_title('Difference')
    diff = real - predicted
    ax3.plot(diff)

    ax4 = fig.add_subplot(224)
    ax4.set_title('Error (%)')
    perc = diff / real * 100.0
    y = np.zeros_like(perc)
    for i in range(y.shape[1]):
        y[:, i] = np.sort(perc[:, i])
    x = np.arange(len(y)) / len(y)
    ax4.plot(x, y)

    fig.suptitle(title, fontsize=20)

    return fig


if __name__ == '__main__':
    plt.style.use('fivethirtyeight')
    fname = os.path.join('..', 'data', 'IEEE39_1W.gridcal')

    # open the file
    main_circuit = gce.FileOpen(fname).open()

    # declare power flow options
    pf_options_ = gce.PowerFlowOptions(solver_type=gce.SolverType.NR)

    # train and predict
    print('Running ML Training and Prediction...')
    model_voltage, model_flow = train_ml(main_circuit, pf_options_)
    voltage_pred, flow_pred = predict_ml(main_circuit, model_voltage, model_flow)

    print('Running Time Series with Newton-Raphson...')
    ts_driver = gce.TimeSeries(grid=main_circuit, options=pf_options_)
    ts_driver.run()

    print('Plotting...')
    fig1 = plot(ts_driver.results.Sf.real, flow_pred, 'Branch power')
    fig2 = plot(np.abs(ts_driver.results.voltage), voltage_pred, 'Voltage module')

    plt.show()
