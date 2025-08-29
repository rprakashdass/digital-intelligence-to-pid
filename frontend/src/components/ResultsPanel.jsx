import React from 'react';
import { FileJson } from 'lucide-react';

const ResultsPanel = ({ results, loading }) => {
  return (
    <div className="h-full flex flex-col">
      <div className="flex-grow bg-gray-900 rounded-lg p-4 relative">
        {loading && <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10"><p>Processing...</p></div>}
        {results ? (
          <pre className="text-sm whitespace-pre-wrap break-words">{JSON.stringify(results, null, 2)}</pre>
        ) : (
          <div className="text-center text-gray-500 flex flex-col items-center justify-center h-full">
            <FileJson size={48} className="mx-auto" />
            <p>Analysis results will be shown here</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPanel;