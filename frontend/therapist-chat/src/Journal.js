import { useEffect, useState } from "react";

function Journal() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    fetch("https://crispy-goldfish-wrw7p4x6pvqr35vrp-8000.app.github.dev/journal", {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => setEntries(data.entries || []));
  }, []);

  return (
    <div style={{ width: "600px", margin: "auto" }}>
      <h3>📓 Your Journal</h3>

      {entries.length === 0 && <p>No journal entries yet.</p>}

      {entries.map((entry, i) => (
        <div
          key={i}
          style={{
            border: "1px solid gray",
            padding: "10px",
            marginBottom: "10px",
            borderRadius: "8px",
          }}
        >
          <p>{entry.entry}</p>
          <small>{new Date(entry.timestamp).toLocaleString()}</small>
        </div>
      ))}
    </div>
  );
}

export default Journal;