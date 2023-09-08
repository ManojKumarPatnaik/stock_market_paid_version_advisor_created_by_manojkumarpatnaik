

import requests
import json
import os
# from nsepy import get_history
# from datetime import date
# import pandas

def example(input_prompt):
    # URI and header

    uri = os.getenv("URI")
    header = {os.getenv("API_KEY"):os.getenv("KEY_VALUE")}
    # reading from frontend ui and once user click on submit button
    with open('resources/input.json', 'r') as f:
        json_input = json.load(f)
    json_input["messages"][0]["content"] = input_prompt
    # Send POST request


    # data = get_history(symbol="SBIN", start=date(2015, 1, 1), end=date(2015, 1, 31))
    # data[['Close']].plot()


    try:
        response = requests.post(uri, headers=header, json=json_input)
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]
        print('Response text:\n', message["content"])
    except requests.exceptions.HTTPError as ex:
        print('Error response status code:', ex.response.status_code)
        print('Error response text:', ex.response.text)

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/jarvis/openai', methods=['POST'])
def compare():
    data = request.get_json()
    # retrieve json data from request
    # extract prompt string from data
    input_prompt = data["messages"][0]["content"]
    # call example method with input prompt
    example(input_prompt)
    # return response

    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



