export type VoiceState =
  | "IDLE"
  | "CONNECTING"
  | "CONNECTED"
  | "LISTENING"
  | "PROCESSING"
  | "SPEAKING"
  | "TOOL_CALL"
  | "ERROR"
  | "ENDING"
  | "ENDED";

export interface ChatMessage {
  id: string;
  speaker: "user" | "assistant" | "system";
  text: string;
  timestamp: string;
}

export interface AgentActivityEvent {
  id: string;
  conversation_id?: string;
  event_type: "tool_started" | "tool_completed" | "tool_failed" | "state_changed" | string;
  tool_name?: string;
  status: "running" | "success" | "failed" | "INFO" | string;
  duration_ms?: number;
  payload?: any;
  created_at: string;
}

export interface CustomerContext {
  id?: string;
  name?: string;
  email?: string;
  company?: string;
  role?: string;
  intent?: string;
  use_case?: string;
  requirements?: string;
  timeline?: string;
  budget_range?: string;
  qualification_score: number;
  lead_status: "NEW" | "QUALIFYING" | "QUALIFIED" | "MEETING_BOOKED" | "HANDOFF" | "CLOSED" | string;
  qualification_details?: {
    qualification_score: number;
    reasons: string[];
    missing_fields: string[];
    recommended_status: string;
  };
}

export interface BookingDetails {
  booking_id: string;
  slot_id: string;
  lead_id?: string;
  name: string;
  email: string;
  company?: string;
  meeting_type?: string;
  confirmed_start: string;
  confirmed_end: string;
  status: string;
}

export interface ConversationSummary {
  customer_name?: string | null;
  company?: string | null;
  email?: string | null;
  intent?: string | null;
  use_case?: string | null;
  requirements: string[];
  timeline?: string | null;
  budget_range?: string | null;
  qualification_score: number;
  lead_status: string;
  next_action?: string | null;
}

export interface CalendarSlot {
  id: string;
  start_time: string;
  end_time: string;
  is_booked: boolean;
}

export interface ServiceItem {
  service_id: string;
  name: string;
  category: string;
  description: string;
  ideal_for: string;
  capabilities: string[];
  starting_price: string;
  pricing_notes: string;
  delivery_range: string;
  status: string;
}
