import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { DealershipSelector } from "../components/DealershipSelector";
import { LanguageSelector } from "../components/LanguageSelector";
import { MessageInput } from "../components/MessageInput";
import { MessageList } from "../components/MessageList";
import { api } from "../services/api";
import type { Conversation, Dealership, Language } from "../types";

export function ChatPage() {
  const { dealershipSlug } = useParams();
  const navigate = useNavigate();

  const [dealerships, setDealerships] = useState<Dealership[]>([]);
  const [selectedSlug, setSelectedSlug] = useState("");
  const [language, setLanguage] = useState<Language>("english");
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const selectedDealership = useMemo(
    () => dealerships.find((dealership) => dealership.slug === selectedSlug) ?? null,
    [dealerships, selectedSlug]
  );

  useEffect(() => {
    let cancelled = false;
    async function loadDealerships() {
      try {
        const data = await api.listDealerships();
        if (cancelled) return;
        setDealerships(data);
        const fallbackSlug = data[0]?.slug ?? "";
        const requestedSlug = dealershipSlug ?? fallbackSlug;
        const valid = data.some((item) => item.slug === requestedSlug);
        const resolvedSlug = valid ? requestedSlug : fallbackSlug;
        setSelectedSlug(resolvedSlug);
        if (dealershipSlug && !valid) {
          navigate(`/d/${resolvedSlug}`, { replace: true });
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load dealerships");
      }
    }
    void loadDealerships();
    return () => {
      cancelled = true;
    };
  }, [dealershipSlug, navigate]);

  useEffect(() => {
    if (!selectedDealership) return;
    setLanguage(selectedDealership.language_default || "english");
  }, [selectedDealership]);

  useEffect(() => {
    if (!selectedDealership) return;
    const dealership = selectedDealership;
    let cancelled = false;
    async function createFreshConversation() {
      setLoading(true);
      setError("");
      try {
        const data = await api.createConversation({
          dealership_id: dealership.id,
          dealership_name: dealership.name,
          language
        });
        if (!cancelled) {
          setConversation(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to create conversation");
          setConversation(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }
    void createFreshConversation();
    return () => {
      cancelled = true;
    };
  }, [selectedDealership, language]);

  function handleSelectDealership(slug: string) {
    setSelectedSlug(slug);
    navigate(`/d/${slug}`);
  }

  async function handleSend(content: string) {
    if (!conversation || !selectedDealership) return;
    setLoading(true);
    setError("");
    try {
      const response = await api.sendMessage(conversation.id, selectedDealership.id, content);
      setConversation(response.conversation);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
    } finally {
      setLoading(false);
    }
  }

  async function startNewConversation() {
    if (!selectedDealership) return;
    setLoading(true);
    try {
      const data = await api.createConversation({
        dealership_id: selectedDealership.id,
        dealership_name: selectedDealership.name,
        language
      });
      setConversation(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reset conversation");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <header className="chat-header">
        <h1>{selectedDealership ? `${selectedDealership.name} Assistant` : "Dealership Assistant"}</h1>
        <div className="selector-row">
          <DealershipSelector dealerships={dealerships} selectedSlug={selectedSlug} onChange={handleSelectDealership} />
          <LanguageSelector value={language} onChange={setLanguage} />
          <button onClick={() => void startNewConversation()} disabled={loading} className="ghost-button">
            Fresh Conversation
          </button>
        </div>
      </header>

      {error ? <p className="error">{error}</p> : null}

      <section className="chat-layout">
        <div className="chat-panel card">
          <MessageList messages={conversation?.messages ?? []} />
          <MessageInput onSend={handleSend} disabled={loading || !conversation} />
        </div>
      </section>
    </main>
  );
}
