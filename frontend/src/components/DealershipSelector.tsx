import type { Dealership } from "../types";

interface Props {
  dealerships: Dealership[];
  selectedSlug: string;
  onChange: (slug: string) => void;
}

export function DealershipSelector({ dealerships, selectedSlug, onChange }: Props) {
  return (
    <label className="selector-block">
      <span>Dealership</span>
      <select value={selectedSlug} onChange={(event) => onChange(event.target.value)}>
        {dealerships.map((dealership) => (
          <option key={dealership.id} value={dealership.slug}>
            {dealership.name}
          </option>
        ))}
      </select>
    </label>
  );
}

