"use client";

import { createContext, useContext, useState } from "react";

interface Session {
  id: string;
  title: string;
  status: string;
  created_at: string;
}

interface SessionContextType {
  session: Session | null;
  setSession: (session: Session | null) => void;
  createSession: (title: string) => Promise<Session>;
  updateSession: (title?: string, status?: string) => Promise<void>;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);

  const createSession = async (title: string): Promise<Session> => {
    const response = await fetch("/api/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });

    if (!response.ok) {
      throw new Error("Failed to create session");
    }

    const newSession = await response.json();
    setSession(newSession);
    return newSession;
  };

  const updateSession = async (title?: string, status?: string) => {
    if (!session) return;

    const response = await fetch(`/api/sessions/${session.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, status }),
    });

    if (!response.ok) {
      throw new Error("Failed to update session");
    }

    const updatedSession = await response.json();
    setSession(updatedSession);
  };

  return (
    <SessionContext.Provider
      value={{ session, setSession, createSession, updateSession }}
    >
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error("useSession must be used within a SessionProvider");
  }
  return context;
}
