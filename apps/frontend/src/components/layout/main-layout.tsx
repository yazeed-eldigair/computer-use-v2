import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { Separator } from "@/components/ui/separator";
import { SessionPanel } from "@/components/session/session-panel";
import { ChatPanel } from "@/components/chat/chat-panel";
import { VncViewer } from "@/components/computer/vnc-viewer";
import { SessionProvider } from "@/providers/session-provider";
import { WebSocketProvider } from "@/providers/websocket-provider";
import { FilePanel } from "@/components/file/file-panel";

export function MainLayout() {
  return (
    <SessionProvider>
      <WebSocketProvider>
        <ResizablePanelGroup
          direction="horizontal"
          className="min-h-screen rounded-lg border"
        >
          {/* Left Panel - Chats */}
          <ResizablePanel defaultSize={20} minSize={15} maxSize={25}>
            <div className="flex h-full flex-col">
              <div className="flex h-14 items-center px-4 py-2">
                <h2 className="text-lg font-semibold">Chats</h2>
              </div>
              <Separator />
              <div className="flex-1 overflow-hidden">
                <SessionPanel />
              </div>
            </div>
          </ResizablePanel>

          <ResizableHandle />

          {/* Middle Panel - Computer View */}
          <ResizablePanel defaultSize={50}>
            <div className="flex h-full flex-col">
              <div className="flex h-14 items-center px-4 py-2">
                <h2 className="text-lg font-semibold">Computer View</h2>
              </div>
              <Separator />
              <div className="flex-1">
                <VncViewer />
              </div>
            </div>
          </ResizablePanel>

          <ResizableHandle />

          {/* Right Panel - Agent & files */}
          <ResizablePanel defaultSize={30} minSize={25} maxSize={35}>
            <div className="flex h-full flex-col">
              <div className="flex h-14 items-center px-4 py-2">
                <h2 className="text-lg font-semibold">Agent & Files</h2>
              </div>
              <Separator />
              <ResizablePanelGroup direction="vertical">
                <ResizablePanel defaultSize={70}>
                  <ChatPanel />
                </ResizablePanel>
                <ResizableHandle />
                <ResizablePanel defaultSize={30}>
                  <FilePanel />
                </ResizablePanel>
              </ResizablePanelGroup>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </WebSocketProvider>
    </SessionProvider>
  );
}
