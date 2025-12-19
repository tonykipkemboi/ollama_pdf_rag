/**
 * Custom Ollama provider integration for FastAPI backend
 */

interface Message {
  role: string;
  content: string;
}

interface Source {
  pdf_name: string;
  pdf_id: string;
  chunk_index: number;
}

interface QueryResponse {
  answer: string;
  sources: Source[];
  metadata: {
    model_used: string;
    chunks_retrieved: number;
    pdfs_queried: number;
    reasoning_steps?: string[];
  };
  session_id: string;
  message_id: number;
}

export async function ollamaChat(
  messages: Message[],
  model: string = "mistral:latest",
  pdfIds?: string[]
): Promise<QueryResponse> {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

  // Extract last user message
  const lastMessage = messages[messages.length - 1];
  const question = lastMessage.content;

  // Query backend with optional PDF filter
  const response = await fetch(`${API_URL}/api/v1/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      model,
      session_id: null,
      pdf_ids: pdfIds, // Filter to specific PDFs if provided
    }),
  });

  if (!response.ok) {
    // Try to get error details from response
    let errorDetail = response.statusText;
    try {
      const errorData = await response.json();
      errorDetail = errorData.detail || errorDetail;
    } catch {
      // If parsing fails, use statusText
    }

    throw new Error(errorDetail);
  }

  const data: QueryResponse = await response.json();

  return data;
}

export async function uploadPDF(file: File): Promise<any> {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/api/v1/pdfs/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }

  return response.json();
}

export async function listPDFs(): Promise<any[]> {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

  const response = await fetch(`${API_URL}/api/v1/pdfs`);

  if (!response.ok) {
    throw new Error(`Failed to list PDFs: ${response.statusText}`);
  }

  return response.json();
}

export async function deletePDF(pdfId: string): Promise<void> {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

  const response = await fetch(`${API_URL}/api/v1/pdfs/${pdfId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error(`Delete failed: ${response.statusText}`);
  }
}
