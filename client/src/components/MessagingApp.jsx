import { useState } from "react";
import axios from "axios";
import { Avatar } from "./ui/avatar";
import { Button } from "./ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Input } from "./ui/input";

export default function MessagingApp() {
  const [messages, setMessages] = useState([
    {
      id: "1",
      sender: "agent",
      timestamp: new Date(),
      content: "Hello! How can I help you today?",
    },
  ]);
  const [inputValue, setInputValue] = useState("");

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      sender: "user",
      timestamp: new Date(),
      content: inputValue,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");

    try {
      const response = await axios.post(
        "http://localhost:5001/user-message",
        { message: inputValue },
        { headers: { "Content-Type": "application/json" } }
      );
      const data = response.data;

      const agentMessage = {
        id: Date.now().toString(),
        sender: "agent",
        timestamp: new Date(),
        ...(typeof data === "object"
          ? { jsonData: data }
          : { content: String(data) }),
      };
      setMessages((prev) => [...prev, agentMessage]);
    } catch (err) {
      console.error(err);
    }
  };

  const generateAvatar = (name) =>
    `https://ui-avatars.com/api/?name=${encodeURIComponent(
      name
    )}&background=random&color=fff&size=256`;

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
            <span>Programming Assignments Generator</span>
          </CardTitle>
        </CardHeader>

        <CardContent className="p-0">
          <div className="h-[60vh] overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.sender === "user" ? "justify-end" : "justify-start"
                }`}
              >
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
                    className={`p-3 rounded-lg ${
                      message.sender === "user"
                        ? "bg-teal-500 text-white rounded-br-none"
                        : "bg-gray-200 text-gray-800 rounded-bl-none"
                    }`}
                  >
                    {message.jsonData ? (
                      <JSONViewer data={message.jsonData} />
                    ) : (
                      <p className="text-sm whitespace-pre-wrap">
                        {message.content}
                      </p>
                    )}
                    <p className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
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
            <Button
              type="submit"
              size="icon"
              className="bg-teal-500 hover:bg-teal-600"
            >
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
                <path d="M22 2L11 13" />
                <path d="M22 2L15 22L11 13L2 9L22 2Z" />
              </svg>
            </Button>
          </form>
        </CardFooter>
      </Card>
    </div>
  );
}

function JSONViewer({ data, depth = 0 }) {
  if (data === null || typeof data !== "object") {
    return <span className="text-sm">{data === null ? "null" : data}</span>;
  }

  if (Array.isArray(data)) {
    return (
      <ul
        className="list-disc list-inside text-sm"
        style={{ marginLeft: depth * 16 }}
      >
        {data.map((item, idx) => (
          <li key={idx}>
            <JSONViewer data={item} depth={depth + 1} />
          </li>
        ))}
      </ul>
    );
  }

  // Reverse the keys so first-defined fields render at top
  const keys = Object.keys(data).reverse();
  return (
    <div
      className="space-y-1 text-sm"
      style={{ marginLeft: depth * 16 }}
    >
      {keys.map((key) => (
        <div key={key}>
          <strong className="capitalize">
            {key.replace(/_/g, " ").replace(/([a-z])([A-Z])/g, "$1 $2")}:
          </strong>{" "}
          <JSONViewer data={data[key]} depth={depth + 1} />
        </div>
      ))}
    </div>
  );
}
