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

  const handleImageUpload = async (file) => {
    setLoading(true);
    setResults(null); // Clear previous results
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
    setResults(null);
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
          break;
        default:
          break;
      }
      setResults(data);
      setActiveTab('results');
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
        <div className="flex border-b border-gray-700">
          <button onClick={() => setActiveTab('viewer')} className={`px-4 py-2 -mb-px border-b-2 ${activeTab === 'viewer' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-white'}`}>Viewer</button>
          <button onClick={() => setActiveTab('results')} className={`px-4 py-2 -mb-px border-b-2 ${activeTab === 'results' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-white'}`}>Results</button>
        </div>
        <div className="flex-grow bg-gray-800 rounded-b-lg mt-2">
          {activeTab === 'viewer' ? <Viewer image={image} loading={loading && !results} /> : <ResultsPanel results={results} loading={loading && !image} />}
        </div>
      </main>
    </div>
  );
}

export default App;