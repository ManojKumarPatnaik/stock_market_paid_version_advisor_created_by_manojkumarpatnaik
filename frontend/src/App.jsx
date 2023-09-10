import React from "react";

import { useState } from "react";
import "./App.css";
import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import axios from "axios";
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
} from "@chatscope/chat-ui-kit-react";

function App() {
  const base64regex = /^([0-9a-zA-Z+/]{4})*(([0-9a-zA-Z+/]{2}==)|([0-9a-zA-Z+/]{3}=))?$/;
  const [messages, setMessages] = useState([
    {
      message: "Hello, I'm Jarvis StockBot!",
      sentTime: "just now",
      sender: "JarvisStockbot",
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = async (message) => {
    const newMessage = {
      message,
      direction: "outgoing",
      sender: "user",
    };

    const newMessages = [...messages, newMessage];

    setMessages(newMessages);

    setIsTyping(true);
    await processMessageToJarvisStockbot(newMessages);
  };

  async function processMessageToJarvisStockbot(chatMessages) {
    let apiMessages = chatMessages.map((messageObject) => {
      let role = "";
      if (messageObject.sender === "user") {
        role = "assistant";
      } else {
        role = "assistant2";
      }
      return { role: role, content: messageObject.message };
    });

    const message = apiMessages[apiMessages.length - 1];

    const updatedMessage = {
      role: "assistant",
      content:
        message.content +
        `Please provide the following information in json format using above text 
        ticker_id: find the ticker_id the stock symbol for the security of interest, entered in uppercase (e.g., AAPL for 
        Apple Inc.) from yfinance package API check if it listed in NSE then append .NS to ticker_id (e.g., SBIN for SBI output SBIN.NS)
        Start_date: The start date of the data range, in yyyy-mm-DD format
        End_date: The end date of the data range, in yyyy-mm-DD format
        Moving_average_days: The number of days to use for the moving average calculation, should be an integer format only
        before the word 'days'
        Balance_sheet: Indicate 'true' or 'false' if above text asking to extract balance sheet data
        Actions: Indicate 'true' or 'false' if above text asking to extract actions data
        Financials: Indicate 'true' or 'false' if above text asking to extract financial statements data
        Capital_gains: Indicate 'true' or 'false' if above text asking to extract capital gains data
        Cash_flow: Indicate 'true' or 'false' if above text asking to extract cash flow data
        Income_statement: Indicate 'true' or 'false' if above text asking to extract income statement data
        Please_store the requested information in the json format with all keys should be in lowercase`,
    };

    const apiRequestBody = {
      model: "gpt-3.5-turbo",
      messages: [updatedMessage],
    };

    const response = await fetch(
      "https://aoai-engx-hack23.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2023-07-01-preview",
      {
        method: "POST",
        headers: {
          "Api-Key": "f855aa32fcf842fe84a540df1e8c7e99",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(apiRequestBody),
      }
    );

    response.json().then((res) => {
      const jsonData = JSON.parse(res.choices[0].message.content);
      console.log(jsonData);

      const pythonApiRequestBody = {
        model: "gpt-3.5-turbo",
        messages: [
          {
            role: "assistant",
            content: `Could you please give me the statistic data for ${jsonData?.ticker_id} symbol from start date as ${jsonData?.start_date} to end date as ${jsonData?.end_date} and draw a simple moving average for ${jsonData?.moving_average_days} days?`,
          },
        ],
      };
      axios
        .post("http://localhost:5000/jarvis/openai", pythonApiRequestBody)
        .then((data) => {
          return data.data;
        })
        .then((data) => {
          setMessages([
            ...chatMessages,
            {
              message: data.message,
              chart: data.chart,
              sender: "JarvisStockbot",
            },
          ]);
          setIsTyping(false);
        })
        .catch((error) => {
          setMessages([
            ...chatMessages,
            {
              message:
                "Invalid Format, please mention start date end date and symbol",
              sender: "JarvisStockbot",
            },
          ]);
          setIsTyping(false);
        });
    });
  }

  return (
    <div className="App">
      <div style={{ position: "relative", height: "800px", width: "700px" }}>
        <MainContainer>
          <ChatContainer>
            <MessageList
              scrollBehavior="smooth"
              typingIndicator={
                isTyping ? <TypingIndicator content="typing" /> : null
              }
            >
              {messages.map((message, i) => {
                return (
                  <>
                    {message.sender === "JarvisStockbot" ? (
                      <div className="message">
                        {base64regex.test(message.chart) ? (
                          <div className="response">
                            <img
                              src={`data:image/png;base64,${message.chart}`}
                            />
                            <div className="message">{message.message}</div>
                          </div>
                        ) : (
                          <>
                            <div className="message">{message.message}</div>
                          </>
                        )}
                      </div>
                    ) : (
                      <div className="message-user">
                        <Message key={i} model={message} />
                      </div>
                    )}
                  </>
                );
              })}
            </MessageList>
            <MessageInput placeholder="Type message here" onSend={handleSend} />
          </ChatContainer>
        </MainContainer>
      </div>
    </div>
  );
}

export default App;
