import React, { useState, useRef } from 'react';
import { Upload, Play, FileCheck, FileText, GitFork, FileDown, Info } from 'lucide-react';

const ControlPanel = ({ onImageUpload, onRun, loading }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [showSymbolInfo, setShowSymbolInfo] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      onImageUpload(file);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const toggleSymbolInfo = () => {
    setShowSymbolInfo(!showSymbolInfo);
  };

  return (
    <div className="bg-gray-800 p-4 flex flex-col gap-4 shadow-md">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
            accept="image/*"
          />
          <button onClick={handleUploadClick} disabled={loading} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors">
            <Upload size={20} />
            <span>{selectedFile ? selectedFile.name : 'Upload P&ID'}</span>
          </button>
          <button onClick={toggleSymbolInfo} className="flex items-center gap-2 px-3 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors">
            <Info size={18} />
            <span>Supported Symbols</span>
          </button>
        </div>
        <div className="flex items-center gap-3">
          {/* Analysis dropdown menu */}
          <div className="relative group">
            <button 
              disabled={loading} 
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              <GitFork size={18} />
              <span>Analyze</span>
              <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            <div className="absolute right-0 mt-1 w-48 bg-gray-700 rounded-md shadow-lg overflow-hidden z-10 invisible group-hover:visible">
              <button 
                onClick={() => onRun('graph')} 
                disabled={loading}
                className="w-full text-left px-4 py-2 text-sm text-white hover:bg-gray-600 flex items-center gap-2"
              >
                <GitFork size={16} />
                <span>Complete Analysis</span>
              </button>
              <button 
                onClick={() => onRun('validate')} 
                disabled={loading}
                className="w-full text-left px-4 py-2 text-sm text-white hover:bg-gray-600 flex items-center gap-2"
              >
                <FileCheck size={16} />
                <span>Validation Only</span>
              </button>
              <button 
                onClick={() => onRun('ocr')} 
                disabled={loading}
                className="w-full text-left px-4 py-2 text-sm text-white hover:bg-gray-600 flex items-center gap-2"
              >
                <FileText size={16} />
                <span>OCR Only</span>
              </button>
            </div>
          </div>
          
          <button 
            onClick={() => onRun('export')} 
            disabled={loading} 
            title="Export Results" 
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <FileDown size={18} />
            <span>Export</span>
          </button>
        </div>
      </div>
      
      {showSymbolInfo && (
        <div className="bg-gray-700 p-3 rounded-lg text-sm">
          <h3 className="text-white font-semibold mb-2">Currently Supported ISA-5.1 Symbols:</h3>
          <ul className="text-gray-200 list-disc pl-5 space-y-1">
            <li>Pump</li>
            <li>Manual valve</li>
            <li>Control valve</li>
            <li>Instrument bubble</li>
            <li>Tank/vessel</li>
          </ul>
          <p className="text-gray-300 mt-2 text-xs">All other shapes will be flagged as "Unknown Symbol" in the issues list for review.</p>
        </div>
      )}
    </div>
  );
};

export default ControlPanel;