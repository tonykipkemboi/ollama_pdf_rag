"use client";

import { useState, useCallback } from "react";
import { usePathname } from "next/navigation";
import { toast } from "sonner";
import useSWR from "swr";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from "@/components/ui/sidebar";
import { FileText, Trash2, Check } from "lucide-react";
import { fetcher } from "@/lib/utils";

interface PDF {
  pdf_id: string;
  name: string;
  collection_name: string;
  upload_timestamp: string;
  doc_count: number;
  page_count: number;
  is_sample: boolean;
}

export function SidebarPDFs() {
  const pathname = usePathname();
  const chatId = pathname?.startsWith("/chat/") ? pathname.split("/")[2] : null;

  const { data: pdfs, mutate, isLoading } = useSWR<PDF[]>(
    "http://localhost:8001/api/v1/pdfs",
    fetcher,
    {
      refreshInterval: 5000, // Refresh every 5 seconds
    }
  );

  // Fetch PDFs linked to current chat
  const { data: chatPdfsData, mutate: mutateChatPdfs } = useSWR<{ pdfIds: string[] }>(
    chatId ? `/api/chat/${chatId}/pdfs` : null,
    fetcher
  );
  const selectedPdfIds = chatPdfsData?.pdfIds || [];

  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const togglePdfSelection = useCallback(async (pdfId: string) => {
    if (!chatId) {
      toast.error("Start a chat first to select PDFs");
      return;
    }

    const isSelected = selectedPdfIds.includes(pdfId);

    try {
      if (isSelected) {
        // Remove PDF from chat
        await fetch(`/api/chat/${chatId}/pdfs`, {
          method: "DELETE",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ pdfId }),
        });
        toast.success("PDF removed from chat");
      } else {
        // Add PDF to chat
        await fetch(`/api/chat/${chatId}/pdfs`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ pdfId }),
        });
        toast.success("PDF added to chat");
      }
      mutateChatPdfs();
    } catch (error) {
      toast.error("Failed to update PDF selection");
    }
  }, [chatId, selectedPdfIds, mutateChatPdfs]);

  const handleDelete = async () => {
    const pdfToDelete = deleteId;
    setShowDeleteDialog(false);

    const deletePromise = fetch(
      `http://localhost:8001/api/v1/pdfs/${pdfToDelete}`,
      {
        method: "DELETE",
      }
    );

    toast.promise(deletePromise, {
      loading: "Deleting PDF...",
      success: () => {
        mutate(
          (currentPDFs) =>
            currentPDFs?.filter((pdf) => pdf.pdf_id !== pdfToDelete),
          false
        );
        return "PDF deleted successfully";
      },
      error: "Failed to delete PDF",
    });
  };

  if (isLoading) {
    return (
      <SidebarGroup>
        <div className="px-2 py-1 text-sidebar-foreground/50 text-xs">
          PDFs
        </div>
        <SidebarGroupContent>
          <div className="flex flex-col">
            {[1, 2, 3].map((item) => (
              <div
                className="flex h-8 items-center gap-2 rounded-md px-2"
                key={item}
              >
                <div className="h-4 w-full flex-1 rounded-md bg-sidebar-accent-foreground/10" />
              </div>
            ))}
          </div>
        </SidebarGroupContent>
      </SidebarGroup>
    );
  }

  if (!pdfs || pdfs.length === 0) {
    return (
      <SidebarGroup>
        <div className="px-2 py-1 text-sidebar-foreground/50 text-xs">
          PDFs
        </div>
        <SidebarGroupContent>
          <div className="flex w-full flex-row items-center justify-center gap-2 px-2 py-4 text-sm text-zinc-500">
            No PDFs uploaded yet. Use the 📎 button to upload.
          </div>
        </SidebarGroupContent>
      </SidebarGroup>
    );
  }

  // Show selected count if any
  const selectedCount = selectedPdfIds.length;
  const headerText = chatId
    ? `PDFs (${selectedCount}/${pdfs.length} selected)`
    : `PDFs (${pdfs.length})`;

  return (
    <>
      <SidebarGroup>
        <div className="px-2 py-1 text-sidebar-foreground/50 text-xs">
          {headerText}
          {chatId && selectedCount === 0 && (
            <span className="ml-1 text-amber-500">• Click to select</span>
          )}
        </div>
        <SidebarGroupContent>
          <SidebarMenu>
            {pdfs.map((pdf) => {
              const isSelected = selectedPdfIds.includes(pdf.pdf_id);
              return (
                <SidebarMenuItem key={pdf.pdf_id} className="group/pdf">
                  <div className="flex items-center justify-between">
                    <SidebarMenuButton
                      className={`flex-1 ${isSelected ? "bg-primary/10" : ""}`}
                      onClick={() => togglePdfSelection(pdf.pdf_id)}
                    >
                      <div className="flex items-center gap-2 overflow-hidden">
                        <div className="relative">
                          <FileText className={`h-4 w-4 flex-shrink-0 ${isSelected ? "text-primary" : ""}`} />
                          {isSelected && (
                            <Check className="absolute -right-1 -top-1 h-3 w-3 text-primary" />
                          )}
                        </div>
                        <div className="flex flex-col overflow-hidden">
                          <span className={`truncate text-sm ${isSelected ? "font-medium" : ""}`}>
                            {pdf.name}
                          </span>
                          <span className="text-xs text-zinc-500">
                            {pdf.doc_count} chunks • {pdf.page_count} pages
                          </span>
                        </div>
                      </div>
                    </SidebarMenuButton>
                    <div
                      className="ml-2 mr-2 cursor-pointer opacity-0 transition-opacity group-hover/pdf:opacity-100"
                      onClick={(e) => {
                        e.stopPropagation();
                        setDeleteId(pdf.pdf_id);
                        setShowDeleteDialog(true);
                      }}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          setDeleteId(pdf.pdf_id);
                          setShowDeleteDialog(true);
                        }
                      }}
                    >
                      <Trash2 className="h-4 w-4 text-zinc-500 hover:text-red-500" />
                    </div>
                  </div>
                </SidebarMenuItem>
              );
            })}
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <AlertDialog onOpenChange={setShowDeleteDialog} open={showDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete PDF?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete this
              PDF, its vector embeddings, and remove it from our servers.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
