import type {
  Conversation,
  Dealership,
  DealershipRollup,
  Language,
  SummaryMetric
} from "../types";

const API_BASE = "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    }
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Request failed");
  }
  return (await response.json()) as T;
}

export const api = {
  listDealerships: () => request<Dealership[]>("/api/dealerships"),
  getDealershipBySlug: (slug: string) => request<Dealership>(`/api/dealerships/${slug}`),
  createConversation: (payload: {
    dealership_id: number;
    dealership_name: string;
    language: Language;
    user_name?: string;
    phone?: string;
  }) => request<Conversation>("/api/conversations", { method: "POST", body: JSON.stringify(payload) }),
  getConversation: (conversationId: number, dealershipId: number) =>
    request<Conversation>(`/api/conversations/${conversationId}?dealership_id=${dealershipId}`),
  sendMessage: (conversationId: number, dealershipId: number, content: string) =>
    request<{ conversation: Conversation }>(
      `/api/conversations/${conversationId}/messages?dealership_id=${dealershipId}`,
      {
        method: "POST",
        body: JSON.stringify({ content })
      }
    ),
  getDashboardSummary: () => request<{ metrics: SummaryMetric[] }>("/api/dashboard/summary"),
  getDashboardDealerships: () => request<DealershipRollup[]>("/api/dashboard/dealerships"),
  getDealershipDashboard: (dealershipId: number) =>
    request<{ dealership_id: number; dealership_name: string; metrics: SummaryMetric[] }>(
      `/api/dashboard/${dealershipId}`
    ),
  getDealershipLeads: (dealershipId: number) => request<Array<Record<string, string | number | null>>>(`/api/dashboard/${dealershipId}/leads`),
  getDealershipConversations: (dealershipId: number) =>
    request<Array<Record<string, string | number | null>>>(`/api/dashboard/${dealershipId}/conversations`),
  getDealershipNotifications: (dealershipId: number) =>
    request<Array<Record<string, string | number | null>>>(`/api/dashboard/${dealershipId}/notifications`),
  getDealershipUsers: (dealershipId: number) =>
    request<Array<Record<string, string | number | null>>>(`/api/dashboard/${dealershipId}/users`)
};
