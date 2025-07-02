import AIChat from "../components/chat/AIChat";

export default function DashboardPage() {
  return (
    <div className="h-screen flex flex-col">
      <div className="flex-1 px-4 pb-12">
        <AIChat />
      </div>
    </div>
  );
}
