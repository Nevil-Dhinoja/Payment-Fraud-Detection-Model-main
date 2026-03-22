import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

const Login = () => {
  const navigate = useNavigate();

  // State to store identifier, password, submission status, and login status
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(sessionStorage.isLoggedIn);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!identifier.trim() || !password.trim()) {
      alert("Both identifier and password are required.");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await axios.post("http://localhost:7000/api/auth/login", {
        identifier: identifier.trim(),
        password: password.trim(),
      });

      // Save JWT token to sessionStorage
      const token = response.data.token;
      sessionStorage.setItem("token", token);

      // Set login status to true
      setIsLoggedIn(true);

      // Redirect to the home page

      navigate("/");
      window.location.reload();
    } catch (error) {
      console.error(error);
      alert(
        error?.response?.data?.message ||
          "Login failed. Please check your credentials and try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "400px", margin: "0 auto" }}>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "10px" }}>
          <label htmlFor="identifier">Email/Phone:</label>
          <input
            type="text"
            id="identifier"
            name="identifier"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            required
            style={{ display: "block", width: "100%", padding: "8px" }}
          />
        </div>
        <div style={{ marginBottom: "10px" }}>
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            name="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ display: "block", width: "100%", padding: "8px" }}
          />
        </div>
        <button
          type="submit"
          disabled={isSubmitting}
          style={{
            backgroundColor: "#007bff",
            color: "#fff",
            padding: "10px 20px",
            border: "none",
            cursor: "pointer",
            width: "100%",
          }}
        >
          {isSubmitting ? "Logging in..." : "Login"}
        </button>
      </form>
      <p style={{ marginTop: "20px" }}>
        Don't have an account? <Link to="/register">Sign up</Link>
      </p>
    </div>
  );
};

export default Login;
