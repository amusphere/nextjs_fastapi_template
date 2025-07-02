import { cn } from "../../lib/utils";
import { Card, CardContent } from "../ui/card";

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp: Date;
}

export default function ChatMessage({ message, isUser, timestamp }: ChatMessageProps) {
  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}>
      <div className={cn(
        "max-w-[85%] sm:max-w-[75%] md:max-w-[70%]",
        isUser ? "ml-2 sm:ml-4" : "mr-2 sm:mr-4"
      )}>
        <Card className={cn(
          "shadow-sm break-words",
          isUser
            ? "bg-blue-500 text-white border-blue-500"
            : "bg-gray-50 border-gray-200"
        )}>
          <CardContent className="p-2 sm:p-3">
            <div className="break-words overflow-wrap-anywhere">
              <p className="text-sm sm:text-base whitespace-pre-wrap">
                {message}
              </p>
            </div>
            <p className={cn(
              "text-xs mt-2 opacity-70",
              isUser ? "text-blue-100" : "text-gray-500"
            )}>
              {timestamp.toLocaleTimeString()}
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
