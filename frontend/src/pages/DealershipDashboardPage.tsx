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

  useEffect(() => {
    if (!numericId) return;
    void Promise.all([
      api.getDealershipDashboard(numericId),
      api.getDealershipLeads(numericId),
      api.getDealershipConversations(numericId),
      api.getDealershipNotifications(numericId)
    ]).then(([summary, leadsData, convoData, notificationData]) => {
      setName(summary.dealership_name);
      setMetrics(summary.metrics);
      setLeads(leadsData);
      setConversations(convoData);
      setNotifications(notificationData);
    });
  }, [numericId]);

  return (
    <main className="page dashboard-page">
      <header className="subheader">
        <h1>{name || "Dealership CRM"}</h1>
        <Link to="/dashboard">Back to SimpSocial dashboard</Link>
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
          {activeTab === "users" ? <p className="muted">User list can be added from contacts endpoint in next iteration.</p> : null}
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
  );
}

