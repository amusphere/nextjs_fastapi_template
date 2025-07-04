"use client";

import { useEffect, useRef, useState } from "react";
import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";

interface ChatMessage {
  id: string;
  message: string;
  isUser: boolean;
  timestamp: Date;
}

interface AIResponse {
  success: boolean;
  operator_response?: Record<string, unknown>;
  execution_results?: Record<string, unknown>[];
  summary?: {
    results_text?: string;
    [key: string]: unknown;
  };
  error?: string;
}

export default function AIChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (messageText: string) => {
    setError(null);
    setIsLoading(true);

    // ユーザーのメッセージを追加
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      message: messageText,
      isUser: true,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await fetch('/api/ai/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: messageText }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: AIResponse = await response.json();

      // AIの応答を整形
      let aiResponseText = "";
      if (data.success) {
        // 成功した場合はresults_textのみ表示
        aiResponseText = data.summary?.results_text || "処理が完了しました。";
      } else {
        aiResponseText = data.error || "エラーが発生しました。";
      }

      // AIの応答を追加
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: aiResponseText,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMessage]);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '不明なエラーが発生しました';
      setError(errorMessage);

      // エラーメッセージを追加
      const errorAiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: `エラー: ${errorMessage}`,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorAiMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full h-full flex flex-col bg-gray-50">
      {/* Error */}
      {error && (
        <div className="flex-shrink-0 p-4">
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md" role="alert">
            <p className="font-bold">エラー</p>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-2 min-h-0">
        {messages.length === 0 && !isLoading ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">Aureca AI</h1>
            <p>AIアシスタントに話しかけてみましょう。</p>
          </div>
        ) : (
          <div className="space-y-4 pb-4">
            {messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                message={msg.message}
                isUser={msg.isUser}
                timestamp={msg.timestamp}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex-shrink-0 bg-white/70 backdrop-blur-sm border-t border-gray-200/50">
        <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}
