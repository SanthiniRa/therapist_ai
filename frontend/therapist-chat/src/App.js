import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./login";
import Chat from "./chat";
import MoodChart from "./moodChart";
import Journal from "./Journal";
function App() {
  return (
    <BrowserRouter>

      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/mood" element={<MoodChart />} />
        <Route path="/journal" element={<Journal />} />
      </Routes>

    </BrowserRouter>
  );
}

export default App;