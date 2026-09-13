import { useState } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "¡Hola! Soy tu asistente personal." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!input.trim()) return;
    setLoading(true);
    const newUser = { role: "user", content: input };
    setMessages((m) => [...m, newUser]);

    const resp = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages,
        history_id: "sess_001"
      })
    });
    const data = await resp.json();

    setMessages((m) => [
      ...m,
      { role: "assistant", content: data.response }
    ]);

    setInput("");
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white shadow-sm flex items-center justify-between p-4">
        <h1 className="text-xl font-medium">🧠 Asistente Apple</h1>
        <button className="btn-sm">⚙️ Config.</button>
      </header>

      <main className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={max-w-[800px] mx-auto mb-4 p-3 rounded-lg ${
              msg.role === "assistant"
                ? "bg-blue-100"
                : "bg-gray-100"
            }}
          >
            <p className="text-gray-900">{msg.content}</p>
          </div>
        ))}
      </main>

      <footer className="p-2 flex justify-between items-center">
        <input
          type="text"
          placeholder="Escribe algo..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 px-3 py-2 border rounded-md"
          disabled={loading}
        />
        <button
          onClick={submit}
          disabled={loading || !input.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded-md"
        >
          {loading ? "Enviando…" : "Enviar"}
        </button>
      </footer>
    </div>
  );
}

export default App;
