import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import "chart.js/auto";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

function MoodChart() {
  const [moods, setMoods] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/mood`, {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => setMoods(data.moods || []));
  }, []);

  const moodToNumber = (mood) => {
    switch (mood) {
      case "sad": return 1;
      case "anxious": return 2;
      case "neutral": return 3;
      case "happy": return 4;
      default: return 3;
    }
  };

  const data = {
    labels: moods.map((m, i) => `Entry ${i + 1}`),
    datasets: [
      {
        label: "Mood Trend",
        data: moods.map((m) => moodToNumber(m.mood)),
        borderColor: "blue",
        fill: false,
      },
    ],
  };

  return (
    <div style={{ width: "600px", margin: "auto" }}>
      <h3>📊 Mood Tracker</h3>
      <Line data={data} />
    </div>
  );
}

export default MoodChart;