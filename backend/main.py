from collections import defaultdict

import requests
import json
import configparser
import os
from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Load configuration from file
config = configparser.ConfigParser()
config.read('config.ini')

# Set environment variables from configuration, with default values
os.environ.setdefault('URI', config.get('API', 'URI', fallback='http://default-uri.com'))
os.environ.setdefault('API_KEY', config.get('API', 'API_KEY', fallback='default-api-key'))
os.environ.setdefault('KEY_VALUE', config.get('API', 'KEY_VALUE', fallback='default-key-value'))



def getResponseFromOpenAI(input_prompt):
    # reading from frontend ui and once user click on submit button
    uri = os.getenv("URI")
    header = {os.getenv("API_KEY"): os.getenv("KEY_VALUE")}
    with open('resources/input.json', 'r') as f:
        json_input = json.load(f)
    raw_input_data =  "Can you extract the symbol, start_date, and end_date and store the values in a dictionary? " \
                     "Symbol should be in uppercase and start_date, end_date should be in yyyy-mm-DD format. " \
                     "Please see below text for reference.\n" + input_prompt
    json_input["messages"][0]["content"] = raw_input_data

    try:
        response = requests.post(uri, headers=header, json=json_input)
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]
        # print(message)
        symbol = jsonify(str(message["content"])).response
        print(symbol)
        # start_date = message["content"]['start_date']
        # end_date = message["content"]['end_date']
        # # Call the get_Data() method with the extracted values
        # get_Data(symbol, start_date, end_date)
        # Call the get_Data() method with the extracted values
        get_Data_From_YFinance("ASIANPAINT.NS", "2023-05-22", "2023-09-07")
        print('Response text:\n', message["content"])
    except requests.exceptions.HTTPError as ex:
        print('Error response status code:', ex.response.status_code)
        print('Error response text:', ex.response.text)


app = Flask(__name__)

def getResponseFromOpenAI2(data):
    # reading from frontend ui and once user click on submit button
    uri = os.getenv("URI")
    header = {os.getenv("API_KEY"): os.getenv("KEY_VALUE")}
    with open('resources/input.json', 'r') as f:
        json_input = json.load(f)
    raw_input_data =  "Can you suggest when to buy and hold the stock based on the chart below, and provide some short and long-term use cases?\n" + data
    json_input["messages"][0]["content"] = raw_input_data
    try:
        response = requests.post(uri, headers=header, json=json_input)
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]
        print(message)
        sma_21 = data['Close'].rolling(window=21).mean()
        current_price = data['Close'][-1]
        current_sma21 = sma_21[-1]
        if current_price > current_sma21:
            suggestion = "The current price is above the 21-day SMA. This suggests a bullish trend, and it may be a good time to buy the stock."
        else:
            suggestion = "The current price is below the 21-day SMA. This suggests a bearish trend, and it may be a good idea to wait before buying the stock."
        short_term_use_case = "One short-term use case for this stock is to trade it based on technical analysis, using indicators such as moving averages and momentum oscillators."
        long_term_use_case = "One long-term use case for this stock is to hold it as part of a diversified portfolio and take advantage of any dividend payments and potential price appreciation over time."

        # Format the suggestions and return the response
        response_text = f"{suggestion}\n\n{short_term_use_case}\n\n{long_term_use_case}"
        print('Response text:\n', response_text)
        return response_text
    except requests.exceptions.HTTPError as ex:
        print('Error response status code:', ex.response.status_code)
        print('Error response text:', ex.response.text)
def getResponseFromOpenAI1(input_prompt):
    # reading from frontend ui and once user click on submit button
    uri = os.getenv("URI")
    header = {os.getenv("API_KEY"): os.getenv("KEY_VALUE")}
    with open('resources/input.json', 'r') as f:
        json_input = json.load(f)
    raw_input_data =  "Can you give the statistics analysis like mean, sma for 21 days from this table?\n" + input_prompt
    json_input["messages"][0]["content"] = raw_input_data
    try:
        response = requests.post(uri, headers=header, json=json_input)
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]
        print('Response text:\n', message["content"])
    except requests.exceptions.HTTPError as ex:
        print('Error response status code:', ex.response.status_code)
        print('Error response text:', ex.response.text)


@app.route('/jarvis/openai', methods=['POST'])
def compare():
    data = request.get_json()
    # retrieve json data from request
    # extract prompt string from data
    input_prompt = data["messages"][0]["content"]
    # call example method with input prompt
    getResponseFromOpenAI(input_prompt)
    # return response

    return jsonify({"status": "success"})


def get_Data_From_YFinance(symbol, start_date, end_date):
    # symbol = "SBIN.NS"
    # start_date = "2013-01-01"
    # end_date = "2023-01-31"

    # Retrieve the historical data for the specified symbol and date range
    data = yf.download(symbol, start=start_date, end=end_date)

    # Print the data
    print("printing yfinance data from nse\n")
    print(data)
    # getResponseFromOpenAI2(data)



#  drawing a graph with price and date with SMA for 500 days on close price
def draw_graph(symbol,data):

    # Compute the moving average with a 500-day window
    window_size = 500
    data[f"SMA_{window_size}"] = data['Close'].rolling(window=window_size).mean()

    # Plot the graph
    plt.plot(data.index, data['Close'], label='Closing Price')
    plt.plot(data.index, data[f"SMA_{window_size}"], label=f"{window_size}-day SMA")
    plt.plot(data.index, data[f"SMA_{window_size}"], label=f"{window_size}-day SMA")
    plt.xlabel('Date')
    plt.ylabel('Volume in cr')
    plt.title(f"{symbol} Price and {window_size}-day Simple Moving Average")
    plt.legend()
    plt.show()

