import os
import logging
import json
import numpy
import joblib


def init():
    """
    init function 
    """
    # load model
    global model
    
    model_path = os.environ['AZUREML_MODEL_DIR'] + "/model/random_forest_best.pkl"
    model = joblib.load(model_path)

    logging.info("Initialization complete")


def run(raw_data):
    """
    inference run function
    """
    logging.info("Request Received")

    data = json.loads(raw_data)["data"]

    input_features = []
    for item in data:
        single_user_input = [
           int(item['AccountWeeks']),
            int(item['ContractRenewal']),
            int(item['DataPlan']),
            float(item['DataUsage']),
            int(item['CustServCalls']),
            float(item['DayMins']),
            int(item['DayCalls']),
            float(item['MonthlyCharge']),
            float(item['OverageFee']),
            float(item['RoamMins']),
            float(item['AvgCallDuration']),
            float(item['CostPerUsage'])
        ]
        input_features.append(single_user_input)
    input_features = numpy.array(input_features)
    result = model.predict(input_features)

    logging.info("Request Processed")

    return {
        "predictedOutcomes": result.tolist(),
        "inputFeatures": data
    }
