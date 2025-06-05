import { useState } from "react";
import { FaArrowRight } from "react-icons/fa"; 
import "../../styles/modals.css";
import { useChartContext } from "@/app/context/chartContext";

interface ChartInputProps {
  title?: string; 
  isNew?: boolean;
  onSubmit: (query: string) => void; 
}

const sanitizeInput = (input: string) => {
  const pattern = /^[a-zA-Z0-9æøåÆØÅ\s\/,.\-?:+]*$/;
  return pattern.test(input) ? input : "";
};

export default function ChartInput({title,isNew, onSubmit}: ChartInputProps) {

  const {
    loading,
    selectedAsset
  } = useChartContext();

  const [query, setQuery] = useState("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>, asset_id: string) => {
    e.preventDefault();

    const cleanQuery = sanitizeInput(query);
    if (!cleanQuery || !asset_id) {
      console.error("Invalid input");
      return;
    }
  
    if (!query.trim() || !asset_id) {
      console.error("Missing query or asset_id");
      return;
    }
  
    const data = {
      query,
      asset_id
    };

    console.log("Sending data:", data);
    
    try {
      const response = await fetch("http://localhost:8000/api/save-prompt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
  
      const result = await response.json();
      console.log("Upload Success:", result);
      onSubmit(data.query);
      setQuery("");
    } catch (error) {
      console.error("Upload Error:", error);
    }
  };

  return (
    <div className={`input-container ${isNew ? "centered" : ""}`}>
      <div className="input-title">
        <h2>{title}</h2>
        <img 
          src={loading ? "illi_loading.png" : "illi.png"} 
          alt="Status Image" 
          className={loading ? "flash" : ""} 
        />    
      </div>

     <form
        onSubmit={(e) => handleSubmit(e, selectedAsset)} 
        className="chart-input-wrapper"
      >
  
        <input
          type="text"
          placeholder="Enter your suggestion..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="chart-input"
          maxLength={85}
          />
        <button type="submit" className="chart-send-button">
          {loading ? <div className="spinner"></div> : <FaArrowRight className="chart-send-icon" />}
        </button>
      </form>
      
    </div>
  );
}

export {sanitizeInput, ChartInput}