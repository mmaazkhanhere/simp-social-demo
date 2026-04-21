import type { Lead } from "../types";

interface Props {
  lead: Lead | null;
}

const FIELDS: Array<keyof Lead> = [
  "name",
  "phone",
  "employment_status",
  "monthly_income_range",
  "down_payment_range",
  "timeline",
  "intent_score"
];

export function LeadSummaryCard({ lead }: Props) {
  return (
    <section className="card">
      <h3>Lead Summary</h3>
      {!lead ? <p className="muted">No lead captured yet.</p> : null}
      {lead
        ? FIELDS.map((field) => (
            <div key={field} className="field-row">
              <strong>{field}</strong>
              <span>{String(lead[field] ?? "-")}</span>
            </div>
          ))
        : null}
    </section>
  );
}

