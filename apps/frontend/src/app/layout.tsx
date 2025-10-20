import type { Metadata } from "next";
import { Geist } from "next/font/google";
import { SessionProvider } from "@/providers/session-provider";
import { WebSocketProvider } from "@/providers/websocket-provider";
import { Toaster } from "sonner";
import "./globals.css";
import { cn } from "@/lib/utils";

const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist",
});

export const metadata: Metadata = {
  title: "Computer Use v2",
  description: "AI-powered computer control interface",
  authors: [{ name: "Yazeed Eldigair" }],
  keywords: ["Computer Use", "Anthropic", "AI-powered", "Computer control", "VNC", "AI"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={cn(
          "min-h-screen bg-background font-sans antialiased",
          geist.className
        )}
      >
        <div className="relative flex min-h-screen flex-col dark:bg-gray-950">
          <SessionProvider>
            <WebSocketProvider>
              <main className="flex-1">{children}</main>
              <Toaster richColors position="top-right" />
            </WebSocketProvider>
          </SessionProvider>
        </div>
      </body>
    </html>
  );
}
