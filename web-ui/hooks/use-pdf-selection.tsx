"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import { useLocalStorage } from "usehooks-ts";

interface PDF {
  pdf_id: string;
  name: string;
  doc_count: number;
  page_count: number;
}

interface PDFSelectionContextType {
  selectedPdfIds: string[];
  togglePdf: (pdfId: string) => void;
  selectPdf: (pdfId: string) => void;
  deselectPdf: (pdfId: string) => void;
  selectAll: (pdfIds: string[]) => void;
  clearSelection: () => void;
  isSelected: (pdfId: string) => boolean;
}

const PDFSelectionContext = createContext<PDFSelectionContextType | undefined>(
  undefined
);

export function PDFSelectionProvider({ children }: { children: ReactNode }) {
  // Use localStorage to persist selection across page reloads
  const [selectedPdfIds, setSelectedPdfIds] = useLocalStorage<string[]>(
    "selected-pdf-ids",
    []
  );

  const togglePdf = useCallback(
    (pdfId: string) => {
      setSelectedPdfIds((prev) =>
        prev.includes(pdfId)
          ? prev.filter((id) => id !== pdfId)
          : [...prev, pdfId]
      );
    },
    [setSelectedPdfIds]
  );

  const selectPdf = useCallback(
    (pdfId: string) => {
      setSelectedPdfIds((prev) =>
        prev.includes(pdfId) ? prev : [...prev, pdfId]
      );
    },
    [setSelectedPdfIds]
  );

  const deselectPdf = useCallback(
    (pdfId: string) => {
      setSelectedPdfIds((prev) => prev.filter((id) => id !== pdfId));
    },
    [setSelectedPdfIds]
  );

  const selectAll = useCallback(
    (pdfIds: string[]) => {
      setSelectedPdfIds(pdfIds);
    },
    [setSelectedPdfIds]
  );

  const clearSelection = useCallback(() => {
    setSelectedPdfIds([]);
  }, [setSelectedPdfIds]);

  const isSelected = useCallback(
    (pdfId: string) => selectedPdfIds.includes(pdfId),
    [selectedPdfIds]
  );

  return (
    <PDFSelectionContext.Provider
      value={{
        selectedPdfIds,
        togglePdf,
        selectPdf,
        deselectPdf,
        selectAll,
        clearSelection,
        isSelected,
      }}
    >
      {children}
    </PDFSelectionContext.Provider>
  );
}

export function usePDFSelection() {
  const context = useContext(PDFSelectionContext);
  if (context === undefined) {
    throw new Error(
      "usePDFSelection must be used within a PDFSelectionProvider"
    );
  }
  return context;
}
