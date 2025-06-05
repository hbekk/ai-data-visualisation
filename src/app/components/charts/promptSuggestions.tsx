import React, { useEffect, useState } from "react";
import "../../styles/promptSuggestions.css";
import { useChartContext } from "@/app/context/chartContext";


interface Props {
  selectedAsset: string;
  isNew?: boolean;
  onSubmit: (query: string) => void;
}

export default function PromptSuggestions({ selectedAsset, isNew, onSubmit }: Props) {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const { suggestionCache, setSuggestionCache } = useChartContext();


  useEffect(() => {
    if (!selectedAsset) return;
  
    if (suggestionCache[selectedAsset]) {
      setSuggestions(suggestionCache[selectedAsset]);
      return;
    }
  
    async function fetchSuggestions() {
      try {
        setLoading(true);
        const res = await fetch("http://localhost:8000/api/prompt-suggestions/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ asset_id: selectedAsset })
        });
        const data = await res.json();
        setSuggestions(data.suggestions);
        setSuggestionCache(prev => ({ ...prev, [selectedAsset]: data.suggestions }));
      } catch (err) {
        console.error("Error fetching suggestions:", err);
      } finally {
        setLoading(false);
      }
    }
  
    fetchSuggestions();
  }, [selectedAsset]);

  async function handleSuggestionClick(suggestion: string) {
    try {
      await fetch("http://localhost:8000/api/save-prompt/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: suggestion, asset_id: selectedAsset })
      });
    } catch (err) {
      console.error("Error saving prompt:", err);
    }

    onSubmit(suggestion); 
  }

  return (
    <div className={`suggestion-container ${isNew ? "centered" : ""}`}>
      {loading ? (
        <p className="loading">Loading suggestions...</p>
      ) : (
        suggestions.map((suggestion, index) => (
          <button
            key={index}
            className="suggestion-pill"
            onClick={() => handleSuggestionClick(suggestion)}
          >
            {suggestion}
          </button>
        ))
      )}
    </div>
  );
}
