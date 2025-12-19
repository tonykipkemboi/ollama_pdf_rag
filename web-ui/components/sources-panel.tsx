"use client";

import { Card } from "@/components/ui/card";
import { FileText } from "lucide-react";

interface Source {
  pdf_name: string;
  pdf_id: string;
  chunk_index: number;
}

interface SourcesPanelProps {
  sources: Source[];
}

export function SourcesPanel({ sources }: SourcesPanelProps) {
  if (!sources || sources.length === 0) return null;

  // Group by PDF
  const grouped = sources.reduce(
    (acc, source) => {
      if (!acc[source.pdf_name]) {
        acc[source.pdf_name] = 0;
      }
      acc[source.pdf_name]++;
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <Card className="mt-4 p-4">
      <div className="flex items-center gap-2 mb-3">
        <FileText className="h-4 w-4" />
        <span className="text-sm font-medium">Sources</span>
      </div>
      <ul className="text-sm space-y-1">
        {Object.entries(grouped).map(([name, count]) => (
          <li key={name} className="text-muted-foreground">
            • <strong>{name}</strong> ({count} chunks)
          </li>
        ))}
      </ul>
    </Card>
  );
}
