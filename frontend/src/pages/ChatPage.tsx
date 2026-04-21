import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { DealershipSelector } from "../components/DealershipSelector";
import { LanguageSelector } from "../components/LanguageSelector";
import { MessageInput } from "../components/MessageInput";
import { MessageList } from "../components/MessageList";
import { api } from "../services/api";
import type { Conversation, Dealership, Language, Message } from "../types";

export function ChatPage() {
  const { dealershipSlug } = useParams();
  const navigate = useNavigate();

  const [dealerships, setDealerships] = useState<Dealership[]>([]);
  const [selectedSlug, setSelectedSlug] = useState("");
  const [language, setLanguage] = useState<Language>("english");
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [isCreatingConversation, setIsCreatingConversation] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [optimisticMessages, setOptimisticMessages] = useState<Message[]>([]);
  const [error, setError] = useState("");

  const selectedDealership = dealerships.find((dealership) => dealership.slug === selectedSlug) ?? null;

  useEffect(() => {
    let cancelled = false;

    async function loadDealerships() {
      try {
        const data = await api.listDealerships();
        if (cancelled) {
          return;
        }

        setDealerships(data);
        const fallbackSlug = data[0]?.slug ?? "";
        const requestedSlug = dealershipSlug ?? fallbackSlug;
        const resolvedSlug = data.some((item) => item.slug === requestedSlug) ? requestedSlug : fallbackSlug;

        setSelectedSlug(resolvedSlug);

        if (dealershipSlug && resolvedSlug !== dealershipSlug) {
          navigate(`/d/${resolvedSlug}`, { replace: true });
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unable to load dealerships");
        }
      }
    }

    void loadDealerships();

    return () => {
      cancelled = true;
    };
  }, [dealershipSlug, navigate]);

  useEffect(() => {
    if (!selectedDealership) {
      return;
    }

    setLanguage(selectedDealership.language_default || "english");
  }, [selectedDealership]);

  async function createConversationForDealership(dealership: Dealership, nextLanguage: Language) {
    setIsCreatingConversation(true);
    setOptimisticMessages([]);
    setIsSending(false);
    setError("");

    try {
      const nextConversation = await api.createConversation({
        dealership_id: dealership.id,
        dealership_name: dealership.name,
        language: nextLanguage
      });
      setConversation(nextConversation);
    } catch (err) {
      setConversation(null);
      setError(err instanceof Error ? err.message : "Failed to create conversation");
    } finally {
      setIsCreatingConversation(false);
    }
  }

  useEffect(() => {
    if (!selectedDealership) {
      return;
    }

    const dealership = selectedDealership;
    let cancelled = false;

    async function bootstrapConversation() {
      try {
        setIsCreatingConversation(true);
        setOptimisticMessages([]);
        setIsSending(false);
        setError("");

        const nextConversation = await api.createConversation({
          dealership_id: dealership.id,
          dealership_name: dealership.name,
          language
        });

        if (!cancelled) {
          setConversation(nextConversation);
        }
      } catch (err) {
        if (!cancelled) {
          setConversation(null);
          setError(err instanceof Error ? err.message : "Failed to create conversation");
        }
      } finally {
        if (!cancelled) {
          setIsCreatingConversation(false);
        }
      }
    }

    void bootstrapConversation();

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
    const pendingMessage: Message = {
      id: -Date.now(),
      role: "user",
      content,
      created_at: new Date().toISOString()
    };
    setOptimisticMessages((prev) => [...prev, pendingMessage]);
    setIsSending(true);
    setError("");
    try {
      const response = await api.sendMessage(conversation.id, selectedDealership.id, content);
      setConversation(response.conversation);
      setOptimisticMessages([]);
    } catch (err) {
      setOptimisticMessages((prev) => prev.filter((message) => message.id !== pendingMessage.id));
      setError(err instanceof Error ? err.message : "Failed to send message");
    } finally {
      setIsSending(false);
    }
  }

  async function startNewConversation() {
    if (!selectedDealership) {
      return;
    }

    await createConversationForDealership(selectedDealership, language);
  }

  const messagesForDisplay = [...(conversation?.messages ?? []), ...optimisticMessages];

  return (
    <main className="page">
      <header className="chat-header">
        <h1>{selectedDealership ? `${selectedDealership.name} Assistant` : "Dealership Assistant"}</h1>
        <div className="selector-row">
          <DealershipSelector dealerships={dealerships} selectedSlug={selectedSlug} onChange={handleSelectDealership} />
          <LanguageSelector value={language} onChange={setLanguage} />
          <button onClick={() => void startNewConversation()} disabled={isCreatingConversation || isSending} className="ghost-button">
            Fresh Conversation
          </button>
        </div>
      </header>

      {error ? <p className="error">{error}</p> : null}

      <section className="chat-layout">
        <div className="chat-panel card">
          <MessageList
            messages={messagesForDisplay}
            isAssistantTyping={isSending}
            assistantLabel={selectedDealership ? `${selectedDealership.name} Assistant` : "Assistant"}
          />
          <MessageInput onSend={handleSend} disabled={isCreatingConversation || isSending || !conversation} />
        </div>
      </section>
    </main>
  );
}
