from flask import Flask, jsonify
import boto3
from boto3.dynamodb.conditions import Key
from flask_cors import CORS
from decimal import Decimal
import json
import os

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

session = boto3.Session(
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ.get('AWS_REGION', 'us-east-2')
)
dynamodb = session.resource('dynamodb')
table = dynamodb.Table('CompressorTelemetry')

def decimal_fix(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

@app.route('/readings')
def readings():
    result = table.scan()
    items = sorted(result['Items'], key=lambda x: float(x['unix_ts']))
    items = items[-200:]  # last 200 only
    return app.response_class(
        json.dumps(items, default=decimal_fix),
        mimetype='application/json'
    )

@app.route('/faults')
def faults():
    result = table.scan()
    items = sorted(result['Items'], key=lambda x: float(x['unix_ts']))
    faults = [i for i in items if i.get('fault_type') != 'NONE']
    faults = faults[-20:]
    faults = list(reversed(faults))
    return app.response_class(
        json.dumps(faults, default=decimal_fix),
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run(port=5050)