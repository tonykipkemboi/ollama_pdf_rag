"use client";

import { useState, useEffect } from "react";
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
import { FileText, Trash2, Square, CheckSquare } from "lucide-react";
import { fetcher } from "@/lib/utils";
import { usePDFSelection } from "@/hooks/use-pdf-selection";
import { Button } from "./ui/button";

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
  const { data: pdfs, mutate, isLoading } = useSWR<PDF[]>(
    "http://localhost:8001/api/v1/pdfs",
    fetcher,
    {
      refreshInterval: 5000, // Refresh every 5 seconds
    }
  );

  // Use global PDF selection state (persists across chats)
  const { selectedPdfIds, togglePdf, selectAll, clearSelection, isSelected } = usePDFSelection();

  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  // Clean up selected PDFs that no longer exist
  useEffect(() => {
    if (pdfs && selectedPdfIds.length > 0) {
      const validPdfIds = pdfs.map((p) => p.pdf_id);
      const validSelectedIds = selectedPdfIds.filter((id) =>
        validPdfIds.includes(id)
      );
      if (validSelectedIds.length !== selectedPdfIds.length) {
        selectAll(validSelectedIds);
      }
    }
  }, [pdfs, selectedPdfIds, selectAll]);

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
          📄 Documents
        </div>
        <SidebarGroupContent>
          <div className="flex w-full flex-col items-center justify-center gap-2 px-2 py-4 text-sm text-zinc-500">
            <span>No PDFs uploaded yet.</span>
            <span className="text-xs">Use the 📎 button to upload.</span>
          </div>
        </SidebarGroupContent>
      </SidebarGroup>
    );
  }

  // Show selected count
  const selectedCount = selectedPdfIds.length;
  const allSelected = pdfs.length > 0 && selectedCount === pdfs.length;

  return (
    <>
      <SidebarGroup>
        <div className="flex items-center justify-between px-2 py-1">
          <span className="text-sidebar-foreground/50 text-xs">
            📄 Documents ({selectedCount}/{pdfs.length})
          </span>
          <div className="flex gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="h-5 px-1 text-xs"
              onClick={() => {
                if (allSelected) {
                  clearSelection();
                } else {
                  selectAll(pdfs.map((p) => p.pdf_id));
                }
              }}
            >
              {allSelected ? "None" : "All"}
            </Button>
          </div>
        </div>
        {selectedCount === 0 && (
          <div className="px-2 pb-1 text-xs text-amber-500">
            ⚠️ Select PDFs to use as context
          </div>
        )}
        <SidebarGroupContent>
          <SidebarMenu>
            {pdfs.map((pdf) => {
              const selected = isSelected(pdf.pdf_id);
              return (
                <SidebarMenuItem key={pdf.pdf_id} className="group/pdf">
                  <div className="flex items-center justify-between">
                    <SidebarMenuButton
                      className={`flex-1 ${selected ? "bg-primary/10" : ""}`}
                      onClick={() => togglePdf(pdf.pdf_id)}
                    >
                      <div className="flex items-center gap-2 overflow-hidden">
                        {/* Checkbox icon */}
                        {selected ? (
                          <CheckSquare className="h-4 w-4 flex-shrink-0 text-primary" />
                        ) : (
                          <Square className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
                        )}
                        <div className="flex flex-col overflow-hidden">
                          <span className={`truncate text-sm ${selected ? "font-medium" : ""}`}>
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
