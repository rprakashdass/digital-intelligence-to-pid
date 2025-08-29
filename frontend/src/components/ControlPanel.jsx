import React, { useState, useRef } from 'react';
import { Upload, Play, FileCheck, FileText, GitFork, FileDown } from 'lucide-react';

const ControlPanel = ({ onImageUpload, onRun, loading }) => {
  const [selectedFile, setSelectedFile] = useState(null);
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

  return (
    <div className="bg-gray-800 p-4 flex justify-between items-center shadow-md">
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
      </div>
      <div className="flex items-center gap-2">
        <button onClick={() => onRun('validate')} disabled={loading} title="Run Validation" className="p-2 bg-gray-700 rounded-lg hover:bg-gray-600 disabled:opacity-50 transition-colors">
          <FileCheck size={20} />
        </button>
        <button onClick={() => onRun('ocr')} disabled={loading} title="Run OCR" className="p-2 bg-gray-700 rounded-lg hover:bg-gray-600 disabled:opacity-50 transition-colors">
          <FileText size={20} />
        </button>
        <button onClick={() => onRun('graph')} disabled={loading} title="Run Graph" className="p-2 bg-gray-700 rounded-lg hover:bg-gray-600 disabled:opacity-50 transition-colors">
          <GitFork size={20} />
        </button>
        <button onClick={() => onRun('export')} disabled={loading} title="Export Results" className="p-2 bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors">
          <FileDown size={20} />
        </button>
      </div>
    </div>
  );
};

export default ControlPanel;