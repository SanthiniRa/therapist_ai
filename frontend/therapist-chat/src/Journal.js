import { useEffect, useState } from "react";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

function Journal() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/journal`, {
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