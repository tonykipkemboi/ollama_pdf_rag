// Ollama models for local PDF RAG
export type ChatModel = {
  id: string;
  name: string;
  provider: string;
  description: string;
};

// Fallback models if backend is unreachable
export const chatModels: ChatModel[] = [
  {
    id: "llama3.2:latest",
    name: "Llama 3.2",
    provider: "ollama",
    description: "Lightweight model",
  },
];

// Fetch available Ollama models from backend
export async function fetchOllamaModels(): Promise<ChatModel[]> {
  try {
    const response = await fetch("http://localhost:8001/api/v1/models");
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const models = await response.json();

    if (!models || models.length === 0) {
      console.warn("No models returned from backend, using fallback");
      return chatModels;
    }

    return models.map((model: any) => ({
      id: model.name,
      name: model.name,
      provider: "ollama",
      description: `${(model.size / 1e9).toFixed(1)}GB`,
    }));
  } catch (error) {
    console.error("Failed to fetch Ollama models:", error);
    return chatModels;
  }
}

// Get the default model (first available from Ollama)
export async function getDefaultChatModel(): Promise<string> {
  try {
    const models = await fetchOllamaModels();
    if (models && models.length > 0) {
      return models[0].id;
    }
    return chatModels[0].id;
  } catch (error) {
    console.error("Failed to get default model:", error);
    return chatModels[0].id;
  }
}

// Legacy export for backwards compatibility - but should fetch dynamically
export const DEFAULT_CHAT_MODEL = chatModels[0].id;

// Group models by provider for UI
export const modelsByProvider = chatModels.reduce(
  (acc, model) => {
    if (!acc[model.provider]) {
      acc[model.provider] = [];
    }
    acc[model.provider].push(model);
    return acc;
  },
  {} as Record<string, ChatModel[]>
);
