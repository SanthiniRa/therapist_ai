import React from "react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "";

function Login() {
  const handleLogin = () => {
    // Redirect user to FastAPI Google OAuth login
    const loginUrl = BACKEND_URL ? `${BACKEND_URL}/login/google` : "/login/google";
    window.location.href = loginUrl;
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h2>Welcome! Please log in</h2>
      <button onClick={handleLogin}>Login with Google</button>
    </div>
  );
}

export default Login;