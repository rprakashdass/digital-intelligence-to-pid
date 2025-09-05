import React, { useState } from 'react';
import { MessageCircle, Send, Video, Image, Brain, AlertCircle, Upload } from 'lucide-react';

const RAGPanel = ({ imageId, onVideoUpload, loading }) => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [isQuerying, setIsQuerying] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadType, setUploadType] = useState('image'); // 'image' or 'video'
  const fileInputRef = React.useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      if (uploadType === 'video') {
        onVideoUpload(file);
      }
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleQuery = async () => {
    if (!query.trim() || !imageId) return;

    setIsQuerying(true);
    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_id: imageId,
          query: query.trim()
        })
      });

      if (response.ok) {
        const data = await response.json();
        setResponse(data);
      } else {
        const error = await response.json();
        setResponse({
          answer: `Error: ${error.detail || 'Failed to process query'}`,
          confidence: 0,
          knowledge_sources: []
        });
      }
    } catch (error) {
      setResponse({
        answer: `Error: ${error.message}`,
        confidence: 0,
        knowledge_sources: []
      });
    } finally {
      setIsQuerying(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQuery();
    }
  };

  const exampleQueries = [
    "What does FIC-101 do?",
    "Explain the function of the pump in this diagram",
    "What safety systems are present?",
    "Are there any issues with this P&ID?",
    "What type of control system is used?",
    "Describe the process flow"
  ];

  return (
    <div className="bg-gray-800 p-4 rounded-lg shadow-md">
      <div className="flex items-center gap-2 mb-4">
        <Brain className="text-blue-400" size={20} />
        <h3 className="text-lg font-semibold text-white">Smart Q&A</h3>
      </div>

      {/* Upload Type Selection */}
      <div className="mb-4">
        <div className="flex gap-2 mb-2">
          <button
            onClick={() => setUploadType('image')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
              uploadType === 'image' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <Image size={16} />
            Image
          </button>
          <button
            onClick={() => setUploadType('video')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
              uploadType === 'video' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <Video size={16} />
            Video
          </button>
        </div>

        {/* File Upload */}
        <div className="mb-4">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
            accept={uploadType === 'video' ? 'video/*' : 'image/*'}
          />
          <button 
            onClick={handleUploadClick} 
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50 transition-colors w-full"
          >
            <Upload size={16} />
            <span>
              {selectedFile ? selectedFile.name : `Upload ${uploadType === 'video' ? 'Video' : 'Image'}`}
            </span>
          </button>
        </div>
      </div>

      {/* Query Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Ask a question about the P&ID:
        </label>
        <div className="flex gap-2">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="e.g., What does FIC-101 do?"
            className="flex-1 px-3 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
            rows={2}
            disabled={isQuerying || !imageId}
          />
          <button
            onClick={handleQuery}
            disabled={isQuerying || !query.trim() || !imageId}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={16} />
          </button>
        </div>
      </div>

      {/* Example Queries */}
      <div className="mb-4">
        <p className="text-sm text-gray-400 mb-2">Try these examples:</p>
        <div className="flex flex-wrap gap-2">
          {exampleQueries.map((example, index) => (
            <button
              key={index}
              onClick={() => setQuery(example)}
              className="px-3 py-1 bg-gray-700 text-gray-300 text-xs rounded-full hover:bg-gray-600 transition-colors"
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* Response */}
      {response && (
        <div className="mt-4 p-4 bg-gray-700 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <MessageCircle className="text-green-400" size={16} />
            <span className="text-sm font-medium text-gray-300">Response</span>
            {response.confidence > 0 && (
              <span className="text-xs text-gray-400">
                (Confidence: {(response.confidence * 100).toFixed(1)}%)
              </span>
            )}
          </div>
          
          <div className="text-white text-sm leading-relaxed mb-3">
            {response.answer}
          </div>

          {/* Knowledge Sources */}
          {response.knowledge_sources && response.knowledge_sources.length > 0 && (
            <div className="border-t border-gray-600 pt-3">
              <p className="text-xs text-gray-400 mb-2">Knowledge Sources:</p>
              <div className="space-y-1">
                {response.knowledge_sources.map((source, index) => (
                  <div key={index} className="text-xs text-gray-300">
                    <span className="text-blue-400">{source.type}</span>: {source.key}
                    {source.similarity && (
                      <span className="text-gray-500 ml-2">
                        ({(source.similarity * 100).toFixed(1)}% match)
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Analysis Summary */}
          {response.analysis_summary && (
            <div className="border-t border-gray-600 pt-3 mt-3">
              <p className="text-xs text-gray-400 mb-2">Analysis Summary:</p>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="text-center">
                  <div className="text-blue-400 font-medium">{response.analysis_summary.symbols_detected}</div>
                  <div className="text-gray-400">Symbols</div>
                </div>
                <div className="text-center">
                  <div className="text-green-400 font-medium">{response.analysis_summary.text_elements}</div>
                  <div className="text-gray-400">Text</div>
                </div>
                <div className="text-center">
                  <div className="text-yellow-400 font-medium">{response.analysis_summary.issues_found}</div>
                  <div className="text-gray-400">Issues</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {isQuerying && (
        <div className="mt-4 p-4 bg-gray-700 rounded-lg">
          <div className="flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400"></div>
            <span className="text-gray-300 text-sm">Processing your question...</span>
          </div>
        </div>
      )}

      {/* No Image Warning */}
      {!imageId && (
        <div className="mt-4 p-3 bg-yellow-900/20 border border-yellow-600/30 rounded-lg">
          <div className="flex items-center gap-2">
            <AlertCircle className="text-yellow-400" size={16} />
            <span className="text-yellow-300 text-sm">
              Please upload a P&ID image or video first to ask questions.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default RAGPanel;
