interface Props {
  stage: string;
  score?: string;
}

export function StatusBadge({ stage, score }: Props) {
  return (
    <div className="status-row">
      <span className="badge">Stage: {stage}</span>
      <span className="badge">Score: {score ?? "n/a"}</span>
    </div>
  );
}

