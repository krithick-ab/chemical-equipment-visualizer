import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const HomePage = () => {
  const [file, setFile] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setTimeout(() => {
        navigate(`/results/${response.data.id}`);
      }, 2000);
    } catch (err) {
      setError('File upload failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/history/');
      setHistory(response.data);
    } catch (err) {
      setError('Failed to fetch history.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto p-4">
        <div className="bg-white rounded-lg shadow-md p-6 my-8">
          <h2 className="text-2xl font-bold mb-4 text-center">Upload your chemical equipment CSV file below</h2>
          <div className="flex flex-col items-center">
            <input type="file" onChange={handleFileChange} className="mb-4" />
            <button onClick={handleUpload} className="bg-blue-500 text-white px-4 py-2 rounded-md" disabled={loading}>
              {loading ? 'Uploading...' : 'Upload'}
            </button>
            {error && <p className="text-red-500 mt-4">{error}</p>}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold mb-4 text-center">View History</h2>
          <div className="flex justify-center">
            <button onClick={fetchHistory} className="bg-blue-500 text-white px-4 py-2 rounded-md" disabled={loading}>
              {loading ? 'Loading...' : 'View History'}
            </button>
          </div>
          <ul className="mt-4">
            {history.map((item) => (
              <li key={item.id} className="border-b py-2 flex justify-between items-center">
                <span>{item.filename} - {new Date(item.uploaded_at).toLocaleString()}</span>
                <button onClick={() => navigate(`/results/${item.id}`)} className="bg-gray-200 px-3 py-1 rounded-md">View</button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default HomePage;