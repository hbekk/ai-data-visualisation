import { fetchData } from "../components/sidebar/archived_charts";
import { fetchHistoryData } from "../components/sidebar/chart_history";
import { useChartContext } from "../context/chartContext";

export const useSaveGraph = () => {
  const { setArchivedList, setActiveChart } = useChartContext();

  const saveGraph = async (
    chartData: any,
    chartOptions: any,
    chartType: any,
    chartTitle: string,
    assetId: string,
    previousQueries: string[]
  ) => {
    const timestamp = Date.now();

    const data = {
      chartData,
      chartOptions,
      chartType,
      date: timestamp,
      title: chartTitle,
      asset_id: assetId,
      previousQueries
    };

    try {
      const response = await fetch("http://localhost:8000/save_chart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      const result = await response.json();
      console.log("Upload Success:", result);

      const newList = await fetchData(assetId);  
      setArchivedList(newList);
      setActiveChart(newList[newList.length - 1]);

    } catch (error) {
      console.error("Upload Error:", error);
    }
  };

  return { saveGraph };
};

export const useRemoveGraph = () => {
  
  const { setArchivedList } = useChartContext();
  
  const removeGraph = async (id: number, asset_id: string) => {
    try {
      const response = await fetch("http://localhost:8000/remove_saved_chart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ timestamp: id }),
      });
      const result = await response.json();
  
      const newList = await fetchData(asset_id);  
      setArchivedList(newList);
  
      console.log("Removal Success:", result);
    } catch (error) {
      console.error("Removal Error:", error);
    }
  };

  return {removeGraph};
};


export const useAddChartHistory = () => {
  const { setChartHistoryList, setActiveChart, chartHistoryList} = useChartContext();

  const addChartHistory = async (
    chartData: any,
    chartOptions: any,
    chartType: any,
    chartTitle: string,
    assetId: string,
    previousQueries: string[]
  ) => {
    const timestamp = Date.now();

    const data = {
      chartData,
      chartOptions,
      chartType,
      date: timestamp,
      title: chartTitle,
      asset_id: assetId,
      previousQueries
    };

    try {
      const response = await fetch("http://localhost:8000/save_chart_history", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      const result = await response.json();
      console.log("Upload Success:", result);

      const newList = await fetchHistoryData(assetId);
      setChartHistoryList(newList);
      setActiveChart(newList[newList.length - 1]);


    } catch (error) {
      console.error("Upload Error:", error);
    }
  };

  return { addChartHistory };
};