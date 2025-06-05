import '../../styles/Sidebar/sidebar-lists.css'; 
import { useState, useEffect } from 'react';
import { LiaSave } from "react-icons/lia";
import { useChartContext } from '@/app/context/chartContext';

export async function fetchData(asset_id: string): Promise<any[]> {
  try {
    const response = await fetch("http://localhost:8000/get_chart_data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ asset_id }),
    });
    if (!response.ok) {
      throw new Error("Failed to fetch data");
    }
    const data = await response.json();
    return data.data; 
  } catch (error: any) {
    console.error("Fetch error:", error);
    throw new Error(error.message); 
  }
}

export default function ArchivedCharts() {
  const {
    selectedAsset,
    loading,
    setLoading,
    error,
    setError,
    setArchivedList,
    archivedList,
    setChartData,
    setChartOptions,
    setChartType,
    activeChart,
    setActiveChart,
    setPreviousQuery,
    setIsSaved,
    setChartDate,
    setChartTitle,
    setIsNew
  } = useChartContext();


  const handleChartClick = (chart:any) => {
    setChartData(chart.chartData);
    setChartOptions(chart.chartOptions);
    setChartType(chart.chartType);
    setChartTitle(chart.title);
    setActiveChart(chart);
    setPreviousQuery(chart.previousQueries);
    setIsSaved(true);
    setChartDate(chart.date);
    setIsNew(false);
  }

  useEffect(() => {
    const loadData = async () => {
      if (selectedAsset) {
        try {
          const data = await fetchData(selectedAsset);
          setArchivedList(data);
        } catch (error: any) {
          setError(error.message);
        } finally {
        }
      }
    };
    loadData();
  }, [selectedAsset]);

  return (
    <div className="lists-container">
      <div className="list-title">
        <LiaSave className="list-title-icon" />
        <h1>Archived Charts</h1>
      </div>
  
      {error ? (
        <p>Error: {error}</p>
      ) : (
        <div className="list-content">
          {archivedList.length === 0 ? (
            <p>No archived graphs</p>
          ) : (
            <ul>
            {[...archivedList].reverse().map((chart, index) => (
              <li key={index}>
                <button
                  className={`archived-chart-button ${activeChart === chart ? 'active' : ''}`} 
                  onClick={() => handleChartClick(chart)}
                >
                  <h2>{chart.title}</h2>
                  <h3>Saved: {new Date(chart.date).toLocaleString()}</h3>
                </button>
              </li>
            ))}
          </ul>
          )}
        </div>
      )}
    </div>
  );
}
