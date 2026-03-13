import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./login";
import Chat from "./chat";

function App() {
  return (
    <BrowserRouter>

      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/chat" element={<Chat />} />
      </Routes>

    </BrowserRouter>
  );
}

export default App;