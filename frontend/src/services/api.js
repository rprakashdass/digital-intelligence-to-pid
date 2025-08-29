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

export const runValidation = async () => {
  const response = await fetch(`${API_URL}/run/validate`, { method: 'POST' });
  return response.json();
};

export const runOCR = async () => {
  const response = await fetch(`${API_URL}/run/ocr`, { method: 'POST' });
  return response.json();
};

export const runGraph = async () => {
  const response = await fetch(`${API_URL}/run/graph`, { method: 'POST' });
  return response.json();
};

export const runExport = async () => {
  const response = await fetch(`${API_URL}/run/export`, { method: 'POST' });
  // This might trigger a file download
  return response.blob();
};
