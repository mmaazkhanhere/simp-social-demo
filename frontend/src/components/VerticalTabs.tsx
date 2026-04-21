interface TabItem {
  id: string;
  label: string;
}

interface Props {
  items: TabItem[];
  active: string;
  onChange: (id: string) => void;
}

export function VerticalTabs({ items, active, onChange }: Props) {
  return (
    <aside className="vertical-tabs">
      {items.map((item) => (
        <button
          key={item.id}
          className={active === item.id ? "tab-button active" : "tab-button"}
          onClick={() => onChange(item.id)}
        >
          {item.label}
        </button>
      ))}
    </aside>
  );
}

