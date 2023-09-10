from collections import defaultdict

import requests
import json
import configparser
import os
from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import base64
from flask_cors import CORS, cross_origin

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
    raw_data = input_prompt+'''\n
    Please provide the following information using above text 
    ticker_id: find the ticker_id the stock symbol for the security of interest, entered in uppercase (e.g., AAPL for 
    Apple Inc.) from yfinance package API check if it listed in NSE then append .NS to ticker_id (e.g., SBIN for SBI output SBIN.NS)
    Start_date: The start date of the data range, in yyyy-mm-DD format
    End_date: The end date of the data range, in yyyy-mm-DD format
    Moving_average_days: The number of days to use for the moving average calculation, should be an integer format only
    before the word 'days'
    Balance_sheet: Indicate 'true' or 'false' if above text asking to extract balance sheet data
    Actions: Indicate 'true' or 'false'  if above text asking to extract actions data
    Financials: Indicate 'true' or 'false'  if above text asking to extract financial statements data
    Capital_gains: Indicate 'true' or 'false' if above text asking to extract capital gains data
    Cash_flow: Indicate 'true' or 'false'  if above text asking to extract cash flow data
    Income_statement: Indicate 'true' or 'false'  if above text asking to extract income statement data
    Please_store the requested information in the json format with all keys should be in lowercase'''

    json_input["messages"][0]["content"] = raw_data

    try:
        response = requests.post(uri, headers=header, json=json_input)
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]
        # print(message)
        content_Json=json.loads(message["content"])
        print(content_Json)
        ticker=content_Json['ticker_id']
        # print(ticker)
        balance_sheet=content_Json['balance_sheet']
        # print(balance_sheet)

        start_date = content_Json['start_date']
        # print(start_date)
        end_date = content_Json['end_date']
        # print(end_date)
        no_of_days = content_Json['moving_average_days']
        # print(no_of_days)
        if(balance_sheet):
            print(yf.Ticker(ticker).balance_sheet)
        Actions = content_Json['actions']
        if(Actions):
            print(yf.Ticker(ticker).actions)
        Financials = content_Json['financials']
        if (Financials):
            print(yf.Ticker(ticker).financials)
        Capital_gains = content_Json['capital_gains']
        if (Capital_gains):
            print(yf.Ticker(ticker).capital_gains)
        Cash_flow = content_Json['capital_gains']
        if (Cash_flow):
            print(yf.Ticker(ticker).cashflow)
        Income_statement = content_Json['income_statement']
        if (Income_statement):
            print(yf.Ticker(ticker).incomestmt)
        print(yf.Ticker(ticker).news)
        print(yf.Ticker(ticker).history)
        data, chartdata, advice = get_Data_From_YFinance(ticker, start_date, end_date,no_of_days)
        print('Response text:\n', message["content"])
        return chartdata,advice
    except requests.exceptions.HTTPError as ex:
        print('Error response status code:', ex.response.status_code)
        print('Error response text:', ex.response.text)


app = Flask(__name__)
CORS(app, support_credentials=True)

def getFromOpenAI_21_days_sma(data):
    # reading from frontend ui and once user click on submit button
    uri = os.getenv("URI")
    header = {os.getenv("API_KEY"): os.getenv("KEY_VALUE")}
    with open('resources/input.json', 'r') as f:
        json_input = json.load(f)
    raw_input_data =  "Can you suggest when to buy and hold the stock based on the data below, and provide some short and long-term use cases?\n" + data
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
def getStockAdviceFromOpenAI(dataFrame):
    # reading from frontend ui and once user click on submit button
    uri = os.getenv("URI")
    header = {os.getenv("API_KEY"): os.getenv("KEY_VALUE")}
    with open('resources/input.json', 'r') as f:
        json_input = json.load(f)
    raw_input_data =  "You're the expert stock advisor and having 30 years of experience in stock selection and Investments plans" \
                      "give below dataframe can you analyze the stock performance over the period and explain how it behave in every quater? " \
                      "and when to buy this stock? how long should I hold means suggestion for long or short" \
                      " term investment plan and don't give any code snippets?\n" + str(dataFrame)
    json_input["messages"][0]["content"] = raw_input_data
    try:
        response = requests.post(uri, headers=header, json=json_input)
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]

        print('Response text:\n', message["content"])
        return message['content']
    except requests.exceptions.HTTPError as ex:
        print('Error response status code:', ex.response.status_code)
        print('Error response text:', ex.response.text)


