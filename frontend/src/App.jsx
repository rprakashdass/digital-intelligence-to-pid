import React, { useState } from 'react';
import ControlPanel from './components/ControlPanel';
import Viewer from './components/Viewer';
import ResultsPanel from './components/ResultsPanel';
import { uploadImage, runValidation, runOCR, runGraph, runExport } from './services/api';
// import './App.css';

function App() {
  const [image, setImage] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('viewer'); // viewer or results
  const [graphData, setGraphData] = useState(null);
  const [analysisType, setAnalysisType] = useState(null); // To track what type of analysis was performed

  const handleImageUpload = async (file) => {
    setLoading(true);
    setResults(null); // Clear previous results
    setGraphData(null); // Clear previous graph data
    setAnalysisType(null); // Reset analysis type
    try {
      await uploadImage(file);
      setImage(URL.createObjectURL(file));
      setActiveTab('viewer');
    } catch (error) {
      console.error("Error uploading image:", error);
    }
    setLoading(false);
  };

  const handleRun = async (type) => {
    setLoading(true);
    try {
      let data;
      if (type === 'export') {
        const blob = await runExport();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'results.zip'; // or other appropriate filename
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        setLoading(false);
        return;
      }

      switch (type) {
        case 'validate':
          data = await runValidation();
          break;
        case 'ocr':
          data = await runOCR();
          break;
        case 'graph':
          data = await runGraph();
          // Save graph data for visualization
          setGraphData(data);
          // When running graph analysis, stay on viewer tab to see visualization
          setActiveTab('viewer');
          break;
        default:
          break;
      }
      setResults(data);
      setAnalysisType(type);
      
      // Only switch to results tab for validate and OCR
      if (type === 'validate' || type === 'ocr') {
        setActiveTab('results');
      }
    } catch (error) {
      console.error(`Error running ${type}:`, error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col">
      <header className="bg-gray-800 shadow-md p-4">
        <h1 className="text-2xl font-bold text-center text-white">P&ID Diagram Analyzer</h1>
      </header>
      <ControlPanel onImageUpload={handleImageUpload} onRun={handleRun} loading={loading} />
      <main className="flex-grow p-4 flex flex-col">
        {image && (
          <div className="flex border-b border-gray-700 mb-2">
            <button 
              onClick={() => setActiveTab('viewer')} 
              className={`px-4 py-2 -mb-px border-b-2 ${activeTab === 'viewer' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-white'}`}
            >
              Viewer {graphData && '(with visualization)'}
            </button>
            <button 
              onClick={() => setActiveTab('results')} 
              className={`px-4 py-2 -mb-px border-b-2 ${activeTab === 'results' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-white'}`}
              disabled={!results}
            >
              Analysis Results {results && `(${analysisType})`}
            </button>
            
            {/* Add a Run Analysis button directly in the tab bar for convenience */}
            {activeTab === 'viewer' && !graphData && (
              <button
                onClick={() => handleRun('graph')}
                disabled={loading || !image}
                className="ml-auto px-3 py-1 mr-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? "Analyzing..." : "Run Analysis"}
              </button>
            )}
          </div>
        )}
        
        <div className="flex-grow bg-gray-800 rounded-lg">
          {activeTab === 'viewer' ? (
            <Viewer 
              image={image} 
              loading={loading} 
              graphData={graphData} 
            />
          ) : (
            <ResultsPanel 
              results={results} 
              loading={loading} 
              analysisType={analysisType}
              onViewerClick={() => setActiveTab('viewer')}
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;