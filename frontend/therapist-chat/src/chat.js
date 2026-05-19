import { useEffect, useState, useRef } from "react";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

function Chat() {
  const [user, setUser] = useState(null);
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  // -----------------------------
  // Fetch user session
  // -----------------------------
  useEffect(() => {
    fetch(`${API_BASE}/user`, {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => setUser(data.user))
      .catch((err) => console.log(err));
  }, []);

  // -----------------------------
  // Auto scroll
  // -----------------------------
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  if (!user) {
    return <div>Loading user info…</div>;
  }

  // -----------------------------
  // Send message
  // -----------------------------
  const sendMessage = async () => {
    if (!message) return;

    const newChat = [...chat, { role: "user", text: message }];
    setChat(newChat);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ message }),
        }
      );

      if (response.status === 429) {
        alert("Too many requests! Please wait.");
        setLoading(false);
        return;
      }

      const data = await response.json();

      setChat([...newChat, { role: "ai", text: data.reply }]);
    } catch (err) {
      setChat([
        ...newChat,
        { role: "ai", text: "Error contacting therapist AI" },
      ]);
    }

    setLoading(false);
    setMessage("");
  };

  // -----------------------------
  // Quick tool buttons
  // -----------------------------
  const quickActions = [
    "I feel anxious",
    "Help me reframe this thought",
    "I want to journal",
  ];

  return (
    <div style={{ width: "650px", margin: "auto", fontFamily: "Arial" }}>
      <h2>Welcome, {user.name}</h2>
      <h2>🧠 Therapist AI</h2>

      {/* Chat Box */}
      <div
        style={{
          border: "1px solid #ccc",
          height: "400px",
          overflowY: "scroll",
          padding: "10px",
          marginBottom: "10px",
          borderRadius: "10px",
          background: "#fafafa",
        }}
      >
        {chat.map((msg, i) => (
          <p key={i}>
            <b>{msg.role === "user" ? "You" : "Therapist"}:</b>{" "}
            {msg.text}
          </p>
        ))}

        {loading && <p><i>Therapist is typing...</i></p>}

        <div ref={chatEndRef} />
      </div>

      {/* Quick Actions */}
      <div style={{ marginBottom: "10px" }}>
        {quickActions.map((q, i) => (
          <button
            key={i}
            onClick={() => setMessage(q)}
            style={{
              marginRight: "5px",
              padding: "5px 10px",
              borderRadius: "5px",
              border: "1px solid gray",
            }}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input */}
      <input
        style={{ width: "75%", padding: "10px", borderRadius: "5px" }}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="How are you feeling today?"
        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
      />

      <button
        style={{
          padding: "10px",
          marginLeft: "5px",
          borderRadius: "5px",
        }}
        onClick={sendMessage}
      >
        Send
      </button>
    </div>
  );
}

export default Chat;