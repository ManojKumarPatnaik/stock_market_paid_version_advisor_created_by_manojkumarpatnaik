import React from "react";
import Chatbot from "react-chatbot-kit";

import config from "./stockbot/config";
import MessageParser from "./stockbot/message-parser";
import ActionProvider from "./stockbot/action-provider";

function App() {
  return (
    <div className="App">
      <Chatbot
        config={config}
        messageParser={MessageParser}
        actionProvider={ActionProvider}
      />
    </div>
  );
}

export default App;