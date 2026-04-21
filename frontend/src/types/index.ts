export type Language = "english" | "spanish";

export interface Dealership {
  id: number;
  name: string;
  slug: string;
  language_default: Language;
}

export interface Message {
  id: number;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}

export interface Lead {
  id: number;
  dealership_id: number;
  conversation_id: number;
  name: string | null;
  phone: string | null;
  employment_status: string | null;
  monthly_income_range: string | null;
  down_payment_range: string | null;
  timeline: string | null;
  intent_score: "hot" | "warm" | "cold";
  is_application_ready: boolean;
}

export interface Conversation {
  id: number;
  dealership_id: number;
  status: string;
  stage: string;
  language: Language;
  messages: Message[];
  lead: Lead | null;
}

export interface SummaryMetric {
  label: string;
  value: number;
}

export interface DashboardSummaryResponse {
  metrics: SummaryMetric[];
}

export interface DealershipRollup {
  dealership_id: number;
  dealership_name: string;
  conversations: number;
  leads: number;
  users: number;
}

export interface DealershipDashboardResponse {
  dealership_id: number;
  dealership_name: string;
  metrics: SummaryMetric[];
}

export interface LeadTableRow {
  name: string;
  phone: string;
  employment_status: string;
  monthly_income_range: string;
  down_payment_range: string;
  timeline: string;
  intent_score: string;
}

export interface ConversationTableRow {
  id: number;
  status: string;
  stage: string;
  language: string;
}

export interface NotificationTableRow {
  id: number;
  event_type: string;
  delivery_status: string;
  sent_at: string;
}

export interface UserTableRow {
  name: string;
  phone: string;
  employment_status: string;
  monthly_income_range: string;
  down_payment_range: string;
  timeline: string;
  intent_score: string;
}
