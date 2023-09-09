// in ActionProvider.jsx
import React from 'react';
import axios from "axios";

const ActionProvider = ({ createChatBotMessage, setState, children }) => {
  const handleHello = (message) => {
     axios.post('http://localhost:3001/api',{
      message
  }).then(response=>{
      const botMessage = createChatBotMessage(response.data);
      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, botMessage],
      }));
     }).catch(error => {
      console.log(error);
    });
  };

  // Put the handleHello function in the actions object to pass to the MessageParser
  return (
    <div>
      {React.Children.map(children, (child) => {
        return React.cloneElement(child, {
          actions: {
            handleHello,
          },
        });
      })}
    </div>
  );
};

export default ActionProvider;