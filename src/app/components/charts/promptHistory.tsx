import React, { useState, useEffect } from "react";
import Modal from "../../../modals/modal";
import { IoMdArrowBack } from "react-icons/io";



interface PromptHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (query: string) => void;
  selectedAsset: string
}

export default function PromptHistory({ isOpen, onClose, onSubmit, selectedAsset}: PromptHistoryProps) {
  const [promptHistory, setPromptHistory] = useState<{ query: string; timestamp: string }[]>([]);
  const [loading, setLoading] = useState(false); 

  const fetchPromptHistory = async (asset_id: string) => {
    try {
      console.log(asset_id, "Failed" );
      const response = await fetch("http://localhost:8000/api/get-prompt-history",{
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ asset_id }),
      });
      if (!response.ok) {
        throw new Error("Failed to fetch data");
      }
      const data = await response.json();
      setPromptHistory(data.data);
    } catch (error: any) {
      console.error("Fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/clear-prompt-history/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ asset_id: selectedAsset }) 
      });
  
      if (!res.ok) {
        throw new Error("Failed to clear history");
      }
      setPromptHistory([]); 
    } catch (error) {
      console.error("Clear history error:", error);
    }
  };
  
  useEffect(() => {
    if (isOpen) {
      fetchPromptHistory(selectedAsset);
    }
  }, [isOpen]);

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="modal-header">
        <button className="close-btn" onClick={onClose}>
          <IoMdArrowBack />
        </button>
        <h2>Prompt History</h2>
      </div>

      <div className="prompt-list-container">
        {loading ? ( 
          <p className="loading-message">Loading...</p>
        ) : promptHistory.length > 0 ? (
          <ul className="prompt-list">
            {[...promptHistory].reverse().map((entry, index) => (
              <li key={index} className="prompt-item">
                <div className="prompt-text">
                  <strong>{entry.query}</strong> <br />
                  <small>
                    {new Date(entry.timestamp).toLocaleDateString()},{" "}
                    {new Date(entry.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </small>
                </div>
                <button
                  className="execute-btn"
                  onClick={() => {
                    onSubmit(entry.query);
                    onClose();
                  }}
                >
                  Ask again
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="no-history-message">No prompt history yet.</p>
        )}
      </div>        
      <button className="clear-history-btn" onClick={handleClearHistory}>
        Clear History
      </button>
    </Modal>
  );
}
