export const handleChartRequest = async (
  query: string,
  selectedAsset: string,
  previousQuery: string[],
  setLoading: React.Dispatch<React.SetStateAction<boolean>>,
  setResponse: React.Dispatch<React.SetStateAction<any>>,
  setChartData: React.Dispatch<React.SetStateAction<any>>,
  setChartOptions: React.Dispatch<React.SetStateAction<any>>,
  setChartType: React.Dispatch<React.SetStateAction<any>>,
  setChartTitle: (title: string) => void,
) => {
  setLoading(true);
  setResponse(null);

  const requestData = {
    query,
    asset_id: String(selectedAsset),
    previousQuery,
  };

  try {
    const res = await fetch("http://localhost:8000/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestData),
    });

    let data;
    try {
      data = await res.json();
    } catch (error) {
      console.error("Invalid JSON response:", error);
      data = { error: "Invalid response from server." };
    }

    if (!res.ok) {
      setResponse({ error: "Unexpected error occurred." });
      return null;
    }

    if (data && data.success === false && typeof data.message === "string") {
      setResponse({ message: data.message });
      setChartData(null);
      setChartOptions(null);
      setChartType(null);
      if (setChartTitle) setChartTitle("Notice");
      return null;
    }

    if (data.message) {
      setResponse({ message: data.message });
      setChartData(null);
      setChartOptions(null);
      setChartType(null);
      if (setChartTitle) setChartTitle("Summary");
      return null;
    }

    if (data.chartData && data.chartOptions && data.chartType) {
      setChartData(data.chartData);
      setChartOptions(data.chartOptions);
      setChartType(data.chartType);

      setResponse({ type: "chart", ...data });

      if (setChartTitle && data.llmTitle) {
        setChartTitle(data.llmTitle);
      }

      return {
        chartData: data.chartData,
        chartOptions: data.chartOptions,
        chartType: data.chartType,
        chartTitle: data.llmTitle || "Untitled",
      };
    }

    setResponse({ error: "Unexpected processing. Please try again!" });
    return null;

  } catch (error) {
    console.error("Error fetching data:", error);
    setResponse({ error: "An error occurred while processing your request." });
    return null;
  } finally {
    setLoading(false);
  }
};
