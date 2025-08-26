"use client";

import { Button } from "@/components/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/components/ui/card";
import { Input } from "@/components/components/ui/input";
import { Separator } from "@/components/components/ui/separator";
import { ChatMessage } from "@/types/Chat";
import { Bot, MessageCircle, Send, Trash2, User } from "lucide-react";
import { useEffect, useRef, useState } from "react";

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const DRAFT_KEY = "chat:inputDraft";

  // メッセージ追加時にボトムへスクロール
  useEffect(() => {
    try {
      bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    } catch {
      // noop
    }
  }, [messages]);

  // 初回マウント時にサーバの履歴を取得
  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch("/api/chat/history?limit=50", { method: "GET" });
        if (res.ok) {
          const data: { total: number; messages: { role: ChatMessage["role"]; content: string }[] } = await res.json();
          const mapped: ChatMessage[] = (data.messages || []).map((m) => ({ role: m.role, content: m.content }));
          setMessages(mapped);
        }
      } catch {
        // サーバ取得失敗時は何もしない（空表示）
      }
    };
    load();
  }, []);

  // 入力ドラフトの復元
  useEffect(() => {
    try {
      const raw = typeof window !== "undefined" ? window.localStorage.getItem(DRAFT_KEY) : null;
      if (raw) setInput(raw);
    } catch {
      // noop
    }
  }, []);

  // 入力ドラフトの保存
  useEffect(() => {
    try {
      if (typeof window !== "undefined") {
        if (input) window.localStorage.setItem(DRAFT_KEY, input);
        else window.localStorage.removeItem(DRAFT_KEY);
      }
    } catch {
      // noop
    }
  }, [input]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const prompt = input;
    setMessages((msgs) => [...msgs, { role: "user", content: prompt }]);
    setInput("");
    try { if (typeof window !== "undefined") window.localStorage.removeItem(DRAFT_KEY); } catch { }
    setIsLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      const data = await res.json();
      if (res.ok) {
        setMessages((msgs) => [...msgs, { role: "assistant", content: data.response }]);
      } else {
        setMessages((msgs) => [...msgs, { role: "assistant", content: data.message || "Error occurred" }]);
      }
    } catch {
      setMessages((msgs) => [...msgs, { role: "assistant", content: "Connection error. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col w-full h-full max-h-screen md:max-w-4xl md:mx-auto md:px-4 md:py-4">
      <Card className="flex flex-col h-full max-h-full overflow-hidden">
        <CardHeader className="pb-4 flex-shrink-0">
          <div className="flex items-center justify-between gap-3">
            <CardTitle className="flex items-center gap-2 text-center md:text-left">
              <MessageCircle className="h-6 w-6" />
              AI Chat Assistant
            </CardTitle>
            <Button
              variant="secondary"
              size="sm"
              onClick={async () => {
                try {
                  await fetch("/api/chat/history", { method: "DELETE" });
                } catch {
                  // noop
                }
                setMessages([]);
                setInput("");
                try { if (typeof window !== "undefined") window.localStorage.removeItem(DRAFT_KEY); } catch { }
              }}
              title="Reset chat history"
            >
              <Trash2 className="h-4 w-4 mr-1" /> Reset
            </Button>
          </div>
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Start a conversation with our AI assistant
            </p>
          </div>
        </CardHeader>

        <Separator className="flex-shrink-0" />

        <CardContent className="flex-1 flex flex-col p-0 min-h-0 overflow-hidden">
          {/* Chat messages area */}
          <div className="flex-1 overflow-y-auto p-4 max-h-full">
            <div className="space-y-4 min-h-full">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <div className="h-16 w-16 bg-muted rounded-full flex items-center justify-center mb-4">
                    <Bot className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Welcome to AI Chat!</h3>
                  <p className="text-muted-foreground max-w-md">
                    Ask me anything and I&apos;ll do my best to help you. Start by typing a message below.
                  </p>
                </div>
              ) : (
                messages.map((message, idx) => (
                  <div key={idx} className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                    {message.role === "assistant" && (
                      <div className="h-8 w-8 bg-primary/10 rounded-full flex items-center justify-center shrink-0">
                        <Bot className="h-4 w-4 text-primary" />
                      </div>
                    )}

                    <div className={`max-w-[80%] md:max-w-[70%] ${message.role === "user" ? "order-first" : ""}`}>
                      <div className={`p-3 rounded-lg ${message.role === "user"
                        ? "bg-primary text-primary-foreground ml-auto"
                        : "bg-muted"
                        }`}>
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      </div>
                    </div>

                    {message.role === "user" && (
                      <div className="h-8 w-8 bg-primary rounded-full flex items-center justify-center shrink-0">
                        <User className="h-4 w-4 text-primary-foreground" />
                      </div>
                    )}
                  </div>
                ))
              )}

              {/* Loading display */}
              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="h-8 w-8 bg-primary/10 rounded-full flex items-center justify-center shrink-0">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                  <div className="bg-muted p-3 rounded-lg">
                    <div className="flex gap-1">
                      <div className="h-2 w-2 bg-muted-foreground/40 rounded-full animate-bounce"></div>
                      <div className="h-2 w-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="h-2 w-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
              <div ref={bottomRef} />
            </div>
          </div>

          <Separator />

          {/* Input area */}
          <div className="p-4">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message here..."
                className="flex-1"
                onKeyPress={handleKeyPress}
                disabled={isLoading}
              />
              <Button
                onClick={sendMessage}
                disabled={!input.trim() || isLoading}
                size="icon"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
