const API_URL = 'http://localhost:8000';

export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${API_URL}/upload`, {
    method: 'POST',
    body: formData,
  });
  return response.json();
};

export const uploadVideo = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${API_URL}/upload/video`, {
    method: 'POST',
    body: formData,
  });
  return response.json();
};

export const runValidation = async () => {
  const response = await fetch(`${API_URL}/run/validate`, { method: 'POST' });
  return response.json();
};

export const runOCR = async () => {
  const response = await fetch(`${API_URL}/run/ocr`, { method: 'POST' });
  return response.json();
};

export const runGraph = async () => {
  try {
    const response = await fetch(`${API_URL}/run/graph`, { 
      method: 'POST',
      headers: {
        'Accept': 'application/json',
      }
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`API Error (${response.status}): ${errorText}`);
      throw new Error(`Server error: ${response.status} - ${errorText}`);
    }
    
    return response.json();
  } catch (error) {
    console.error("Error running graph analysis:", error);
    throw error;
  }
};

export const runExport = async () => {
  const response = await fetch(`${API_URL}/run/export`, { method: 'POST' });
  // This might trigger a file download
  return response.blob();
};
