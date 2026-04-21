import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { VerticalTabs } from "../components/VerticalTabs";
import { api } from "../services/api";
import type { DealershipRollup, SummaryMetric } from "../types";

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "dealerships", label: "Dealerships" },
  { id: "conversations", label: "Conversations" },
  { id: "leads", label: "Leads" },
  { id: "users", label: "Users" },
  { id: "notifications", label: "Notifications" }
];

export function DashboardPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [metrics, setMetrics] = useState<SummaryMetric[]>([]);
  const [dealerships, setDealerships] = useState<DealershipRollup[]>([]);

  useEffect(() => {
    void Promise.all([api.getDashboardSummary(), api.getDashboardDealerships()]).then(([summary, rows]) => {
      setMetrics(summary.metrics);
      setDealerships(rows);
    });
  }, []);

  return (
    <main className="page dashboard-page">
      <header className="dashboard-topbar">
        <div>
          <h1>SimpSocial Dashboard</h1>
          <p className="muted dashboard-subtitle">Performance view across all dealerships</p>
        </div>
        <div className="dashboard-actions">
          <Link to="/" className="action-link">
            Back to Home
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

          {activeTab === "dealerships" ? (
            <div className="table-shell">
              <table className="table">
                <thead>
                  <tr>
                    <th>Dealership</th>
                    <th>Conversations</th>
                    <th>Leads</th>
                    <th>Users</th>
                    <th>CRM</th>
                  </tr>
                </thead>
                <tbody>
                  {dealerships.map((row) => (
                    <tr key={row.dealership_id}>
                      <td>{row.dealership_name}</td>
                      <td>{row.conversations}</td>
                      <td>{row.leads}</td>
                      <td>{row.users}</td>
                      <td>
                        <Link to={`/dashboard/${row.dealership_id}`} className="action-link action-link-inline">
                          Open
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}

          {activeTab !== "overview" && activeTab !== "dealerships" ? (
            <p className="muted">This tab uses aggregate metrics in MVP and can be expanded later.</p>
          ) : null}
        </div>
      </section>
    </main>
  );
}
