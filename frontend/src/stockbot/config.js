import { createChatBotMessage } from 'react-chatbot-kit';

const botName = 'StockBot';
const config = {
  initialMessages: [createChatBotMessage(`Hi! I'm ${botName}`)],
  botName: botName,
};

export default config;