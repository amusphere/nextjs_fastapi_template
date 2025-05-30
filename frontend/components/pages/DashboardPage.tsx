import AIChat from "../components/chat/AIChat";

export default function DashboardPage() {
  return (
    <div className="container mx-auto p-4 sm:p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-2xl sm:text-3xl font-bold">Dashboard</h1>
        <p className="mt-2 text-gray-600">Welcome to your dashboard!</p>
      </div>

      <div className="max-w-4xl mx-auto">
        <AIChat />
      </div>
    </div>
  );
}
