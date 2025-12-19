import { ollamaChat } from "@/lib/ai/provider";
import { getDefaultChatModel } from "@/lib/ai/models";
import { createUIMessageStream, createUIMessageStreamResponse } from "ai";
import { auth } from "@/app/(auth)/auth";
import {
  getChatById,
  saveChat,
  saveMessages,
} from "@/lib/db/queries";
import { generateUUID } from "@/lib/utils";

export const maxDuration = 60;

interface MessagePart {
  type: string;
  text?: string;
  url?: string;
  name?: string;
  mediaType?: string;
}

interface PostRequestBody {
  id: string;
  message: {
    id?: string;
    role: string;
    parts: MessagePart[];
  };
  selectedChatModel?: string;
  selectedVisibilityType?: string;
  selectedPdfIds?: string[]; // PDFs selected by user
}

// Simple question classifier - checks if question likely needs document context
function needsDocumentContext(question: string): boolean {
  const documentKeywords = [
    "document", "pdf", "file", "page", "section", "chapter",
    "according to", "based on", "what does", "what is", "explain",
    "summarize", "summary", "tell me about", "describe", "definition",
    "content", "text", "says", "mentioned", "states", "written",
    "this", "the document", "the file", "the pdf", "uploaded",
    "in the", "from the", "about the"
  ];
  
  const lowerQuestion = question.toLowerCase();
  return documentKeywords.some(keyword => lowerQuestion.includes(keyword));
}

