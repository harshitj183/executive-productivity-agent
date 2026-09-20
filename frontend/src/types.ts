export type AgentEventType =
  | 'log'
  | 'tool_call'
  | 'tool_result'
  | 'result'
  | 'validation_result'
  | 'error'
  | 'done'

export interface AgentEvent {
  type: AgentEventType
  message?: string
  content?: string
  tool?: string
  args?: Record<string, unknown>
  step?: string
}

export type MessageRole = 'user' | 'assistant' | 'system'

export interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  timestamp: Date
  logs?: AgentEvent[]
  isStreaming?: boolean
  isError?: boolean
  validationResult?: string
}

export interface StatusResponse {
  status: string
  brief_generated: boolean
  total_llm_calls: number
  conversation_turns: number
}

export type AppState = 'idle' | 'generating_brief' | 'chatting' | 'validating' | 'ready'
