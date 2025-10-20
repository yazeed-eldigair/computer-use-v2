"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Upload, File as FileIcon, Trash2, UploadCloud } from "lucide-react";
import { cn } from "@/lib/utils";
import { useSession } from "@/providers/session-provider";
import { toast } from "sonner";

interface FileInfo {
  id: string;
  filename: string;
  size: number;
  uploaded_at: string;
}

interface StagedFile {
  file: File;
  id: string;
  filename: string;
  size: number;
}

export function FilePanel() {
  const { session } = useSession();
  const sessionId = session?.id;
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [stagedFiles, setStagedFiles] = useState<StagedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleFilesSelected = (selectedFiles: File[]) => {
    const newStagedFiles = selectedFiles.map((file) => ({
      file,
      id: crypto.randomUUID(),
      filename: file.name,
      size: file.size,
    }));
    setStagedFiles((prev) => [...prev, ...newStagedFiles]);
  };

  const uploadStagedFiles = async () => {
    if (stagedFiles.length === 0) return;
    setIsUploading(true);

    for (const staged of stagedFiles) {
      const formData = new FormData();
      formData.append("file", staged.file);

      try {
        const response = await fetch(`/api/files?session_id=${sessionId}`, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }

        const newFile = await response.json();
        setFiles((prev) => [...prev, newFile]);
        toast.success(`File uploaded: ${newFile.filename}`);
      } catch (error) {
        console.error("Upload error:", error);
        toast.error(`Failed to upload file: ${staged.filename}`);
      }
    }

    setStagedFiles([]);
    setIsUploading(false);
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    handleFilesSelected(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    noClick: stagedFiles.length > 0, // Disable clicking when files are staged
  });

  // File input is now handled by dropzone

  const removeStagedFile = (id: string) => {
    setStagedFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const handleDelete = async (fileId: string) => {
    try {
      const response = await fetch(
        `/api/files/${fileId}?session_id=${sessionId}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error(`Delete failed: ${response.statusText}`);
      }

      const deletedFile = files.find(f => f.id === fileId);
      setFiles((prev) => prev.filter((f) => f.id !== fileId));
      if (deletedFile) {
        toast.success(`File deleted: ${deletedFile.filename}`);
      }
    } catch (error) {
      console.error("Delete error:", error);
      toast.error("Failed to delete file");
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    const kb = bytes / 1024;
    if (kb < 1024) return kb.toFixed(1) + " KB";
    const mb = kb / 1024;
    if (mb < 1024) return mb.toFixed(1) + " MB";
    const gb = mb / 1024;
    return gb.toFixed(1) + " GB";
  };

  if (!sessionId) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 text-sm text-muted-foreground">
        <p>Start a chat to upload and manage files</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex h-14 items-center justify-between px-4 py-2">
        <h2 className="text-lg font-semibold">Files</h2>
        <div className="relative">
          <Button
            variant="outline"
            size="sm"
            className="cursor-pointer"
            disabled={isUploading || stagedFiles.length === 0}
            onClick={(e) => {
              e.stopPropagation();
              uploadStagedFiles();
            }}
          >
            <Upload className="mr-2 h-4 w-4" />
            Upload {stagedFiles.length > 0 && `(${stagedFiles.length})`}
          </Button>
        </div>
      </div>
      <ScrollArea className="flex-1">
        <div className="relative space-y-2 p-4">
          {files.length === 0 && stagedFiles.length === 0 ? (
            <div
              {...getRootProps()}
              className={cn(
                "flex h-[200px] flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed text-sm text-muted-foreground",
                stagedFiles.length === 0 && "cursor-pointer",
                isDragActive && "border-primary/50 bg-primary/5"
              )}
            >
              <input {...getInputProps()} />
              <UploadCloud className="h-8 w-8" />
              <p>Drag and drop files here or click to select</p>
            </div>
          ) : (
            <>
              {stagedFiles.map((file) => (
                <div
                  key={file.id}
                  className="flex items-center justify-between rounded-lg border border-primary/20 bg-primary/5 p-3"
                >
                  <div className="flex items-center space-x-3">
                    <FileIcon className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">{file.filename}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatFileSize(file.size)} • Ready to upload
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="cursor-pointer"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeStagedFile(file.id);
                    }}
                  >
                    <Trash2 className="h-4 w-4 text-muted-foreground" />
                  </Button>
                </div>
              ))}
              {files.map((file) => (
                <div
                  key={file.id}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div className="flex items-center space-x-3">
                    <FileIcon className="h-5 w-5 text-gray-500" />
                    <div>
                      <p className="font-medium">{file.filename}</p>
                      <p className="text-sm text-gray-500">
                        {formatFileSize(file.size)}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="cursor-pointer"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(file.id);
                    }}
                  >
                    <Trash2 className="h-4 w-4 text-gray-500" />
                  </Button>
                </div>
              ))}
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
