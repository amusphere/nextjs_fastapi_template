import { cn } from "../../lib/utils";
import { Bot, User } from 'lucide-react';

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp: Date; // タイムスタンプは当面表示しないが、データとしては残す
}

export default function ChatMessage({ message, isUser }: ChatMessageProps) {
  const Icon = isUser ? User : Bot;
  const iconContainerBg = isUser ? "bg-gray-300" : "bg-gray-200";
  const iconColor = isUser ? "text-gray-600" : "text-gray-500";

  return (
    <div className={cn("flex items-start gap-3", isUser ? "justify-end" : "justify-start")}>
      {!isUser && (
        <div className={cn("w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center", iconContainerBg)}>
          <Icon className={cn("w-5 h-5", iconColor)} />
        </div>
      )}
      <div
        className={cn(
          "max-w-[85%] rounded-2xl px-4 py-2.5",
          isUser
            ? "bg-blue-600 text-white"
            : "bg-white border border-gray-200"
        )}
      >
        <p className="text-sm whitespace-pre-wrap break-words">{message}</p>
      </div>
      {isUser && (
        <div className={cn("w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center", iconContainerBg)}>
          <Icon className={cn("w-5 h-5", iconColor)} />
        </div>
      )}
    </div>
  );
}
