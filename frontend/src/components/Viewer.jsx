import React from 'react';
import { ImageIcon } from 'lucide-react';

const Viewer = ({ image, loading }) => {
  return (
    <div className="h-full flex flex-col">
      <div className="flex-grow bg-gray-900 rounded-lg p-4 relative flex justify-center items-center">
        {loading && <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10"><p>Loading...</p></div>}
        {image ? (
          <img src={image} alt="P&ID Diagram" className="max-h-full max-w-full object-contain" />
        ) : (
          <div className="text-center text-gray-500">
            <ImageIcon size={48} className="mx-auto" />
            <p>Upload an image to begin</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Viewer;