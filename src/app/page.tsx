"use client";
import React, { useEffect, useState } from "react";
import SideBar from "./components/sidebar/sideBar";
import ChartInput from "./components/charts/chartInput";
import Charts from "./components/charts/Charts";
import { useChartContext } from "./context/chartContext";

export default function Home() {
  const {
    selectedAsset,
    setSelectedAsset,
    assets,
    setAssets,
    loading,
    setLoading,
    chartData,
    setChartData,
    chartOptions,
    setChartOptions,
    chartType,
    setChartType,
    chartTitle,
    setChartTitle,
    chartDate,
    setChartDate,
    isSaved,
    setIsSaved,
  } = useChartContext(); 
  
  const [error, setError] = useState<string | null>(null);

  const fetchAssets = async () => {
    try {
      const response = await fetch("http://localhost:8000/assets");
      if (!response.ok) {
        throw new Error("Failed to fetch assets");
      }
      const responseData = await response.json();
      console.log("Fetched data:", responseData);
      setAssets(responseData.data);
    } catch (error: any) {
      console.error("Fetch error:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssets();
  }, []); 

  useEffect(() => {
    if (selectedAsset) {
      console.log("Selected asset changed:", selectedAsset);
    }
  }, [selectedAsset]);

  return (
    <main>
      <div className="sidebar-container">
        <SideBar />
      </div>

      <div className="chart-containers">
        <Charts />
      </div>
    </main>
  );
}
