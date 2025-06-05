"use client"
import React, { createContext, useContext, useState, ReactNode, useRef } from 'react';

interface ChartContextProps {
  selectedAsset: string | null;
  setSelectedAsset: React.Dispatch<React.SetStateAction<string | null>>;
  assets: { id: string; name: string }[];
  setAssets: React.Dispatch<React.SetStateAction<{ id: string; name: string }[]>>;
  error: string | null;
  setError: React.Dispatch<React.SetStateAction<string | null>>;
  loading: boolean;
  setLoading: React.Dispatch<React.SetStateAction<boolean>>;

  chartData: any | null;
  setChartData: React.Dispatch<React.SetStateAction<any | null>>;
  chartOptions: any | null;
  setChartOptions: React.Dispatch<React.SetStateAction<any | null>>;
  chartType: string;
  setChartType: React.Dispatch<React.SetStateAction<string>>;
  chartTitle: string;
  setChartTitle: React.Dispatch<React.SetStateAction<string>>;
  chartDate: string;
  setChartDate: React.Dispatch<React.SetStateAction<string>>;
  isSaved: boolean;
  setIsSaved: React.Dispatch<React.SetStateAction<boolean>>;
  chartRef: React.RefObject<HTMLCanvasElement | null>;
  activeChart: any | null;
  setActiveChart: React.Dispatch<React.SetStateAction<any>>;
  previousQuery: string[];
  setPreviousQuery: React.Dispatch<React.SetStateAction<string[]>>;

  archivedList: any[];
  setArchivedList: React.Dispatch<React.SetStateAction<any>[]>;

  chartHistoryList: any[];
  setChartHistoryList: React.Dispatch<React.SetStateAction<any>[]>;

  isNew: boolean;
  setIsNew: React.Dispatch<React.SetStateAction<boolean>>;

  isClearModalOpen: boolean;
  setIsClearModalOpen: React.Dispatch<React.SetStateAction<boolean>>;

  response: any | null;
  setResponse: React.Dispatch<React.SetStateAction<any | null>>;

  showSuggestions: boolean;
  setShowSuggestions: React.Dispatch<React.SetStateAction<boolean>>;

  suggestionCache: Record<string, string[]>;
  setSuggestionCache: React.Dispatch<React.SetStateAction<Record<string, string[]>>>;



}

const ChartContext = createContext<ChartContextProps | undefined>(undefined);

export const ChartProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);
  const [assets, setAssets] = useState<{ id: string; name: string }[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // CHART STATES
  const [chartData, setChartData] = useState<any | null>(null);
  const [chartOptions, setChartOptions] = useState<any | null>(null);
  const [chartType, setChartType] = useState<string>("line");
  const [chartTitle, setChartTitle] = useState<string>("");
  const [chartDate, setChartDate] = useState<string>("");
  const [previousQuery, setPreviousQuery] = useState<string[]>([]);
  const [isSaved, setIsSaved] = useState<boolean>(false);
  const [isReply, setIsReply] = useState<boolean>(false);
  const chartRef = useRef<HTMLCanvasElement | null>(null);
  const [activeChart, setActiveChart] = useState<any | null>(null); 
  const [response, setResponse] = useState<any | null>(null);


  // LIST STATES

  const [archivedList, setArchivedList] = useState<any[]>([]);
  const [chartHistoryList, setChartHistoryList] = useState<any[]>([]);

  const [isNew, setIsNew] = useState<boolean>(true);

  const [isClearModalOpen, setIsClearModalOpen] = useState<boolean>(false);

  const [showSuggestions, setShowSuggestions] = useState<boolean>(true);
  const [suggestionCache, setSuggestionCache] = useState<Record<string, string[]>>({});





  return (
    <ChartContext.Provider
      value={{
        selectedAsset,
        setSelectedAsset,
        assets,
        setAssets,
        error,
        setError,
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
        chartRef,
        archivedList,
        setArchivedList,
        chartHistoryList,
        setChartHistoryList,
        activeChart,
        setActiveChart,
        previousQuery,
        setPreviousQuery,
        isNew,
        setIsNew,
        isClearModalOpen,
        setIsClearModalOpen,
        response,
        setResponse,
        showSuggestions,
        setShowSuggestions,
        suggestionCache,
        setSuggestionCache,


      }}
    >
      {children}
    </ChartContext.Provider>
  );
};

export const useChartContext = (): ChartContextProps => {
  const context = useContext(ChartContext);
  if (!context) {
    throw new Error("useChartContext must be used within a ChartProvider");
  }
  return context;
};
