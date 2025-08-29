import React, { useState, useEffect } from 'react';
import { ImageIcon, Square, Circle, ArrowRight, LineChart } from 'lucide-react';

const Viewer = ({ image, loading, graphData }) => {
  const [showNodes, setShowNodes] = useState(true);
  const [showEdges, setShowEdges] = useState(true);
  const [showTexts, setShowTexts] = useState(true);

  // Reset visualization options when a new image is loaded
  useEffect(() => {
    if (image) {
      setShowNodes(true);
      setShowEdges(true);
      setShowTexts(true);
    }
  }, [image]);

  // When graphData changes, ensure visualization is enabled
  useEffect(() => {
    if (graphData) {
      // If we got graph data, ensure at least one visualization is enabled
      if (!showNodes && !showEdges && !showTexts) {
        setShowNodes(true);
      }
    }
  }, [graphData, showNodes, showEdges, showTexts]);

  return (
    <div className="h-full flex flex-col">
      {image && (
        <div className="bg-gray-800 p-3 mb-2 rounded-t-lg flex flex-wrap gap-4">
          <div className="flex items-center">
            <h3 className="mr-4 font-medium text-white">Visualization Controls:</h3>
          </div>
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input 
                type="checkbox" 
                checked={showNodes} 
                onChange={() => setShowNodes(!showNodes)} 
                className="rounded text-blue-500 focus:ring-blue-500"
              />
              <div className="flex items-center">
                <Square size={16} className="mr-1 text-green-400" />
                <span>Symbols</span>
              </div>
            </label>
            
            <label className="flex items-center space-x-2 cursor-pointer">
              <input 
                type="checkbox" 
                checked={showEdges} 
                onChange={() => setShowEdges(!showEdges)} 
                className="rounded text-blue-500 focus:ring-blue-500"
              />
              <div className="flex items-center">
                <LineChart size={16} className="mr-1 text-blue-400" />
                <span>Lines</span>
              </div>
            </label>
            
            <label className="flex items-center space-x-2 cursor-pointer">
              <input 
                type="checkbox" 
                checked={showTexts} 
                onChange={() => setShowTexts(!showTexts)} 
                className="rounded text-blue-500 focus:ring-blue-500"
              />
              <div className="flex items-center">
                <ArrowRight size={16} className="mr-1 text-yellow-400" />
                <span>Text</span>
              </div>
            </label>
          </div>
        </div>
      )}
      
      <div className="flex-grow bg-gray-900 rounded-lg p-4 relative flex justify-center items-center">
        {loading && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10">
            <p>Loading...</p>
          </div>
        )}
        
        <div className="relative">
          {image ? (
            <>
              <img 
                src={image} 
                alt="P&ID Diagram" 
                className="max-h-full max-w-full object-contain" 
              />
              
              {/* Visualization overlays */}
              {graphData && (
                <svg className="absolute top-0 left-0" style={{ width: '100%', height: '100%' }}>
                  {/* Draw lines/edges */}
                  {showEdges && graphData.edges && graphData.edges.map((edge, index) => (
                    <polyline 
                      key={`edge-${index}`} 
                      points={edge.polyline.map(pt => pt.join(',')).join(' ')} 
                      stroke="#3b82f6" 
                      strokeWidth="2" 
                      fill="none"
                    />
                  ))}
                  
                  {/* Draw nodes/symbols */}
                  {showNodes && graphData.nodes && graphData.nodes.map((node, index) => (
                    <rect 
                      key={`node-${index}`} 
                      x={node.bbox.x} 
                      y={node.bbox.y} 
                      width={node.bbox.w} 
                      height={node.bbox.h} 
                      stroke={node.kind === "equipment" ? "#22c55e" : "#f59e0b"} 
                      strokeWidth="2" 
                      fill="none" 
                    />
                  ))}
                  
                  {/* Draw text elements */}
                  {showTexts && graphData.texts && graphData.texts.map((text, index) => (
                    <rect 
                      key={`text-${index}`} 
                      x={text.bbox.x} 
                      y={text.bbox.y} 
                      width={text.bbox.w} 
                      height={text.bbox.h} 
                      stroke="#eab308" 
                      strokeWidth="1" 
                      fill="none" 
                      strokeDasharray="4"
                    />
                  ))}
                </svg>
              )}
            </>
          ) : (
            <div className="text-center text-gray-500">
              <ImageIcon size={48} className="mx-auto" />
              <p>Upload an image to begin</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Legend */}
      {graphData && (
        <div className="bg-gray-800 p-3 mt-2 rounded-lg flex flex-wrap gap-4 text-sm">
          <div className="flex items-center">
            <div className="w-4 h-4 border-2 border-green-400 mr-2"></div>
            <span>Equipment (Pump, Valve, Tank)</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 border-2 border-yellow-400 mr-2"></div>
            <span>Instrument Bubbles</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 border-2 border-blue-400 mr-2"></div>
            <span>Lines/Connections</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 border-2 border-yellow-400 border-dashed mr-2"></div>
            <span>Text Elements</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default Viewer;