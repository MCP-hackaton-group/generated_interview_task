import { useState } from "react";
import { Avatar } from "./ui/avatar";
import { Button } from "./ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";

export default function MessagingApp() {
  const [messages, setMessages] = useState([
    {
      id: "1",
      content: "Hello! How can I help you today?",
      sender: "agent",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");

    // Simulate agent response after a short delay
    setTimeout(() => {
      const agentMessage = {
        id: (Date.now() + 1).toString(),
        content: "Thanks for your message! This is a simulated response from the agent.",
        sender: "agent",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, agentMessage]);
    }, 1000);
  };

  // Generate mock avatar URLs using UI Avatars based on initials
  const generateAvatar = (name) => {
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random&color=fff&size=256`;
  };

  return (
    <div className="flex min-h-screen bg-gray-50 items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="border-b bg-white">
          <CardTitle className="flex items-center gap-2">
            <Avatar className="h-8 w-8">
              <img
                src={generateAvatar("AGENT")}
                alt="Agent"
                className="h-full w-full object-cover rounded-full"
              />
            </Avatar>
            <span>Proggraming Assignments Generator</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="h-[60vh] overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}>
                <div className="flex items-start gap-2 max-w-[80%]">
                  {message.sender === "agent" && (
                    <Avatar className="h-8 w-8 mt-0.5">
                      <img
                        src={generateAvatar("AGENT")}
                        alt="Agent"
                        className="h-full w-full object-cover rounded-full"
                      />
                    </Avatar>
                  )}
                  <div
                    className={`p-3 rounded-lg ${message.sender === "user"
                        ? "bg-teal-500 text-white rounded-br-none"
                        : "bg-gray-200 text-gray-800 rounded-bl-none"
                      }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </p>
                  </div>
                  {message.sender === "user" && (
                    <Avatar className="h-8 w-8 mt-0.5">
                      <img
                        src={generateAvatar("CLIENT")}
                        alt="User"
                        className="h-full w-full object-cover rounded-full"
                      />
                    </Avatar>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
<CardFooter className="border-t p-3 flex items-center">
  <form
    className="flex w-full gap-2 items-center"
    onSubmit={(e) => {
      e.preventDefault();
      handleSendMessage();
    }}
  >
    <Input
      placeholder="Type your message..."
      value={inputValue}
      onChange={(e) => setInputValue(e.target.value)}
      className="flex-1"
    />
    <Button type="submit" size="icon" className="bg-teal-500 hover:bg-teal-600">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="h-4 w-4"
      >
        <path d="M22 2L11 13"></path>
        <path d="M22 2L15 22L11 13L2 9L22 2Z"></path>
      </svg>
    </Button>
  </form>
</CardFooter>


      </Card>
    </div>
  );
}
