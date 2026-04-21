import type { Message } from "../types";

interface Props {
  messages: Message[];
}

export function MessageList({ messages }: Props) {
  return (
    <div className="message-list">
      {messages.map((message) => (
        <div key={message.id} className={`bubble bubble-${message.role}`}>
          <p>{message.content}</p>
        </div>
      ))}
      {messages.length === 0 ? <p className="muted">Start the conversation to capture lead details.</p> : null}
    </div>
  );
}

