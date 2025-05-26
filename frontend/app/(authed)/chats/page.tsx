'use client';

import { Button } from '@/components/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/components/ui/card';
import { Input } from '@/components/components/ui/input';
import { ChatMessage, ChatPromptRequest, ChatPromptResponse } from '@/types/Chat';
import { useState } from 'react';


export default function ChatsPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSendMessage = async () => {
    if (!prompt.trim()) return;

    setIsLoading(true);
    setError(null);

    // ユーザーメッセージを追加
    const userMessage: ChatMessage = { role: 'user', content: prompt };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);

    try {
      const request: ChatPromptRequest = {
        prompt,
        messages: messages, // 過去の会話履歴
        model: 'gpt4.1',
        max_tokens: 1000,
        temperature: 0.7,
      };

      const response = await fetch('/api/chats', {
        method: 'POST',
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to get response from AI');
      } else {
        const data = await response.json() as ChatPromptResponse;
        // アシスタントの返答を追加
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: data.response,
        };
        setMessages([...updatedMessages, assistantMessage]);
      }
    } catch (err) {
      setError('Failed to send message');
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
      setPrompt('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">AI Chat</h1>
        <p className="text-gray-600">LLMとチャットしてみましょう</p>
      </div>

      {error && (
        <Card className="mb-4 border-red-200 bg-red-50">
          <CardContent className="p-4">
            <p className="text-red-600">{error}</p>
          </CardContent>
        </Card>
      )}

      <Card className="mb-4">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Chat History</CardTitle>
          <Button variant="outline" onClick={clearChat} disabled={messages.length === 0}>
            Clear Chat
          </Button>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {messages.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                チャットを開始してください...
              </p>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg ${message.role === 'user'
                    ? 'bg-blue-100 ml-12'
                    : 'bg-gray-100 mr-12'
                    }`}
                >
                  <div className="flex items-start gap-2">
                    <span className="font-semibold text-sm">
                      {message.role === 'user' ? 'You' : 'AI'}:
                    </span>
                    <p className="flex-1 whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4">
          <div className="flex gap-2">
            <Input
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="メッセージを入力してください..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button
              onClick={handleSendMessage}
              disabled={isLoading || !prompt.trim()}
            >
              {isLoading ? 'Sending...' : 'Send'}
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Enterキーで送信 | Shift+Enterで改行
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
