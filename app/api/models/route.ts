import { MODEL_DEFAULT } from "@/lib/config"
import { getAllModels, refreshModelsCache } from "@/lib/models"
import { bedrockModels } from "@/lib/models/data/bedrock"
import type { ModelConfig } from "@/lib/models/types"
import { NextResponse } from "next/server"

function getActiveProvider(): "bedrock" | "openai" {
  return process.env.LLM_PROVIDER?.toLowerCase() === "openai"
    ? "openai"
    : "bedrock"
}

function uniqueModelIds(modelIds: string[]): string[] {
  return Array.from(
    new Set(modelIds.map((modelId) => modelId.trim()).filter(Boolean))
  )
}

function buildOpenAIModels(): ModelConfig[] {
  const defaultModel = process.env.OPENAI_DEFAULT_MODEL || "gpt-4o-mini"
  const availableModels = uniqueModelIds([
    ...(process.env.OPENAI_AVAILABLE_MODELS || "").split(","),
    defaultModel,
  ])

  const defaultPlaceholder: ModelConfig = {
    id: MODEL_DEFAULT,
    name: defaultModel,
    provider: "OpenAI Compatible",
    providerId: "openai",
    baseProviderId: "openai",
    description: "Configured default model for the active OpenAI-compatible endpoint",
    icon: "openai",
    accessible: true,
  }

  const runtimeModels = availableModels.map<ModelConfig>((modelId) => ({
    id: modelId,
    name: modelId,
    provider: "OpenAI Compatible",
    providerId: "openai",
    baseProviderId: "openai",
    description: "Available through the configured OpenAI-compatible endpoint",
    icon: "openai",
    accessible: true,
    openSource: modelId.toLowerCase().includes("oss"),
  }))

  return [defaultPlaceholder, ...runtimeModels]
}

async function buildBedrockModels(): Promise<ModelConfig[]> {
  const allModels = await getAllModels()
  const configuredDefaultId =
    process.env.BEDROCK_DEFAULT_MODEL || bedrockModels[0]?.id || MODEL_DEFAULT
  const configuredDefault =
    bedrockModels.find((model) => model.id === configuredDefaultId) ||
    allModels.find((model) => model.id === configuredDefaultId)

  const defaultPlaceholder: ModelConfig = configuredDefault
    ? {
        ...configuredDefault,
        id: MODEL_DEFAULT,
        description: `Configured default model (${configuredDefault.id})`,
        accessible: true,
      }
    : {
        id: MODEL_DEFAULT,
        name: configuredDefaultId,
        provider: "Amazon Bedrock",
        providerId: "bedrock",
        baseProviderId: "bedrock",
        description: "Configured default Bedrock model",
        icon: "bedrock",
        accessible: true,
      }

  return [
    defaultPlaceholder,
    ...allModels.map((model) => ({
      ...model,
      accessible: true,
    })),
  ]
}

async function getRuntimeModels(): Promise<ModelConfig[]> {
  if (getActiveProvider() === "openai") {
    return buildOpenAIModels()
  }

  return buildBedrockModels()
}

export async function GET() {
  try {
    const models = await getRuntimeModels()

    return new Response(JSON.stringify({ models }), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
      },
    })
  } catch (error) {
    console.error("Error fetching models:", error)
    return new Response(JSON.stringify({ error: "Server error occurred" }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
      },
    })
  }
}

export async function POST() {
  try {
    refreshModelsCache()
    const models = await getRuntimeModels()

    return NextResponse.json({
      message: "Models cache refreshed",
      models,
      timestamp: new Date().toISOString(),
      count: models.length,
    })
  } catch (error) {
    console.error("Failed to refresh models:", error)
    return NextResponse.json(
      { error: "Server error occurred" },
      { status: 500 }
    )
  }
}
