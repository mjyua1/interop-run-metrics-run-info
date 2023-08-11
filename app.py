from flask import Flask, request
import pymongo
from main import *
from parserRunMetrics import *

app = Flask(__name__)

host = pymongo.MongoClient('itpmongodb.usc.edu', username='mjyuan', password='4578256778', authSource='mjyuan')
database = host["mjyuan"]
collection1 = database["run_info"]
collection2 = database["run_metrics"]


@app.route('/parseRunInfo', methods=['POST'])
def parseRunInfo():
    run_folder = request.json['run_folder']
    result_dict = finalOutput(run_folder)
    success_code = False
    try:
        saved = save_run_info(result_dict)
        result_dict['_id'] = str(result_dict['_id'])
        success_code = True
    except Exception as e:
        print(f"Error saving to database: {str(e)}")
    return {'success': success_code, "result": result_dict}

@app.route('/parseRunMetrics', methods=['POST'])
def parseRunMetrics():
    run_folder = request.json['run_folder']
    metrics_result = finalOutput2(run_folder)
    success_code = False
    try:
        saved2 = save_run_metrics(metrics_result)
        metrics_result['_id'] = str(metrics_result['_id'])
        success_code = True
    except Exception as e:
        print(f"Error saving to database: {str(e)}")
    return {'success': success_code, "result": metrics_result}


@app.route('/retrieveRunInfo', methods=['GET'])
def retrieveRunInfo():
    run_folder = request.args.get("run_folder")
    success_code = False
    result = {}
    try:
        success_code = True
        result = retrieve_db(run_folder)
    except Exception as e:
        print(f"Error retrieving database: {str(e)}")
    return {'success': success_code, "result": result}


@app.route('/retrieveRunMetrics', methods=['GET'])
def retrieveRunMetrics():
    run_folder = request.args.get("run_folder")
    success_code = False
    result = {}
    try:
        success_code = True
        result = retrieve_db2(run_folder)
    except Exception as e:
        print(f"Error retrieving database: {str(e)}")
    return {'success': success_code, "result": result}


def save_run_info(result_dict):
    success_code = False
    try:
        collection1.insert_one(result_dict)
        success_code = True
    except Exception as e:
        print(f"Error saving to database: {str(e)}")
    return success_code


def save_run_metrics(metrics_result):
    success_code = False
    try:
        collection2.insert_one(metrics_result)
        success_code = True
    except Exception as e:
        print(f"Error saving to database: {str(e)}")
    return success_code

def retrieve_db(run_folder):
    success_code = False
    document = {}
    sort_order = [('last_updated', pymongo.DESCENDING)]
    try:
        query = {"DATA_PATH": run_folder}
        document = collection1.find_one(query, sort=sort_order)
        document['_id'] = str(document['_id'])
        success_code = True
    except Exception as e:
        print(f"Error retrieving database: {str(e)}")
    print(document)
    return document

def retrieve_db2(run_folder):
    success_code = False
    document2 = {}
    sort_order = [('last_updated', pymongo.DESCENDING)]
    try:
        query = {"run_folder": run_folder}
        document2 = collection2.find_one(query, sort=sort_order)
        document2['_id'] = str(document2['_id'])
        success_code = True
    except Exception as e:
        print(f"Error retrieving database: {str(e)}")
    print(document2)
    return document2


if __name__ == '__main__':
    app.run(debug=True, port=8001)