#  drawing a graph with price and date with SMA for 500 days on volume
def draw_graph1(symbol,data):

    # Compute the moving average with a 500-day window
    window_size = 500
    data[f"SMA_{window_size}"] = data['Volume'].rolling(window=window_size).mean()

    # Plot the graph
    fig, axs = plt.subplots(2, sharex=True)
    fig.suptitle(f"{symbol.upper()} Price and {window_size}-day Simple Moving Average")

    # Plot price and SMA on price
    axs[0].plot(data.index, data['Close'], label='Closing Price')
    axs[0].plot(data.index, data[f"SMA_{window_size}"], label=f"{window_size}-day SMA")
    axs[0].set_ylabel('Price')

    # Plot volume and SMA on volume
    axs[1].plot(data.index, data['Volume'], label='Volume')
    axs[1].plot(data.index, data[f"SMA_{window_size}"], label=f"{window_size}-day SMA")
    axs[1].set_xlabel('Date')
    axs[1].set_ylabel('Volume')
    axs[1].legend()

    plt.show()

#  drawing a graph with volume and date with plotting of SMA for 500 days on price and 100 days on volume
def draw_graph2(symbol,data):


    # Compute the moving averages with a 500-day window
    price_window_size = 500
    volume_window_size = 100
    data[f"SMA_{price_window_size}"] = data['Close'].rolling(window=price_window_size).mean()
    data[f"SMA_{volume_window_size}_Vol"] = data['Volume'].rolling(window=volume_window_size).mean()

    # Plot the graph
    fig, ax1 = plt.subplots()

    # Plot price and SMA on price
    ax1.plot(data.index, data['Close'], label='Price')
    ax1.plot(data.index, data[f"SMA_{price_window_size}"], label=f"{price_window_size}-day Price SMA")
    ax1.set_ylabel('Price')

    # Create secondary y-axis for volume plot
    ax2 = ax1.twinx()

    # Plot volume and SMA on volume
    ax2.plot(data.index, data['Volume'], label='Volume', alpha=0.5)
    ax2.plot(data.index, data[f"SMA_{volume_window_size}_Vol"], label=f"{volume_window_size}-day Volume SMA")
    ax2.set_ylabel('Volume')

    # Add legend
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.title(f"{symbol.upper()} Price and Volume with Simple Moving Averages")
    plt.show()

def draw_graph4(symbol, data):
    # Compute the moving average with a 500-day window
    window_size = 500
    data[f"SMA_{window_size}"] = data['Close'].rolling(window=window_size).mean()

    # Calculate VWAP
    data['TP'] = (data['High'] + data['Low'] + data['Close']) / 3
    data['TPV'] = data['TP'] * data['Volume']
    data['Cumulative TPV'] = data['TPV'].cumsum()
    data['Cumulative Volume'] = data['Volume'].cumsum()
    data['VWAP'] = data['Cumulative TPV'] / data['Cumulative Volume']

    # Plot the graph
    fig, axs = plt.subplots(2, 2, sharex=True, figsize=(10, 8))

    # Plot price and SMA on price
    axs[0, 0].plot(data.index, data['Close'], label='Closing Price')
    axs[0, 0].plot(data.index, data[f"SMA_{window_size}"], label=f"{window_size}-day SMA")
    axs[0, 0].set_ylabel('Price')

    # Plot VWAP
    axs[0, 1].plot(data.index, data['VWAP'], label='VWAP')
    axs[0, 1].set_ylabel('Volume-Weighted Average Price')

    # Plot LTP
    axs[1, 0].plot(data.index, data['Close'], label='Closing Price')
    axs[1, 0].plot(data.index, data['High'], label='High Price')
    axs[1, 0].plot(data.index, data['Low'], label='Low Price')
    axs[1, 0].set_ylabel('Price')

    # Plot number of trades
    axs[1, 1].plot(data.index, data['Volume'], label='Volume')
    axs[1, 1].plot(data.index, data['Volume'].rolling(window=window_size).mean(), label=f"{window_size}-day Volume SMA")
    axs[1, 1].set_xlabel('Date')
    axs[1, 1].set_ylabel('Number of Trades')

    # Add legends
    axs[0, 0].legend(loc='upper left')
    axs[0, 1].legend(loc='upper left')
    axs[1, 0].legend(loc='upper left')
    axs[1, 1].legend(loc='upper left')

    plt.suptitle(f"{symbol.upper()} Price, VWAP, LTP, and Number of Trades")
    plt.show()

def draw_graph5(symbol, data):
    # Compute the moving average with a 500-day window
    window_size = 500
    data[f"SMA_{window_size}"] = data['Close'].rolling(window=window_size).mean()

    # Plot the graph
    fig, ax1 = plt.subplots()

    # Create secondary y-axis for volume plot
    ax2 = ax1.twinx()

    # Plot price and SMA on price
    ax1.plot(data.index, data['Close'], label='Closing Price')
    ax1.plot(data.index, data[f"SMA_{window_size}"], label=f"{window_size}-day SMA")
    ax1.set_ylabel('Price')

    # Plot number of trades
    ax2.plot(data.index, data['Volume'], label='Number of Trades', alpha=0.5)
    ax2.plot(data.index, data['Volume'].rolling(window=window_size).mean(), label=f"{window_size}-day Volume SMA")
    ax2.set_ylabel('Number of Trades')

    # Add legends
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.title(f"{symbol.upper()} Price and Number of Trades with Simple Moving Average")
    plt.show()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
