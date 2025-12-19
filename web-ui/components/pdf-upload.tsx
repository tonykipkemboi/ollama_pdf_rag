"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Upload, CheckCircle2 } from "lucide-react";

interface PDFUploadProps {
  onUploadComplete?: () => void;
}

export function PDFUpload({ onUploadComplete }: PDFUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [uploadCount, setUploadCount] = useState(0);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    setUploadCount(0);
    let successCount = 0;

    for (const file of Array.from(files)) {
      try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("http://localhost:8001/api/v1/pdfs/upload", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }

        const data = await response.json();
        console.log("Uploaded:", data);
        successCount++;
        setUploadCount(successCount);
      } catch (error) {
        console.error("Upload error:", error);
      }
    }

    setUploading(false);

    // Call the callback after all uploads complete
    if (onUploadComplete) {
      onUploadComplete();
    }

    // Reset the input
    e.target.value = "";
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-2">
        <input
          type="file"
          accept=".pdf"
          multiple
          onChange={handleUpload}
          className="hidden"
          id="pdf-upload"
        />
        <label htmlFor="pdf-upload" className="w-full">
          <Button asChild disabled={uploading} className="w-full">
            <span>
              <Upload className="mr-2 h-4 w-4" />
              {uploading
                ? `Uploading... (${uploadCount} completed)`
                : "Upload PDFs"}
            </span>
          </Button>
        </label>
      </div>
      {uploadCount > 0 && !uploading && (
        <div className="flex items-center gap-2 text-sm text-green-500">
          <CheckCircle2 className="h-4 w-4" />
          <span>{uploadCount} PDF(s) uploaded successfully</span>
        </div>
      )}
    </div>
  );
}
