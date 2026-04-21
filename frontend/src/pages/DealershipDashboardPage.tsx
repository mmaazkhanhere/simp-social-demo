import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { VerticalTabs } from "../components/VerticalTabs";
import { api } from "../services/api";
import type {
  ConversationTableRow,
  LeadTableRow,
  NotificationTableRow,
  SummaryMetric,
  UserTableRow
} from "../types";

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "leads", label: "Leads" },
  { id: "conversations", label: "Conversations" },
  { id: "users", label: "Users" },
  { id: "notifications", label: "Notifications" }
];

export function DealershipDashboardPage() {
  const { dealershipId } = useParams();
  const numericId = Number(dealershipId);
  const [activeTab, setActiveTab] = useState("overview");
  const [name, setName] = useState("");
  const [metrics, setMetrics] = useState<SummaryMetric[]>([]);
  const [leads, setLeads] = useState<LeadTableRow[]>([]);
  const [conversations, setConversations] = useState<ConversationTableRow[]>([]);
  const [notifications, setNotifications] = useState<NotificationTableRow[]>([]);
  const [users, setUsers] = useState<UserTableRow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!numericId) {
      setError("Invalid dealership id");
      setIsLoading(false);
      return;
    }

    let cancelled = false;

    async function loadDealershipDashboard() {
      setIsLoading(true);
      setError("");

      try {
        const [summary, leadsData, conversationData, notificationData, userData] = await Promise.all([
          api.getDealershipDashboard(numericId),
          api.getDealershipLeads(numericId),
          api.getDealershipConversations(numericId),
          api.getDealershipNotifications(numericId),
          api.getDealershipUsers(numericId)
        ]);

        if (cancelled) {
          return;
        }

        setName(summary.dealership_name);
        setMetrics(summary.metrics);
        setLeads(leadsData);
        setConversations(conversationData);
        setNotifications(notificationData);
        setUsers(userData);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unable to load dealership dashboard");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadDealershipDashboard();

    return () => {
      cancelled = true;
    };
  }, [numericId]);

  return (
    <main className="page dashboard-page">
      <header className="dashboard-topbar">
        <div>
          <h1>{name || "Dealership CRM"}</h1>
          <p className="muted dashboard-subtitle">Dealership-level CRM view</p>
        </div>
        <div className="dashboard-actions">
          <Link to="/" className="action-link">
            Back to Home
          </Link>
          <Link to="/dashboard" className="action-link action-link-secondary">
            SimpSocial Dashboard
          </Link>
        </div>
      </header>

      {error ? <p className="error">{error}</p> : null}

      <section className="dashboard-layout">
        <VerticalTabs items={TABS} active={activeTab} onChange={setActiveTab} />
        <div className="card dashboard-content">
          {isLoading ? <p className="muted">Loading dealership dashboard...</p> : null}

          {activeTab === "overview" ? (
            <div className="metrics-grid">
              {metrics.map((metric) => (
                <article key={metric.label} className="metric-card">
                  <h4>{metric.label}</h4>
                  <strong>{metric.value}</strong>
                </article>
              ))}
            </div>
          ) : null}

          {activeTab === "leads" ? <GenericTable rows={leads} /> : null}
          {activeTab === "conversations" ? <GenericTable rows={conversations} /> : null}
          {activeTab === "users" ? <GenericTable rows={users} /> : null}
          {activeTab === "notifications" ? <GenericTable rows={notifications} /> : null}
        </div>
      </section>
    </main>
  );
}

function GenericTable<T extends object>({ rows }: { rows: T[] }) {
  if (rows.length === 0) {
    return <p className="muted">No records yet.</p>;
  }

  const keys = Object.keys(rows[0]) as Array<keyof T>;

  return (
    <div className="table-shell">
      <table className="table">
        <thead>
          <tr>
            {keys.map((key) => (
              <th key={String(key)}>{String(key)}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={idx}>
              {keys.map((key) => (
                <td key={String(key)}>{String(row[key] ?? "-")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
