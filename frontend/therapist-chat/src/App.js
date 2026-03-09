import { useState } from "react";

function App() {

  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);

  const sendMessage = async () => {

    const newChat = [...chat, { role: "user", text: message }];
    setChat(newChat);

    const response = await fetch("https://crispy-goldfish-wrw7p4x6pvqr35vrp-8000.app.github.dev/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: message })
    });


    const data = await response.json();

    setChat([...newChat, { role: "ai", text: data.reply }]);
    setMessage("");
  };

  return (
    <div style={{width:"500px", margin:"auto"}}>
      <h2>Therapist AI</h2>

      <div style={{border:"1px solid gray", height:"400px", overflowY:"scroll"}}>
        {chat.map((msg, i) => (
          <p key={i}>
            <b>{msg.role === "user" ? "You" : "Therapist"}:</b> {msg.text}
          </p>
        ))}
      </div>

      <input
        value={message}
        onChange={(e)=>setMessage(e.target.value)}
        placeholder="Type your message..."
      />

      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default App;