"use client";

import { useState, useEffect } from "react";
import { useSession } from "@/providers/session-provider";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Plus, MessageCircle, Trash2 } from "lucide-react";

interface Session {
  id: string;
  title: string;
  created_at: string;
  status: string;
}

export function SessionPanel() {
  const { session, createSession, setSession } = useSession();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");

  useEffect(() => {
    // Load sessions on mount
    fetch("/api/sessions")
      .then((res) => res.json())
      .then(setSessions);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    try {
      const newSession = await createSession(title);
      setSessions((prev) => [...prev, newSession]);
      setTitle("");
      setOpen(false);
    } catch (error) {
      console.error("Failed to create session:", error);
    }
  };

  const handleDelete = async (s: Session, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent session selection when deleting
    try {
      const response = await fetch(`/api/sessions/${s.id}`, {
        method: "DELETE",
      });
      if (!response.ok) throw new Error("Failed to delete session");

      setSessions((prev) => prev.filter((sess) => sess.id !== s.id));
      if (session?.id === s.id) {
        setSession(null);
      }
    } catch (error) {
      console.error("Failed to delete session:", error);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <ScrollArea className="flex-1">
        <div className="space-y-2 p-4">
          {sessions.map((s) => (
            <div
              key={s.id}
              className={`flex cursor-pointer items-center justify-between rounded-lg border p-3 animate-in slide-in-from-left-5 duration-300 ${
                session?.id === s.id ? "border-primary bg-primary/5" : ""
              }`}
              onClick={() => setSession(s)}
            >
              <div className="flex items-center gap-3 caret-transparent">
                <MessageCircle className="h-4 w-4 text-muted-foreground" />
                <p className="font-medium">{s.title}</p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={(e) => handleDelete(s, e)}
                className="h-8 w-8 cursor-pointer"
              >
                <Trash2 className="h-4 w-4 hover:text-destructive text-black" />
              </Button>
            </div>
          ))}
        </div>
      </ScrollArea>

      <div className="p-4 flex items-center justify-center">
        <Button
          className="cursor-pointer mb-4"
          size="lg"
          onClick={() => setOpen(true)}
        >
          <Plus className="mr-2 h-4 w-4" />
          New Chat
        </Button>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create new chat</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4 py-4">
              <Input
                placeholder="Chat title..."
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="cursor-text"
              />
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setOpen(false)}
                className="cursor-pointer"
              >
                Cancel
              </Button>
              <Button type="submit" className="cursor-pointer">
                Create
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
