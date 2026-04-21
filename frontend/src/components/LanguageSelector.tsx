import type { Language } from "../types";

interface Props {
  value: Language;
  onChange: (language: Language) => void;
}

export function LanguageSelector({ value, onChange }: Props) {
  return (
    <label className="selector-block">
      <span>Language</span>
      <select value={value} onChange={(event) => onChange(event.target.value as Language)}>
        <option value="english">English</option>
        <option value="spanish">Spanish</option>
      </select>
    </label>
  );
}