@app.route('/jarvis/openai', methods=['POST'])
@cross_origin(supports_credentials=True)
def compare():
    data = request.get_json()
    # retrieve json data from request
    # extract prompt string from data
    input_prompt = data["messages"][0]["content"]
    # call example method with input prompt
    imgdata , message= getResponseFromOpenAI(input_prompt)
    # return response

    return jsonify({"status": "success", "chart": imgdata, "message":message})


def get_Data_From_YFinance(symbol, start_date, end_date,no_of_days):
    # Retrieve the historical data for the specified symbol and date range
    data = yf.download(symbol, start=start_date, end=end_date)
    # Calculate the  average LTP
    data['avg_LTP'] = (data['Open'] + data['High'] + data['Low'] + data['Close']) / 4

    # Select the columns of interest
    columns_of_interest = ['Open', 'Close',  'Volume', 'avg_LTP']
    data = data[columns_of_interest]


    # Print the data
    print("Printing yfinance data from NSE\n")
    print(data)

    quarter_data = data.resample('Q').agg({'Volume': 'mean', 'avg_LTP': 'mean'})


    # Calculate the number of trades transacted per day
    num_trades = data["Volume"] // no_of_days

    # Add a new column to the quarter_data dataframe that calculates the number of trades transacted per day
    quarter_data["num_trades"] = num_trades



    print(quarter_data)
    message = getStockAdviceFromOpenAI(quarter_data)
    imgdata = draw_graph2(symbol,data,no_of_days)
    return data, imgdata, message



#  drawing a graph with price and date with SMA for 500 days on close price
def draw_graph(symbol,data,no_of_days):

    # Compute the moving average with a 500-day window
    window_size = no_of_days
    data[f"SMA_{window_size}"] = data['Close'].rolling(window=window_size).mean()
    print(data[f"SMA_{window_size}"] )

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
def draw_graph1(symbol,data,no_of_days):

    # Compute the moving average with a 500-day window
    window_size = no_of_days
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

#  drawing a graph with volume and date with plotting of SMA for no_of_days on price and on volume
def draw_graph2(symbol,data,no_of_days):


    # Compute the moving averages with a no_of_days window
    price_window_size = int(no_of_days)
    volume_window_size = int(no_of_days)
    data[f"SMA_{price_window_size}"] = data['Close'].rolling(window=price_window_size,min_periods=price_window_size).mean()
    data[f"SMA_{volume_window_size}_Vol"] = data['Volume'].rolling(window=volume_window_size,min_periods=volume_window_size).mean()

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
    # Save the graph as an image file	
    image_file = 'graph.png'
    plt.savefig(image_file)
    plt.close()  # Close the plot to release resources	
    # Convert the saved image to base64	
    with open(image_file, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode()
    return base64_image

def draw_graph4(symbol, data,no_of_days):
    # Compute the moving average with a 500-day window
    window_size = no_of_days
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

def draw_graph5(symbol, data,no_of_days):
    # Compute the moving average with a 500-day window
    window_size = no_of_days
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


def getResponseFromOpenAI26(data,no_of_days):
    # reading from frontend ui and once user click on submit button
    uri = os.getenv("URI")
    header = {os.getenv("API_KEY"): os.getenv("KEY_VALUE")}
    with open('resources/input.json', 'r') as f:
        json_input = json.load(f)
    raw_input_data =  "Can you suggest when to buy and hold the stock based on the data below, and provide some short and long-term use cases?\n"
    json_input["messages"][0]["content"] = raw_input_data
    try:
        response = requests.post(uri, headers=header, json=json_input)
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]
        print(message)

        # Analyze the data and generate suggestions
        sma_21 = data['Close'].rolling(window=no_of_days).mean()
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
