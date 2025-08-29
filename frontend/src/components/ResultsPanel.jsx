import React, { useState } from 'react';
import { FileJson, AlertTriangle, CircleCheck, Tag, Box, Workflow, Eye } from 'lucide-react';

const ResultsPanel = ({ results, loading, analysisType, onViewerClick }) => {
  const [activeTab, setActiveTab] = useState('summary');

  // Format detection confidence as percentage
  const formatConfidence = (value) => {
    if (value === undefined || value === null) return 'N/A';
    return `${(value * 100).toFixed(1)}%`;
  };

  // Get counts of each symbol type
  const getSymbolCounts = () => {
    if (!results || !results.nodes) return {};
    
    const counts = {};
    results.nodes.forEach(node => {
      const type = node.type || 'unknown';
      counts[type] = (counts[type] || 0) + 1;
    });
    
    return counts;
  };

  // Render a summary of the analysis
  const renderSummary = () => {
    if (!results) return null;
    
    const symbolCounts = getSymbolCounts();
    const totalNodes = results.nodes?.length || 0;
    const totalEdges = results.edges?.length || 0;
    const totalTexts = results.texts?.length || 0;
    const totalIssues = results.issues?.length || 0;
    
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-white mb-2">Analysis Summary</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-800 p-4 rounded-lg">
            <h4 className="text-blue-400 font-medium mb-2 flex items-center">
              <Box className="mr-2" size={18} />
              Detected Symbols ({totalNodes})
            </h4>
            {Object.entries(symbolCounts).length > 0 ? (
              <ul className="space-y-2">
                {Object.entries(symbolCounts).map(([type, count]) => (
                  <li key={type} className="flex justify-between">
                    <span className="text-gray-300 capitalize">{type.replace('_', ' ')}</span>
                    <span className="text-white font-medium">{count}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-400">No symbols detected</p>
            )}
          </div>
          
          <div className="bg-gray-800 p-4 rounded-lg">
            <h4 className="text-green-400 font-medium mb-2 flex items-center">
              <Workflow className="mr-2" size={18} />
              Connections & Text
            </h4>
            <ul className="space-y-2">
              <li className="flex justify-between">
                <span className="text-gray-300">Process Lines</span>
                <span className="text-white font-medium">{totalEdges}</span>
              </li>
              <li className="flex justify-between">
                <span className="text-gray-300">Text Elements</span>
                <span className="text-white font-medium">{totalTexts}</span>
              </li>
            </ul>
          </div>
        </div>
        
        {totalIssues > 0 && (
          <div className="bg-gray-800 p-4 rounded-lg">
            <h4 className="text-yellow-400 font-medium mb-2 flex items-center">
              <AlertTriangle className="mr-2" size={18} />
              Issues Detected ({totalIssues})
            </h4>
            <ul className="space-y-2 max-h-40 overflow-y-auto">
              {results.issues.map((issue, index) => (
                <li key={index} className="flex items-start">
                  <span className={`mr-2 mt-1 ${issue.severity === 'error' ? 'text-red-500' : 'text-yellow-400'}`}>•</span>
                  <span className="text-gray-300">{issue.message}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  // Render detailed tables for symbols
  const renderSymbols = () => {
    if (!results || !results.nodes || results.nodes.length === 0) {
      return <p className="text-gray-400">No symbols detected in the diagram.</p>;
    }
    
    return (
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-800 text-left">
              <th className="p-2 border-b border-gray-700">Type</th>
              <th className="p-2 border-b border-gray-700">Category</th>
              <th className="p-2 border-b border-gray-700">Tag</th>
              <th className="p-2 border-b border-gray-700">Confidence</th>
              <th className="p-2 border-b border-gray-700">Position</th>
            </tr>
          </thead>
          <tbody>
            {results.nodes.map((node, index) => (
              <tr key={index} className="border-b border-gray-800 hover:bg-gray-800">
                <td className="p-2 capitalize">{(node.type || 'unknown').replace('_', ' ')}</td>
                <td className="p-2 capitalize">{node.kind || 'unknown'}</td>
                <td className="p-2">{node.tag || '-'}</td>
                <td className="p-2">{formatConfidence(node.confidence)}</td>
                <td className="p-2 text-xs">
                  ({node.bbox.x}, {node.bbox.y}) {node.bbox.w}×{node.bbox.h}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  // Render detailed tables for connections
  const renderConnections = () => {
    if (!results || !results.edges || results.edges.length === 0) {
      return <p className="text-gray-400">No connections detected in the diagram.</p>;
    }
    
    return (
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-800 text-left">
              <th className="p-2 border-b border-gray-700">Type</th>
              <th className="p-2 border-b border-gray-700">Direction</th>
              <th className="p-2 border-b border-gray-700">Connected Nodes</th>
              <th className="p-2 border-b border-gray-700">Points</th>
            </tr>
          </thead>
          <tbody>
            {results.edges.map((edge, index) => (
              <tr key={index} className="border-b border-gray-800 hover:bg-gray-800">
                <td className="p-2 capitalize">{edge.kind || 'unknown'}</td>
                <td className="p-2">{edge.direction || 'unknown'}</td>
                <td className="p-2">
                  {edge.endpoints ? (
                    <span>
                      {edge.endpoints[0] || 'none'} → {edge.endpoints[1] || 'none'}
                    </span>
                  ) : 'none'}
                </td>
                <td className="p-2 text-xs">
                  {edge.polyline ? `${edge.polyline.length} points` : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  // Render text elements
  const renderTexts = () => {
    if (!results || !results.texts || results.texts.length === 0) {
      return <p className="text-gray-400">No text elements detected in the diagram.</p>;
    }
    
    return (
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-800 text-left">
              <th className="p-2 border-b border-gray-700">Content</th>
              <th className="p-2 border-b border-gray-700">Position</th>
            </tr>
          </thead>
          <tbody>
            {results.texts.map((text, index) => (
              <tr key={index} className="border-b border-gray-800 hover:bg-gray-800">
                <td className="p-2">{text.content || '-'}</td>
                <td className="p-2 text-xs">
                  ({text.bbox.x}, {text.bbox.y}) {text.bbox.w}×{text.bbox.h}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  // Render issues
  const renderIssues = () => {
    if (!results || !results.issues || results.issues.length === 0) {
      return (
        <div className="flex items-center justify-center p-4 bg-gray-800 rounded-lg">
          <CircleCheck className="mr-2 text-green-500" size={24} />
          <p className="text-green-400">No issues detected in the diagram.</p>
        </div>
      );
    }
    
    return (
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-800 text-left">
              <th className="p-2 border-b border-gray-700">Severity</th>
              <th className="p-2 border-b border-gray-700">Message</th>
              <th className="p-2 border-b border-gray-700">Related Element</th>
            </tr>
          </thead>
          <tbody>
            {results.issues.map((issue, index) => (
              <tr key={index} className="border-b border-gray-800 hover:bg-gray-800">
                <td className="p-2">
                  <span className={`inline-block px-2 py-1 rounded text-xs ${
                    issue.severity === 'error' ? 'bg-red-900 text-red-300' :
                    issue.severity === 'warn' ? 'bg-yellow-900 text-yellow-300' :
                    'bg-blue-900 text-blue-300'
                  }`}>
                    {issue.severity}
                  </span>
                </td>
                <td className="p-2">{issue.message}</td>
                <td className="p-2">{issue.targetId || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  // Render raw data
  const renderRawData = () => {
    if (!results) return null;
    
    return (
      <pre className="text-sm whitespace-pre-wrap break-words bg-gray-800 p-4 rounded-lg overflow-auto max-h-96">
        {JSON.stringify(results, null, 2)}
      </pre>
    );
  };

  // Render active tab content
  const renderTabContent = () => {
    switch (activeTab) {
      case 'summary':
        return renderSummary();
      case 'symbols':
        return renderSymbols();
      case 'connections':
        return renderConnections();
      case 'texts':
        return renderTexts();
      case 'issues':
        return renderIssues();
      case 'raw':
        return renderRawData();
      default:
        return renderSummary();
    }
  };

  return (
    <div className="h-full flex flex-col">
      {results && (
        <div className="bg-gray-800 p-2 mb-2 rounded-t-lg overflow-x-auto">
          <div className="flex space-x-1 items-center">
            <button
              onClick={() => setActiveTab('summary')}
              className={`px-3 py-2 text-sm rounded-t-lg ${activeTab === 'summary' ? 'bg-gray-900 text-white' : 'text-gray-400 hover:bg-gray-700'}`}
            >
              Summary
            </button>
            {analysisType !== 'ocr' && (
              <button
                onClick={() => setActiveTab('symbols')}
                className={`px-3 py-2 text-sm rounded-t-lg ${activeTab === 'symbols' ? 'bg-gray-900 text-white' : 'text-gray-400 hover:bg-gray-700'}`}
              >
                Symbols ({results.nodes?.length || 0})
              </button>
            )}
            {analysisType !== 'ocr' && (
              <button
                onClick={() => setActiveTab('connections')}
                className={`px-3 py-2 text-sm rounded-t-lg ${activeTab === 'connections' ? 'bg-gray-900 text-white' : 'text-gray-400 hover:bg-gray-700'}`}
              >
                Connections ({results.edges?.length || 0})
              </button>
            )}
            {(analysisType === 'ocr' || analysisType === 'graph') && (
              <button
                onClick={() => setActiveTab('texts')}
                className={`px-3 py-2 text-sm rounded-t-lg ${activeTab === 'texts' ? 'bg-gray-900 text-white' : 'text-gray-400 hover:bg-gray-700'}`}
              >
                Texts ({results.texts?.length || 0})
              </button>
            )}
            {(analysisType === 'validate' || analysisType === 'graph') && (
              <button
                onClick={() => setActiveTab('issues')}
                className={`px-3 py-2 text-sm rounded-t-lg flex items-center ${activeTab === 'issues' ? 'bg-gray-900 text-white' : 'text-gray-400 hover:bg-gray-700'}`}
              >
                <span>Issues</span>
                {results.issues && results.issues.length > 0 && (
                  <span className="ml-1 px-1.5 py-0.5 text-xs bg-yellow-600 text-white rounded-full">
                    {results.issues.length}
                  </span>
                )}
              </button>
            )}
            <button
              onClick={() => setActiveTab('raw')}
              className={`px-3 py-2 text-sm rounded-t-lg ${activeTab === 'raw' ? 'bg-gray-900 text-white' : 'text-gray-400 hover:bg-gray-700'}`}
            >
              Raw JSON
            </button>
            
            {analysisType === 'graph' && (
              <button
                onClick={onViewerClick}
                className="ml-auto px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-1"
              >
                <Eye size={16} />
                <span>View Visualization</span>
              </button>
            )}
          </div>
        </div>
      )}
      
      <div className="flex-grow bg-gray-900 rounded-lg p-4 relative overflow-auto">
        {loading && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10">
            <p>Processing...</p>
          </div>
        )}
        
        {results ? (
          renderTabContent()
        ) : (
          <div className="text-center text-gray-500 flex flex-col items-center justify-center h-full">
            <FileJson size={48} className="mx-auto" />
            <p>Analysis results will be shown here</p>
            <p className="text-sm mt-2 text-gray-600">
              Click on one of the analysis buttons in the control panel to start
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPanel;