export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatPromptRequest {
  prompt: string;
  messages?: ChatMessage[];
  model?: string;
  max_tokens?: number;
  temperature?: number;
}

export interface ChatPromptResponse {
  response: string;
  model: string;
  tokens_used?: number;
}
