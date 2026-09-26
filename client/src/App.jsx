import { useState } from "react";

function App() {
  const [script, setScript] = useState("devanagari");
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const detectScript = (text) => {
    for (const char of text) {
      const code = char.codePointAt(0);

      // Devanagari: U+0900–U+097F
      if (code >= 0x0900 && code <= 0x097F) {
        return "devanagari";
      }

      // Modi: U+11600–U+1164F
      if (code >= 0x11600 && code <= 0x1164F) {
        return "modi";
      }

      // Sharada: U+11180–U+111DF
      if (code >= 0x11180 && code <= 0x111DF) {
        return "sharada";
      }
    }

    return "unknown";
  };

  const handleGenerate = async () => {
    if (!text.trim()) {
      setError("Please enter some text.");
      return;
    }

    const detectedScript = detectScript(text);

    console.log("Selected script:", script);
    console.log("Detected script:", detectedScript);
    console.log(
      "First character:",
      text[0],
      "Code:",
      text.codePointAt(0).toString(16)
    );

    if (detectedScript !== "unknown" && detectedScript !== script) {
      setError(
        `You selected ${script}, but the entered text appears to be ${detectedScript}.`
      );
      return;
    }

    setError("");
    setSuccess("");
    setLoading(true);

    const data = {
      text: text,
      script: script,
    };

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/generate",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        }
      );

      if (!response.ok) {
        const result = await response.json();
        setError(result.message || "Generation failed.");
        return;
      }

      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "manuscript.zip";

      document.body.appendChild(a);
      a.click();

      a.remove();
      window.URL.revokeObjectURL(url);

      setSuccess("Manuscript generated successfully.");

    } catch (error) {
      console.error(error);
      setError("Unable to connect to the server.");

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white flex items-center justify-center px-4">
      <div className="w-full max-w-xl">

        <h1 className="text-3xl font-semibold text-center mb-2">
          Synthetic Manuscript Generator
        </h1>

        <p className="text-gray-400 text-center mb-8">
          Generate realistic manuscript images from text
        </p>

        <div className="border border-gray-700 rounded-xl p-8 bg-[#111111]">

          {/* Script Selection */}
          <label className="block text-sm text-gray-400 mb-2">
            Select Script
          </label>

          <select
            value={script}
            onChange={(e) => setScript(e.target.value)}
            className="w-full bg-[#1a1a1a] border border-gray-700
                      rounded-lg px-4 py-3 text-white
                      focus:outline-none focus:border-gray-500"
          >
            <option value="devanagari">Devanagari</option>
            <option value="modi">Modi</option>
            <option value="sharada">Sharada</option>
          </select>

          {/* Text Input */}
          <label className="block text-sm text-gray-400 mt-6 mb-2">
            Enter Text
          </label>

          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter the text to generate the manuscript..."
            rows={10}
            className="w-full bg-[#1a1a1a] border border-gray-700
                      rounded-lg px-4 py-3 text-white
                      placeholder-gray-600 resize-none
                      focus:outline-none focus:border-gray-500"
          />

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={!text.trim() || loading}
            className="w-full mt-6 rounded-lg bg-white
                      px-4 py-3 text-black font-medium
                      hover:bg-gray-200 transition
                      disabled:opacity-40 disabled:cursor-not-allowed
                      flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span
                  className="w-5 h-5 border-2 border-black/30
                            border-t-black rounded-full animate-spin"
                ></span>
                Generating...
              </>
            ) : (
              "Generate Manuscript"
            )}
          </button>

          {/* Error */}
          {error && (
            <p className="text-red-400 text-sm mt-4">
              {error}
            </p>
          )}

          {/* Success */}
          {success && (
            <p className="text-green-400 text-sm mt-4">
              {success}
            </p>
          )}

        </div>
      </div>
    </div>
  );
}

export default App;