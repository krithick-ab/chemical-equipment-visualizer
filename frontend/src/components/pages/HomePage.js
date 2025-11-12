import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const HomePage = () => {
  const [file, setFile] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showHistory, setShowHistory] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/history/");
      setHistory(response.data);
    } catch (error) {
      console.error("Error fetching history:", error);
      setError("Failed to fetch history. Please try again later.");
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file to upload.");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/upload/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      navigate(`/results/${response.data.dataset_id}`);
    } catch (error) {
      console.error("Error uploading file:", error);
      setError("Error uploading file. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleHistoryClick = (datasetId) => {
    navigate(`/results/${datasetId}`);
  };

  const toggleHistory = () => {
    setShowHistory(!showHistory);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center font-sans">
      <div className="w-full max-w-3xl mx-auto p-8">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            Equipment Data Analysis
          </h1>
          <p className="text-lg text-gray-600">
            Upload your CSV file to get instant insights and visualizations.
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <div className="flex flex-col items-center">
            <div className="w-full">
              <label
                htmlFor="file-upload"
                className="flex flex-col items-center justify-center w-full h-64 border-4 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 transition-colors"
              >
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <svg
                    className="w-10 h-10 mb-3 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M7 16a4 4 0 01-4-4V7a4 4 0 014-4h5l4 4v5a4 4 0 01-4 4H7z"
                    ></path>
                  </svg>
                  <p className="mb-2 text-sm text-gray-500">
                    <span className="font-semibold">Click to upload</span> or
                    drag and drop
                  </p>
                  <p className="text-xs text-gray-500">
                    CSV files only (MAX. 800x400px)
                  </p>
                </div>
                <input
                  id="file-upload"
                  type="file"
                  className="hidden"
                  onChange={handleFileChange}
                />
              </label>
              {file && (
                <p className="text-center mt-4 text-gray-600">
                  Selected file: {file.name}
                </p>
              )}
            </div>

            <button
              onClick={handleUpload}
              className="mt-6 w-full bg-blue-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-blue-700 transition-transform transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-300 disabled:bg-gray-400"
              disabled={loading}
            >
              {loading ? "Uploading..." : "Analyze Now"}
            </button>

            {error && <p className="mt-4 text-red-500">{error}</p>}
          </div>
        </div>

        <div className="text-center">
          <button
            onClick={toggleHistory}
            className="text-blue-600 font-semibold hover:underline focus:outline-none"
          >
            {showHistory ? "Hide" : "Show"} Upload History
          </button>
        </div>

        {showHistory && (
          <div className="mt-6 bg-white rounded-xl shadow-lg p-8 animate-slide-down">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
              Upload History
            </h2>
            {history.length > 0 ? (
              <ul className="space-y-4">
                {history.map((item) => (
                  <li
                    key={item.id}
                    onClick={() => handleHistoryClick(item.id)}
                    className="p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-gray-700">
                        {item.filename}
                      </span>
                      <span className="text-sm text-gray-500">
                        {new Date(item.uploaded_at).toLocaleString()}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-center text-gray-500">No history found.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePage;