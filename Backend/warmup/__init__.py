import datetime
import logging

import azure.functions as func

import requests
import os

def main(mytimer: func.TimerRequest) -> None:
    logging.info('Python timer trigger function run')

    # url = os.environ['BASE_URL'] + "/api/getplate"

    # scriptpath = os.path.abspath(__file__)
    # scriptdir = os.path.dirname(scriptpath)
    # sample_path = os.path.join(scriptdir, 'sample.jpg')
    # try:
    #     response = requests.post(url, data=open(sample_path, 'rb'), timeout=5) 
    #     logging.info('Response from getplate: ' + response.text)
    # except:
    #     logging.info('Request to getplate failed')