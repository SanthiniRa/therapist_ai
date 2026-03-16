import React, { useEffect } from "react";

function Login() {
  const handleLogin = () => {
    // Redirect user to FastAPI Google OAuth login
    window.location.href = "https://crispy-goldfish-wrw7p4x6pvqr35vrp-8000.app.github.dev/login/google";
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h2>Welcome! Please log in</h2>
      <button onClick={handleLogin}>Login with Google</button>
    </div>
  );
}

export default Login;