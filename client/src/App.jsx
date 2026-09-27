import { useState } from "react";

function App() {
  const [script, setScript] = useState("devanagari");

  const [text, setText] = useState(
    "सर्वे भवन्तु सुखिनः ।"
  );

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleGenerate() {
    if (!text.trim()) {
      setError("Please enter some text.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      console.log("Selected script:", script);
      console.log("Text:", text);

      const response = await fetch(
        "http://127.0.0.1:5000/generate",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            script: script,
            text: text,
          }),
        }
      );

      if (!response.ok) {
        let message = `Server error: ${response.status}`;

        try {
          const data = await response.json();

          if (data.message) {
            message = data.message;
          }
        } catch {
          // Server did not return JSON
        }

        throw new Error(message);
      }

      // Flask returns a ZIP file
      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");

      link.href = url;
      link.download = "manuscript.zip";

      document.body.appendChild(link);

      link.click();

      link.remove();

      window.URL.revokeObjectURL(url);

      console.log("Manuscript generated successfully.");

    } catch (err) {
      console.error("Generation error:", err);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to the server."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#090909",
        color: "white",
        padding: "35px 20px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <div
        style={{
          maxWidth: "540px",
          margin: "0 auto",
        }}
      >
        <h1
          style={{
            textAlign: "center",
            fontSize: "28px",
            marginBottom: "8px",
          }}
        >
          Synthetic Manuscript Generator
        </h1>

        <p
          style={{
            textAlign: "center",
            color: "#9ca3af",
            marginBottom: "35px",
          }}
        >
          Generate realistic manuscript images from text
        </p>

        <div
          style={{
            background: "#111111",
            border: "1px solid #374151",
            borderRadius: "12px",
            padding: "30px",
          }}
        >
          <label
            style={{
              display: "block",
              marginBottom: "10px",
              color: "#d1d5db",
            }}
          >
            Select Script
          </label>

          <select
            value={script}
            onChange={(e) => setScript(e.target.value)}
            style={{
              width: "100%",
              padding: "13px",
              marginBottom: "25px",
              background: "#1a1a1a",
              color: "white",
              border: "1px solid #4b5563",
              borderRadius: "7px",
              fontSize: "15px",
            }}
          >
            <option value="devanagari">Devanagari</option>
            <option value="modi">Modi</option>
            <option value="sharada">Sharada</option>
          </select>

          <label
            style={{
              display: "block",
              marginBottom: "10px",
              color: "#d1d5db",
            }}
          >
            Enter Text
          </label>

          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={10}
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: "14px",
              background: "#1a1a1a",
              color: "white",
              border: "1px solid #4b5563",
              borderRadius: "7px",
              fontSize: "17px",
              resize: "vertical",
              marginBottom: "22px",
            }}
          />

          <button
            onClick={handleGenerate}
            disabled={loading}
            style={{
              width: "100%",
              padding: "14px",
              border: "none",
              borderRadius: "7px",
              background: loading ? "#9ca3af" : "#f3f4f6",
              color: "#111111",
              fontSize: "16px",
              fontWeight: "600",
              cursor: loading ? "wait" : "pointer",
            }}
          >
            {loading
              ? "Generating..."
              : "Generate Manuscript"}
          </button>

          {error && (
            <p
              style={{
                color: "#ef4444",
                marginTop: "18px",
                marginBottom: 0,
              }}
            >
              {error}
            </p>
          )}

          <p
            style={{
              color: "#9ca3af",
              fontSize: "13px",
              marginTop: "20px",
              textAlign: "center",
            }}
          >
            A ZIP file containing manuscript.png and
            manuscript.md will be downloaded.
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;