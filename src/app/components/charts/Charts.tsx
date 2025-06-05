import { useState, useEffect} from "react";
import {useSaveGraph} from "../../utils/archive_graph";
import { useAddChartHistory } from "../../utils/archive_graph";
import { handleChartRequest } from "../../utils/chartUtils";
import { Dialog } from "@/app/modals/dialog_modal";
import { sanitizeInput } from "./chartInput";
import PromptSuggestions from "./promptSuggestions";
import ChartJs from "./chartJs";
import ChartInput from "./chartInput";
import PromptHistory from "./promptHistory";
import { useChartContext } from "@/app/context/chartContext";
import { useRemoveGraph } from "../../utils/archive_graph";
import { SmallDialog } from "@/app/modals/dialog_modal";

const Charts: React.FC = () => {
  const { response, setResponse } = useChartContext();
  const [isModalOpen, setModalOpen] = useState(false);
  const [isSmodalOpen, setSmodalOpen] = useState(false);
  const { showSuggestions, setShowSuggestions } = useChartContext();
  const [userQuery, setUserQuery] = useState<string>(""); 

  const {
    chartData,
    setChartData,
    chartOptions,
    setChartOptions,
    setChartType,
    chartType,
    chartTitle,
    setChartTitle,
    loading,
    setLoading,
    selectedAsset,
    previousQuery,
    setPreviousQuery,
    setActiveChart,
    chartHistoryList,
    isSaved,
    chartDate,
    setIsSaved,
    isNew,
    setIsNew
  } = useChartContext();



  const handleTitleSave = (savedChartTitle: string) => {
    setChartTitle(sanitizeInput(savedChartTitle));
  };


  const { saveGraph } = useSaveGraph();
  const {addChartHistory} = useAddChartHistory();
  const {removeGraph} = useRemoveGraph();

  const openModal = () => setModalOpen(true);
  const closeModal = () => setModalOpen(false);

  const openSmodal = () => {
    setSmodalOpen(true)
  }

  const closeSModal = () => setSmodalOpen(false);

  const downloadChart = () => {
      const canvas = document.querySelector(".graph-container canvas") as HTMLCanvasElement | null;
    
      if (canvas) {
        const imageURL = canvas.toDataURL("image/png");
        const link = document.createElement("a");
        link.href = imageURL;
        link.download = `${chartTitle}.png`; 
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        console.error("Chart canvas not found!");
      }
  };


  const handleNewChart = () => {
    setChartData(null);
    setChartOptions(null);
    setChartType("");
    setChartTitle(""); 
    setPreviousQuery([]);
    setActiveChart(null);
    setIsSaved(false);
    setShowSuggestions(true);
    setIsNew(true);
    setResponse(null);
  };




  const handleDeleteGraph = (chartDate:any) => {
    removeGraph(chartDate, selectedAsset);
  };

  return (
    <>
      {(loading && selectedAsset ) && <div className="loading-gradient"></div>}
  
      <div className="llm-container">

      
      {chartData ? (
            // This ChartInput is shown if chartData is not empty
            <ChartInput
              title="Edit an existing chart"
              isNew={isNew}
              onSubmit={async (query) => {  
                setPreviousQuery((prev) => [...prev, query]);
                setUserQuery(query);
                setShowSuggestions(false);

                const newChart = await handleChartRequest(
                  "reply " + query, 
                  selectedAsset, 
                  previousQuery, 
                  setLoading,
                  setResponse, 
                  setChartData, 
                  setChartOptions, 
                  setChartType, 
                  setChartTitle
                );

                if (newChart.chartData !== null) {
                  addChartHistory(newChart.chartData, newChart.chartOptions, newChart.chartType, newChart.chartTitle, selectedAsset, previousQuery);
                }
              }}
            />
          ) : (
            <ChartInput
              title="Generate a new chart"
              isNew={true}
              onSubmit={async (query) => {
                
              
                setPreviousQuery((prev) => [...prev, query]);
                setUserQuery(query);
                setShowSuggestions(false);


                const newChart = await handleChartRequest(
                  query, 
                  selectedAsset, 
                  previousQuery, 
                  setLoading,
                  setResponse, 
                  setChartData, 
                  setChartOptions, 
                  setChartType, 
                  setChartTitle
                );

                if (newChart && newChart.chartData !== null) {
                  setIsNew(false)
                  addChartHistory(newChart.chartData, newChart.chartOptions, newChart.chartType, newChart.chartTitle, selectedAsset, previousQuery);
                }

              }}
            />
          )}
  
  {(showSuggestions && isNew) && (
  <PromptSuggestions
    selectedAsset={selectedAsset}
    isNew={isNew}
    onSubmit={async (query) => {
      setPreviousQuery((prev) => [...prev, query]);
      setUserQuery(query);
      setShowSuggestions(false);
      setIsNew(false);

      const newChart = await handleChartRequest(
        query, selectedAsset, [query], setLoading, setResponse, setChartData, setChartOptions, setChartType, setChartTitle
      );

      if (newChart.chartData && newChart.chartOptions && newChart.chartType && newChart.chartTitle) {
        addChartHistory(
          newChart.chartData, newChart.chartOptions, newChart.chartType, newChart.chartTitle, selectedAsset, [query]
        );
      }
    }}
  />
)}


      <SmallDialog isOpen={isSmodalOpen} onClose={closeSModal}>
          <div className="modal-title">
              <h2><strong>Are you sure you want to delete?</strong></h2>
            </div>
            <div className="cfm-btn">
            <button onClick={() => setSmodalOpen(false)}>Cancel</button>
            <button onClick={() => { 
                handleDeleteGraph(chartDate, selectedAsset); 
                setSmodalOpen(false); 
                handleNewChart();
              }}>
            Yes, delete
          </button>            
          </div>
      </SmallDialog>

  
        <Dialog isOpen={isModalOpen} onClose={closeModal}>
          <div className="modal-title">
            <h2>Save Chart...</h2>
          </div>
          <form className="save-chart-input">
            <h3>Title:</h3>
            <input
              type="text"
              placeholder="Enter title..."
              className="save-input"
              value={chartTitle}
              onChange={(e) => handleTitleSave(e.target.value)}
              maxLength={60}
            />
            <h3>Description:</h3>
            <input
              type="text"
              placeholder="Enter description..."
              className="save-input"
              maxLength={60}
            />
          </form>
  
          <div className="save-btn">
            <button
              onClick={() => {
                saveGraph(chartData, chartOptions, chartType, chartTitle, selectedAsset, previousQuery);
                setModalOpen(false);
              }}
            >
              Save Chart
            </button>
          </div>
        </Dialog>
  
        <div className="llm-content">

        {loading && <p className="loading">Fetching data...</p>}

        {!loading &&

        <ChartJs
              chartData={chartData || null}  
              chartOptions={chartOptions || null}
              chartType={chartType || 'bar'}  
              textResponse={response?.error || response?.message || null}  
              userQuery={userQuery}
            />
          } 
        </div>
        
        {chartData ? (
          <div className="save-btn">
            {isSaved ? (
              <>
                <button onClick={() => downloadChart()}>Download chart</button>
                <button onClick={() => setSmodalOpen(true)}>Delete chart...</button>
              </>
            ) : (
              <>
                  <button onClick={() => downloadChart()}>Download chart</button>
                  <button onClick={() => setModalOpen(true)}>Save chart...</button>
              </>
            )}
            <button onClick={() => handleNewChart()}>New chart...</button>
          </div>
        ) : null}
     
      </div>
    </>
  );
}
export default Charts;
