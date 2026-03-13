import React, { useEffect } from "react";

function Login({ setUser }) {

  // Check if redirected back from Google callback
  useEffect(() => {
    fetch("https://crispy-goldfish-wrw7p4x6pvqr35vrp-8000.app.github.dev/auth/google/callback")
      .then(res => res.json())
      .then(data => {
        if (data.user) {
          setUser(data.user); // store user in React state
        }
      })
      .catch(err => console.log(err));
  }, []);

  const loginWithGoogle = () => {
    window.location.href =
      "https://crispy-goldfish-wrw7p4x6pvqr35vrp-8000.app.github.dev/login/google";
  };

  return (
    <div style={{ textAlign: "center", marginTop: "100px" }}>
      <h2>Therapist AI</h2>
      <button onClick={loginWithGoogle}>
        Login with Google
      </button>
    </div>
  );
}

export default Login;