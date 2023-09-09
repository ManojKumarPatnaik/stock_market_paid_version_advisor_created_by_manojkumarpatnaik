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

    const apiRequestBody = {
      model: "gpt-3.5-turbo",
      messages: [message],
    };

    axios
      .post("http://localhost:5000/jarvis/openai", apiRequestBody)
      .then((data) => {
        return data.data;
      })
      .then((data) => {
        setMessages([
          ...chatMessages,
          {
            message: data.chart,
            sender: "JarvisStockbot",
          },
        ]);
        setIsTyping(false);
      })
      .catch((error) => {
        setMessages([
          ...chatMessages,
          {
            message: "Currently cant serve your request please try later!",
            sender: "JarvisStockbot",
          },
        ]);
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
                        {base64regex.test(message.message) ? (
                          <img
                            src={`data:image/png;base64,${message.message}`}
                          />
                        ) : (
                          <>
                            <img src="src\assets\bot.png"></img>
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
