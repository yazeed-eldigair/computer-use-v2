"use client";

import { createContext, useContext, useEffect, useRef, useState } from "react";
import { useSession } from "./session-provider";

interface WebSocketUpdate {
  type: "file" | "task" | "message" | "session" | "assistant_response";
  action: string;
  data: any;
}

interface WebSocketContextType {
  connected: boolean;
  lastUpdate: WebSocketUpdate | null;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(
  undefined
);

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const { session } = useSession();
  const ws = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<WebSocketUpdate | null>(null);

  useEffect(() => {
    if (!session) {
      if (ws.current) {
        ws.current.close();
        ws.current = null;
      }
      setConnected(false);
      return;
    }

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    ws.current = new WebSocket(`${protocol}//127.0.0.1:8000/ws/${session.id}`);

    ws.current.onopen = () => {
      setConnected(true);
    };

    ws.current.onclose = () => {
      setConnected(false);
    };

    ws.current.onmessage = (event) => {
      const update: WebSocketUpdate = JSON.parse(event.data);
      setLastUpdate(update);
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [session]);

  return (
    <WebSocketContext.Provider value={{ connected, lastUpdate }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error("useWebSocket must be used within a WebSocketProvider");
  }
  return context;
}
