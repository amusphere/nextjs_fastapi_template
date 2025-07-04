"use client";

import { useState } from "react";
import { Textarea } from "../ui/textarea";

interface ChatInputProps {
  onSendMessage: (message: string) => Promise<void>;
  isLoading: boolean;
}

export default function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const messageToSend = message.trim();
    setMessage("");
    await onSendMessage(messageToSend);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.shiftKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-2 sm:p-4 border-t bg-white">
      <Textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="メッセージを入力してください... (Shift+Enter または Cmd+Enterで送信、Enterで改行)"
        className="min-h-[50px] sm:min-h-[60px] max-h-[100px] sm:max-h-[120px] resize-none w-full text-sm sm:text-base"
        disabled={isLoading}
      />
    </form>
  );
}
