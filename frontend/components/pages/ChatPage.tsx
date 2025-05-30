"use client";

import { useState } from "react";
import { ChatMessage } from "@/types/Chat";
import { Button } from "@/components/components/ui/button";
import { Input } from "@/components/components/ui/input";

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;
    const prompt = input;
    setMessages((msgs) => [...msgs, { role: "user", content: prompt }]);
    setInput("");

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      const data = await res.json();
      if (res.ok) {
        setMessages((msgs) => [
          ...msgs,
          { role: "assistant", content: data.response },
        ]);
      } else {
        setMessages((msgs) => [
          ...msgs,
          { role: "assistant", content: data.message || "Error" },
        ]);
      }
    } catch {
      setMessages((msgs) => [
        ...msgs,
        { role: "assistant", content: "Error" },
      ]);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.map((m, idx) => (
          <div key={idx} className={m.role === "user" ? "text-right" : "text-left"}>
            <span className="inline-block rounded px-3 py-2 bg-muted">
              {m.content}
            </span>
          </div>
        ))}
      </div>
      <div className="p-4 border-t flex space-x-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter your message"
          className="flex-1"
        />
        <Button onClick={sendMessage}>Send</Button>
      </div>
    </div>
  );
}
