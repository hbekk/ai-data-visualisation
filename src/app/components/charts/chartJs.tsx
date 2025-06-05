import { useState, useRef, useEffect } from "react";
import { Chart } from 'chart.js/auto';
import 'chartjs-adapter-moment';
import "../../styles/llmCharts.css";

interface ChartJsCodeRendererProps {
  chartData: any;
  chartOptions: any;
  chartType: any;
  textResponse?: string | null; 
  userQuery: string;
}

const ChartJs: React.FC<ChartJsCodeRendererProps> = ({
  chartData,
  chartOptions,
  chartType,
  textResponse,
  userQuery,
}) => {
  
  const chartRef = useRef<HTMLCanvasElement | null>(null);
  const chartInstance = useRef<Chart | null>(null);
  const [chartError, setChartError] = useState<string | null>(null);

  useEffect(() => {
    if (chartData && chartOptions && chartType && chartRef.current) {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }

      try {
        chartInstance.current = new Chart(chartRef.current, {
          type: chartType,
          data: chartData,
          options: chartOptions,
        });
        setChartError(null); 
      } catch (error: any) {
        setChartError(`Sorry, this chart type (${chartType}) is not supported.`);
      }
    }

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [chartData, chartOptions, chartType]);

  const errorText = textResponse || chartError;

  if (errorText && !chartData) {
    const sadKeywords = ["no data", "not found", "please include", "sorry"];
    const isSad = sadKeywords.some(keyword =>
      errorText.toLowerCase().includes(keyword)
    );

    return (
      <div className="chat-container">
        <div className="query-box">
          <p>{userQuery}</p>
        </div>
        <div className="text-response">
          <img
            className="response-img"
            src={isSad ? "illi_sad.png" : "illi_blink.png"}
            alt="bot"
          />
          <p>{errorText}</p>
        </div>
      </div>
    );
  }

  

  return (
    <div className="graph-container">
      <canvas ref={chartRef} />
    </div>
  );
};

export default ChartJs;
