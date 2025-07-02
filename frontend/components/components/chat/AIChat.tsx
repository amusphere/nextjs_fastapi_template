"use client";

import { AlertCircle } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Alert, AlertDescription } from "../ui/alert";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
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
    <Card className="h-[500px] sm:h-[600px] flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg sm:text-xl">AI アシスタント</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0">
        {error && (
          <Alert className="mx-3 sm:mx-4 mb-4 border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800 text-sm">
              {error}
            </AlertDescription>
          </Alert>
        )}

        <div className="flex-1 overflow-y-auto px-3 sm:px-4 py-2">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-500">
              <p className="text-center text-sm sm:text-base px-4">
                AIアシスタントに質問や依頼を送信してください。
              </p>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <ChatMessage
                  key={msg.id}
                  message={msg.message}
                  isUser={msg.isUser}
                  timestamp={msg.timestamp}
                />
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
      </CardContent>
    </Card>
  );
}
