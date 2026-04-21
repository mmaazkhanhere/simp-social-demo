import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { VerticalTabs } from "../components/VerticalTabs";
import { api } from "../services/api";
import type { SummaryMetric } from "../types";

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
  const [leads, setLeads] = useState<Array<Record<string, string | number | null>>>([]);
  const [conversations, setConversations] = useState<Array<Record<string, string | number | null>>>([]);
  const [notifications, setNotifications] = useState<Array<Record<string, string | number | null>>>([]);
  const [users, setUsers] = useState<Array<Record<string, string | number | null>>>([]);

  useEffect(() => {
    if (!numericId) return;
    void Promise.all([
      api.getDealershipDashboard(numericId),
      api.getDealershipLeads(numericId),
      api.getDealershipConversations(numericId),
      api.getDealershipNotifications(numericId),
      api.getDealershipUsers(numericId)
    ]).then(([summary, leadsData, convoData, notificationData, usersData]) => {
      setName(summary.dealership_name);
      setMetrics(summary.metrics);
      setLeads(leadsData);
      setConversations(convoData);
      setNotifications(notificationData);
      setUsers(usersData);
    });
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
      <section className="dashboard-layout">
        <VerticalTabs items={TABS} active={activeTab} onChange={setActiveTab} />
        <div className="card dashboard-content">
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

function GenericTable({ rows }: { rows: Array<Record<string, string | number | null>> }) {
  const keys = rows.length > 0 ? Object.keys(rows[0]) : [];
  if (rows.length === 0) return <p className="muted">No records yet.</p>;
  return (
    <div className="table-shell">
      <table className="table">
        <thead>
          <tr>
            {keys.map((key) => (
              <th key={key}>{key}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={idx}>
              {keys.map((key) => (
                <td key={key}>{String(row[key] ?? "-")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
