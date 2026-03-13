import { useState } from "react";

function App() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [user, setUser] = useState(null); // store logged-in user

  // Fetch logged-in user info from session
  useEffect(() => {
    fetch("https://crispy-goldfish-wrw7p4x6pvqr35vrp-8000.app.github.dev/user", {
      credentials: "include", // send cookies
    })
      .then(res => res.json())
      .then(data => setUser(data.user))
      .catch(err => console.log(err));
  }, []);

  if (!user) {
    return <div>Loading...</div>;
  }

  const sendMessage = async () => {
    if (!message) return;

    const newChat = [...chat, { role: "user", text: message }];
    setChat(newChat);

    try {
      const response = await fetch(
        "https://crispy-goldfish-wrw7p4x6pvqr35vrp-8000.app.github.dev/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message }),
        }
      );

      const data = await response.json();
      setChat([...newChat, { role: "ai", text: data.reply }]);
    } catch (error) {
      setChat([...newChat, { role: "ai", text: "Error contacting therapist AI" }]);
    }

    setMessage("");
  };

  // -----------------------
  // Conditional rendering
  // -----------------------
  if (!user) {
    // if user is not logged in, show login page
    return <login setUser={setUser} />;
  }

  // if user is logged in, show chat
  return (
    <div style={{ width: "600px", margin: "auto" }}>
      <h2>Welcome, {user.name}</h2>
      <h2>🧠 Therapist AI</h2>
      <p>Logged in as: {user.name || user.email}</p>

      <div
        style={{
          border: "1px solid gray",
          height: "400px",
          overflowY: "scroll",
          padding: "10px",
          marginBottom: "10px",
        }}
      >
        {chat.map((msg, i) => (
          <p key={i}>
            <b>{msg.role === "user" ? "You" : "Therapist"}:</b> {msg.text}
          </p>
        ))}
      </div>

      <input
        style={{ width: "80%", padding: "10px" }}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="How are you feeling today?"
      />

      <button style={{ padding: "10px" }} onClick={sendMessage}>
        Send
      </button>
    </div>
  );
}

export default App;