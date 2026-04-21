import type { Message } from "../types";

interface Props {
  messages: Message[];
  isAssistantTyping?: boolean;
  assistantLabel?: string;
}

export function MessageList({ messages, isAssistantTyping = false, assistantLabel = "Assistant" }: Props) {
  return (
    <div className="message-list">
      {messages.map((message) => (
        <div key={message.id} className={`bubble bubble-${message.role}`}>
          <p>{message.content}</p>
        </div>
      ))}
      {isAssistantTyping ? (
        <div className="bubble bubble-assistant bubble-typing">
          <p>Sarah is typing...</p>
        </div>
      ) : null}
      {messages.length === 0 ? <p className="muted">Start the conversation to capture lead details.</p> : null}
    </div>
  );
}
