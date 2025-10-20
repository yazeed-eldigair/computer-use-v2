"use client";

import { useState, useEffect, useRef } from "react";
import { useSession } from "@/providers/session-provider";
import { useWebSocket } from "@/providers/websocket-provider";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Send, Loader2 } from "lucide-react";

interface Message {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

interface File {
  id: string;
  filename: string;
  mime_type: string;
  size: number;
  uploaded_at: string;
}

export function ChatPanel() {
  const { session } = useSession();
  const { lastUpdate } = useWebSocket();
  const [messages, setMessages] = useState<Message[]>([]);
  const [, setFiles] = useState<File[]>([]);
  const [isWaiting, setIsWaiting] = useState(false);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!session) return;

    // Load initial messages
    fetch(`/api/chat/${session.id}/messages`)
      .then((res) => res.json())
      .then(setMessages);

    // Load initial files
    fetch(`/api/files?session_id=${session.id}`)
      .then((res) => res.json())
      .then(setFiles);
  }, [session]);

  useEffect(() => {
    if (lastUpdate?.type === "assistant_response" && lastUpdate.data?.role) {
      setMessages((prev) => [...prev, lastUpdate.data]);
    }

    if (
      lastUpdate?.type === "assistant_response" &&
      lastUpdate.action === "end"
    ) {
      setIsWaiting(false);
    } else if (lastUpdate?.type === "file") {
      if (lastUpdate.action === "uploaded") {
        setFiles((prev) => [...prev, lastUpdate.data]);
      } else if (lastUpdate.action === "deleted") {
        setFiles((prev) => prev.filter((f) => f.id !== lastUpdate.data.id));
      }
    }
  }, [lastUpdate]);

  // Auto scroll to bottom when messages change
  useEffect(() => {
    const scrollArea = scrollRef.current;
    if (scrollArea) {
      const scrollContainer = scrollArea.querySelector(
        "[data-radix-scroll-area-viewport]"
      );
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!session || !input.trim()) return;

    // Add user message immediately
    const tempMessage: Message = {
      id: crypto.randomUUID(),
      session_id: session.id,
      role: "user",
      content: input.trim(),
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempMessage]);
    setInput("");
    setIsWaiting(true);

    try {
      await fetch(`/api/chat/${session.id}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: tempMessage.content }),
      });
    } catch (error) {
      console.error("Failed to send message:", error);
    }
  };

  if (!session) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-center text-sm text-muted-foreground">
          Start by creating a chat
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 min-h-0 overflow-hidden">
        <ScrollArea ref={scrollRef} className="h-full">
          <div className="space-y-4 p-4">
            {messages
              .filter((msg) => msg && msg.role)
              .map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${
                    msg.role === "assistant" ? "justify-start" : "justify-end"
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 animate-in slide-in-from-bottom-2 duration-400 caret-transparent ${
                      msg.role === "assistant"
                        ? "bg-secondary text-secondary-foreground"
                        : "bg-primary text-primary-foreground"
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
            {isWaiting && (
              <div className="flex justify-start">
                <div className="max-w-[80%] rounded-lg p-3 bg-secondary text-secondary-foreground">
                  <Loader2 className="h-4 w-4 animate-spin opacity-70" />
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      <div className="shrink-0">
        <Separator />
        <div className="p-4 flex items-center gap-2 bg-background">
          <form
            onSubmit={handleSubmit}
            className="flex w-full items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a message..."
              className="flex-1 rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring cursor-text"
            />
            <Button
              type="submit"
              size="icon"
              className="shrink-0"
              disabled={isWaiting}
            >
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
