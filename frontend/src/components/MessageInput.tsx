import { FormEvent, useState } from "react";

interface Props {
  disabled?: boolean;
  onSend: (content: string) => Promise<void>;
}

export function MessageInput({ disabled, onSend }: Props) {
  const [value, setValue] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = value.trim();
    if (!text || disabled) {
      return;
    }
    setValue("");
    await onSend(text);
  }

  return (
    <form onSubmit={submit} className="message-input">
      <input
        type="text"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Type a message..."
        disabled={disabled}
      />
      <button type="submit" disabled={disabled}>
        Send
      </button>
    </form>
  );
}

