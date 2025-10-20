"use client";

export function VncViewer() {
  return (
    <div className="relative h-full w-full bg-black">
      <iframe
        src="http://127.0.0.1:6080/vnc.html?&resize=scale&autoconnect=1&view_only=1&reconnect=1&reconnect_delay=2000"
        className="h-full w-full border-0"
        allow="fullscreen"
      />
    </div>
  );
}