export async function POST(request: Request) {
  try {
    const body: PostRequestBody = await request.json();
    const chatId = body.id;

    // Get user session
    const session = await auth();
    if (!session?.user?.id) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }
    const userId = session.user.id;

    // Use selected model or fetch default from available Ollama models
    const selectedChatModel = body.selectedChatModel || await getDefaultChatModel();
    console.log("Using model:", selectedChatModel);

    console.log("Received message:", JSON.stringify(body.message, null, 2));

    // Extract text content from message parts
    const textPart = body.message.parts.find((p) => p.type === "text");
    const textContent = textPart?.text || "";

    if (!textContent) {
      return new Response(
        JSON.stringify({ error: "No text content found in message" }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // Check if chat exists, create if not
    let chat = await getChatById({ id: chatId });
    const isNewChat = !chat;

    if (!chat) {
      // Create new chat with first message as title (truncated)
      const title = textContent.slice(0, 100) + (textContent.length > 100 ? "..." : "");
      await saveChat({
        id: chatId,
        userId,
        title,
        visibility: (body.selectedVisibilityType as "private" | "public") || "private",
      });
      console.log("Created new chat:", chatId);
    }

    // Use PDF IDs from frontend (user's selection)
    const selectedPdfIds = body.selectedPdfIds || [];
    console.log("Selected PDF IDs from frontend:", selectedPdfIds);

    // Check if question needs document context
    const questionNeedsContext = needsDocumentContext(textContent);
    console.log("Question needs document context:", questionNeedsContext);

    // Save user message
    const userMessageId = body.message.id || generateUUID();
    await saveMessages({
      messages: [{
        id: userMessageId,
        chatId,
        role: "user",
        content: textContent, // Legacy field
        parts: JSON.stringify(body.message.parts),
        createdAt: new Date(),
      }],
    });
    console.log("Saved user message:", userMessageId);

    // Determine if we should use RAG or general chat
    const useRAG = selectedPdfIds.length > 0;
    const noPdfsButNeedsContext = selectedPdfIds.length === 0 && questionNeedsContext;

    console.log("Mode:", useRAG ? "RAG" : "General Chat");
    console.log("No PDFs but needs context:", noPdfsButNeedsContext);

    // Build message history (for now, just the current message)
    const messages = [{ role: body.message.role, content: textContent }];

    let result;
    let formattedResponse: string;
    let reasoningSteps: string[] = [];

    if (noPdfsButNeedsContext) {
      // Warn user that no PDFs are selected
      console.log("Warning: Question seems to need document context but no PDFs selected");
      formattedResponse = `⚠️ **No documents selected**

It looks like your question might be about a document, but you haven't selected any PDFs to search.

**To get answers from your documents:**
1. Look at the sidebar on the left
2. Check the boxes next to the PDFs you want to use
3. Then ask your question again

**If you just want to chat without documents**, feel free to ask general questions and I'll respond based on my knowledge!

---

*Your question was: "${textContent}"*`;
      
      result = {
        answer: formattedResponse,
        sources: [],
        metadata: { reasoning_steps: ["⚠️ No PDFs selected for document query"] }
      };
    } else if (useRAG) {
      // Use RAG with selected PDFs
      console.log("Sending to backend:", {
        question: textContent,
        model: selectedChatModel,
        pdfIds: selectedPdfIds,
      });

      console.log("Calling ollamaChat with RAG...");
      result = await ollamaChat(messages, selectedChatModel, selectedPdfIds);
      
      // Format response with sources
      formattedResponse = `${result.answer}\n\n**Sources:**\n${result.sources
        .map((s: any) => `- ${s.pdf_name} (chunk ${s.chunk_index})`)
        .join("\n")}`;
      reasoningSteps = result.metadata.reasoning_steps || [];
    } else {
      // General chat without RAG
      console.log("Calling ollamaChat for general chat (no RAG)...");
      result = await ollamaChat(messages, selectedChatModel, undefined);
      formattedResponse = result.answer;
      reasoningSteps = result.metadata.reasoning_steps || [];
    }
    console.log("Received result from backend:", {
      answerLength: result.answer.length,
      sourcesCount: result.sources?.length || 0,
      hasReasoningSteps: !!result.metadata?.reasoning_steps,
      reasoningStepsCount: result.metadata?.reasoning_steps?.length || 0,
    });

    console.log("Reasoning steps:", reasoningSteps);
    console.log("Formatted response length:", formattedResponse.length);
    console.log("First 200 chars of response:", formattedResponse.substring(0, 200));

    // Save assistant message
    const assistantMessageId = generateUUID();
    const assistantParts = [
      { type: "text", text: formattedResponse },
    ];

    // Add reasoning parts if present
    if (reasoningSteps.length > 0) {
      assistantParts.unshift({
        type: "reasoning",
        text: reasoningSteps.join("\n"),
      } as any);
    }

    await saveMessages({
      messages: [{
        id: assistantMessageId,
        chatId,
        role: "assistant",
        content: formattedResponse, // Legacy field
        parts: JSON.stringify(assistantParts),
        createdAt: new Date(),
      }],
    });
    console.log("Saved assistant message:", assistantMessageId);

    // Create a UI message stream using AI SDK
    console.log("Creating UI message stream...");
    const textId = "text-1";

    const messageStream = createUIMessageStream({
      execute: async ({ writer }) => {
        // Write reasoning steps progressively with delay for streaming effect
        if (reasoningSteps && reasoningSteps.length > 0) {
          console.log("Writing reasoning steps progressively:", reasoningSteps.length);
          const reasoningId = "reasoning-1";

          writer.write({ type: "reasoning-start", id: reasoningId });

          for (const step of reasoningSteps) {
            writer.write({
              type: "reasoning-delta",
              id: reasoningId,
              delta: step + "\n",
            });
            // Small delay between reasoning steps for progressive display
            await new Promise(resolve => setTimeout(resolve, 150));
          }

          writer.write({ type: "reasoning-end", id: reasoningId });
        }

        // Write sources as custom data (only for RAG mode)
        const sources = result.sources || [];
        if (sources.length > 0) {
          console.log("Writing sources:", sources.length);
          writer.write({
            type: "data-sources" as any,
            data: sources,
          });
        }

        // Write text content progressively with text chunks
        console.log("Writing text content progressively...");
        writer.write({ type: "text-start", id: textId });

        const words = formattedResponse.split(" ");
        for (let i = 0; i < words.length; i++) {
          writer.write({
            type: "text-delta",
            id: textId,
            delta: words[i] + " ",
          });
          // Delay every few words for smoother streaming
          if (i % 3 === 0) {
            await new Promise(resolve => setTimeout(resolve, 30));
          }
        }

        writer.write({ type: "text-end", id: textId });
        console.log("Stream write complete");
      },
    });

    return createUIMessageStreamResponse({ stream: messageStream });
  } catch (error) {
    console.error("Chat error:", error);

    // Extract error message
    const errorMessage = error instanceof Error ? error.message : "Unknown error occurred";
    const errorText = `❌ **Error**: ${errorMessage}\n\nPlease check:\n- Model is installed and running\n- PDF documents are uploaded\n- Backend service is accessible`;

    // Return error as a UI message stream
    const errorStream = createUIMessageStream({
      execute: async ({ writer }) => {
        // Write error chunk
        writer.write({
          type: "error",
          errorText: errorMessage,
        });

        // Write error text progressively
        const textId = "error-text-1";
        writer.write({ type: "text-start", id: textId });

        const words = errorText.split(" ");
        for (let i = 0; i < words.length; i++) {
          writer.write({
            type: "text-delta",
            id: textId,
            delta: words[i] + " ",
          });
          // Delay every few words
          if (i % 3 === 0) {
            await new Promise(resolve => setTimeout(resolve, 30));
          }
        }

        writer.write({ type: "text-end", id: textId });
      },
    });

    return createUIMessageStreamResponse({ stream: errorStream });
  }
}
