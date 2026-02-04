import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

const THREAD = [
  {
    id: 1,
    role: "assistant",
    content:
      "Ask in natural language and I will respond with the data pulled from your database."
  },
  {
    id: 2,
    role: "user",
    content: "Show weekly revenue for the last 6 weeks."
  },
  {
    id: 3,
    role: "assistant",
    data: {
      title: "Weekly Revenue",
      columns: ["week", "revenue"],
      rows: [
        ["2024-08-05", "$182,420"],
        ["2024-08-12", "$175,300"],
        ["2024-08-19", "$194,880"],
        ["2024-08-26", "$201,550"],
        ["2024-09-02", "$189,230"],
        ["2024-09-09", "$207,910"]
      ],
      query:
        "SELECT date_trunc('week', order_date) AS week, SUM(revenue) AS revenue\n" +
        "FROM sales\n" +
        "WHERE order_date >= CURRENT_DATE - INTERVAL '6 weeks'\n" +
        "GROUP BY 1\n" +
        "ORDER BY 1;"
    }
  },
  {
    id: 4,
    role: "user",
    content: "Which products are the most returned?"
  },
  {
    id: 5,
    role: "assistant",
    data: {
      title: "Top Returns",
      columns: ["product", "returns"],
      rows: [
        ["Aura Air Purifier", "112"],
        ["Pulse Fitness Tracker", "97"],
        ["Nimbus Speaker", "83"],
        ["Glow Desk Lamp", "79"],
        ["Zen Mattress", "74"]
      ],
      query:
        "SELECT product_name AS product, COUNT(*) AS returns\n" +
        "FROM returns\n" +
        "GROUP BY 1\n" +
        "ORDER BY returns DESC\n" +
        "LIMIT 5;"
    }
  }
];

export default function App() {
  const [openQueryId, setOpenQueryId] = useState(null);

  const handleToggleQuery = (messageId) => {
    setOpenQueryId((current) => (current === messageId ? null : messageId));
  };

  return (
    <div className="min-h-screen">
      <div className="flex min-h-screen">
        <aside className="hidden w-112 flex-col border-r border-border/70 bg-card/60 px-4 py-6 backdrop-blur sm:flex">
          <div className="flex items-center gap-2">
            <div className="h-9 w-9 rounded-xl bg-primary" />
            <span className="text-sm font-semibold uppercase tracking-[0.2em]">
              InsightFlow
            </span>
          </div>
          <div className="mt-8 flex flex-col gap-3">
            <Button variant="secondary" className="justify-start">
              Button 1
            </Button>
            <Button variant="secondary" className="justify-start">
              Button 2
            </Button>
            <Button variant="secondary" className="justify-start">
              Button 3
            </Button>
          </div>
        </aside>

        <div className="flex-1">
          <header className="border-b border-border/70 bg-card/60 backdrop-blur">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-3 py-4 sm:px-4">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">
                  InsightFlow
                </p>
                <h1 className="text-lg font-semibold sm:text-xl">Chat</h1>
              </div>
              <Button variant="secondary" size="sm">
                New chat
              </Button>
            </div>
          </header>

          <main className="mx-auto flex min-h-[calc(100vh-72px)] max-w-6xl flex-col px-3 pb-6 pt-6 sm:px-4">
            <section className="flex flex-1 flex-col gap-6">
              <div className="flex-1 space-y-6 rounded-3xl border border-border/70 bg-card/70 p-5 shadow-chat-glow backdrop-blur">
                {THREAD.map((message) => (
                  <div
                    key={message.id}
                    className={cn(
                      "flex w-full gap-3",
                      message.role === "user"
                        ? "justify-end"
                        : "justify-start"
                    )}
                  >
                    {message.role === "assistant" && (
                      <div className="h-8 w-8 rounded-full bg-secondary/70" />
                    )}
                    <div
                      className={cn(
                        "max-w-[78%] rounded-2xl border border-border/60 px-4 py-3 text-sm leading-relaxed shadow-sm sm:text-base",
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-card text-card-foreground"
                      )}
                    >
                      {message.content ? (
                        <p>{message.content}</p>
                      ) : (
                        <div className="space-y-3">
                          <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                            Result
                          </p>
                          <h3 className="text-base font-semibold">
                            {message.data.title}
                          </h3>
                          <div className="overflow-hidden rounded-2xl border border-border/60">
                            <div className="grid grid-cols-2 bg-secondary/70 px-3 py-2 text-xs uppercase tracking-[0.2em] text-muted-foreground">
                              {message.data.columns.map((column) => (
                                <span key={column}>{column}</span>
                              ))}
                            </div>
                            <div className="divide-y divide-border/60">
                              {message.data.rows.map((row, index) => (
                                <div
                                  key={`${row[0]}-${index}`}
                                  className="grid grid-cols-2 px-3 py-2 text-sm text-foreground/90"
                                >
                                  {row.map((cell) => (
                                    <span key={cell}>{cell}</span>
                                  ))}
                                </div>
                              ))}
                            </div>
                          </div>
                          {message.data.query && (
                            <div className="space-y-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-auto px-0 text-xs uppercase tracking-[0.2em] text-muted-foreground hover:text-foreground"
                                type="button"
                                onClick={() => handleToggleQuery(message.id)}
                              >
                                {openQueryId === message.id
                                  ? "Hide query"
                                  : "View query"}
                              </Button>
                              {openQueryId === message.id && (
                                <pre className="whitespace-pre-wrap rounded-2xl border border-border/60 bg-secondary/40 px-3 py-2 text-xs text-foreground/90">
                                  <code className="font-mono">
                                    {message.data.query}
                                  </code>
                                </pre>
                              )}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <section className="sticky bottom-4">
                <div className="rounded-3xl border border-border/70 bg-card/80 p-3 shadow-chat-glow backdrop-blur sm:p-4">
                  <form className="grid gap-3 sm:grid-cols-[1fr_auto] sm:items-end">
                    <Textarea
                      placeholder="Ask your database in natural language..."
                      className="resize-none bg-background/60"
                      rows={3}
                    />
                    <Button className="w-full sm:w-auto" type="button">
                      Send
                    </Button>
                  </form>
                </div>
              </section>
            </section>
          </main>
        </div>
      </div>
    </div>
  );
}
