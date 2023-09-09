import { useState } from 'react'
import './App.css'
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import axios from "axios";
import { MainContainer, ChatContainer, MessageList, Message, MessageInput, TypingIndicator } from '@chatscope/chat-ui-kit-react';


// "Explain things like you would to a 10 year old learning how to code."
const systemMessage = { //  Explain things like you're talking to a software professional with 5 years of experience.
  "role": "system", "content": "Explain things like you're talking to a software professional with 2 years of experience."
}

function App() {
  const [messages, setMessages] = useState([
    {
      message: "Hello, I'm Jarvis StockBot!",
      sentTime: "just now",
      sender: "JarvisStockbot"
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = async (message) => {
    const newMessage = {
      message,
      direction: 'outgoing',
      sender: "user"
    };

    const newMessages = [...messages, newMessage];

    setMessages(newMessages);

    // Initial system message to determine JarvisStockbot functionality
    // How it responds, how it talks, etc.
    setIsTyping(true);
    await processMessageToJarvisStockbot(newMessages);
  };

  async function processMessageToJarvisStockbot(chatMessages) { // messages is an array of messages
    // Format messages for JarvisStockbot API
    // API is expecting objects in format of { role: "user" or "assistant", "content": "message here"}
    // So we need to reformat

    let apiMessages = chatMessages.map((messageObject) => {
      let role = "";
      if (messageObject.sender === "user") {
        role = "assistant";
      } else {
        role = "assistant2";
      }
      return { role: role, content: messageObject.message }
    });

    const message= apiMessages[apiMessages.length - 1]


    // Get the request body set up with the model we plan to use
    // and the messages which we formatted above. We add a system message in the front to'
    // determine how we want JarvisStockbot to act. 
    const apiRequestBody = {
      "model": "gpt-3.5-turbo",
      "messages": [  
        message // The messages from our chat with JarvisStockbot
      ]
    }

    axios.post("http://localhost:5001/jarvis/openai",
      apiRequestBody
    ).then((data) => {
      return data.data;
    }).then((data) => {
      console.log(data);
      setMessages([...chatMessages, {
        message: data.chart,
        sender: "JarvisStockbot"
      }]);
      setIsTyping(false);
    }).catch(error => {
      setMessages([...chatMessages, {
        message: "Currently cant serve your request please try later!",
        sender: "JarvisStockbot"
      }])
      console.log(error);
    });;
  }

  return (
    <div className="App">
      <div style={{ position: "relative", height: "800px", width: "700px" }}>
        <MainContainer>
          <ChatContainer>
            <MessageList
              scrollBehavior="smooth"
              typingIndicator={isTyping ? <TypingIndicator content="typing" /> : null}
            >
              {messages.map((message, i) => {


                // console.log(message)
                // return <div className='message'>{
                //   message.sender === "JarvisStockbot" ?
                //     <img src='src\assets\bot.png'></img> : <img src='src\assets\user.png'></img>}
                //   <Message key={i} model={message} /></div>

                console.log(message)
                return <>{message.sender === "JarvisStockbot" ?
                  <div className='message'>
                    <img src='src\assets\bot.png'></img>
                    <img src={`data:image/png;base64,${message.message}`}/></div> : <div className='message-user'>
                    <Message key={i} model={message} />
                    <img src='src\assets\user.png'></img>
                  </div>}</>


              })}
            </MessageList>
            <MessageInput placeholder="Type message here" onSend={handleSend} />
          </ChatContainer>
        </MainContainer>
      </div>
    </div>
  )
}

export default App
