import { useState, useEffect } from "react";
import { IoMdArrowDropdown } from "react-icons/io";
import { useChartContext } from "@/app/context/chartContext";

const AssetPicker = () => {
  const [isDropdownOpen, setDropdownOpen] = useState(false);

  const {
    setSelectedAsset,
    selectedAsset,
    assets,
    setChartData,
    setChartOptions,
    setChartType,
    setChartTitle,
    setActiveChart,
    setPreviousQuery,
    setIsSaved,
    setIsNew,
    setResponse,
    setShowSuggestions

  } = useChartContext();
  

  const toggleDropdown = () => {
    setDropdownOpen(!isDropdownOpen);
  };

  const handleAssetSelect = (asset: { id: string; name: string }) => {
    setSelectedAsset(asset.id);  
    setDropdownOpen(false);
    setChartData(null);
    setChartOptions(null);
    setChartType("");
    setChartTitle("");
    setActiveChart(null);
    setPreviousQuery([]);
    setIsSaved(false);
    setIsNew(true);
    setResponse(null);
    setShowSuggestions(true);
  };

  return (
    <div>
      <div className="dropdown">
        <button onClick={toggleDropdown} className="dropbtn">
          {selectedAsset
            ? assets.find((asset) => asset.id === selectedAsset)?.name || "Unknown Asset"
            : "Select an asset"} 
          <IoMdArrowDropdown />
        </button>
        {isDropdownOpen && (
          <div className="dropdown-content">
            {assets.length > 0 ? (
              assets.map((asset) => (
                <a key={asset.id} onClick={() => handleAssetSelect(asset)}>
                  {asset.name}
                </a>
              ))
            ) : (
              <a>No assets available</a>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AssetPicker;
