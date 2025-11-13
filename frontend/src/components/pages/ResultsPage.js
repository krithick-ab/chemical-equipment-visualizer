import React, { useEffect, useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import { Bar, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const ResultsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [dataset, setDataset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedBarX, setSelectedBarX] = useState('Equipment Name');
  const [selectedBarY, setSelectedBarY] = useState(['Flowrate', 'Pressure', 'Temperature']);
  const [selectedPieData, setSelectedPieData] = useState('Temperature');
  const [availableColumns, setAvailableColumns] = useState([]);

  const defaultBarX = 'Equipment Name';
  const defaultBarY = ['Flowrate', 'Pressure', 'Temperature'];
  const defaultPieData = 'Temperature';

  useEffect(() => {
    const fetchDataset = async () => {
      setLoading(true);
      setError(null);
      try {
        if (location.state?.dataset) {
          setDataset(location.state.dataset);
          if (location.state.dataset.equipment_data && location.state.dataset.equipment_data.length > 0) {
            setAvailableColumns(Object.keys(location.state.dataset.equipment_data[0]));
          }
        } else if (id) {
          const token = localStorage.getItem('access_token');
          const response = await axios.get(
            `http://127.0.0.1:8000/api/equipment/datasets/${id}/`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );
          setDataset(response.data);
          if (response.data.equipment_data && response.data.equipment_data.length > 0) {
            setAvailableColumns(Object.keys(response.data.equipment_data[0]));
          }
        }
      } catch (err) {
        setError("Failed to fetch dataset details.");
      } finally {
        setLoading(false);
      }
    };

    fetchDataset();
  }, [id, location.state]);

  const handleDownload = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams({
        barX: selectedBarX,
        barY: selectedBarY.join(','),
        pieData: selectedPieData,
      }).toString();
      const response = await axios.get(
        `http://127.0.0.1:8000/api/equipment/download-report/${id}/?${params}`,
        {
          responseType: "blob",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `report_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
    } catch (err) {
      setError("Failed to download PDF report.");
    }
  };

  const handleRestoreDefaults = () => {
    setSelectedBarX(defaultBarX);
    setSelectedBarY(defaultBarY);
    setSelectedPieData(defaultPieData);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-lg text-gray-600">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-lg text-red-500">{error}</p>
      </div>
    );
  }

  if (!dataset) return null;

  const equipmentData = dataset.equipment_data || [];

  const numericColumns = availableColumns.filter(col =>
    equipmentData.length > 0 && typeof equipmentData[0][col] === 'number'
  );

  const handleBarXChange = (e) => {
    setSelectedBarX(e.target.value);
  };

  const handleBarYChange = (e) => {
    const { value, checked } = e.target;
    if (checked) {
      setSelectedBarY(prev => [...prev, value]);
    } else {
      setSelectedBarY(prev => prev.filter(col => col !== value));
    }
  };

  const handlePieDataChange = (e) => {
    setSelectedPieData(e.target.value);
  };

  const barChartData = {
    labels: equipmentData.map((e) => e[selectedBarX]),
    datasets: selectedBarY.map((yCol, index) => ({
      label: yCol,
      data: equipmentData.map((e) => e[yCol]),
      backgroundColor: [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(199, 199, 199, 0.8)',
      ][index % 7], // Cycle through 7 distinct colors
      borderColor: [
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(255, 159, 64, 1)',
        'rgba(199, 199, 199, 1)',
      ][index % 7],
      borderWidth: 1,
    })),
  };

  const getCategory = (value, min, max, type) => {
    if (type === 'Temperature') {
      if (value < 290) return "Cool (<290°C)";
      if (value >= 290 && value < 310) return "Warm (290-310°C)";
      if (value >= 310 && value < 330) return "Moderately High (310-330°C)";
      if (value >= 330 && value < 350) return "High (330-350°C)";
      return "Extremely High (>350°C)";
    } else {
      const range = max - min;
      const step = range / 4; // 4 categories
      if (value < min + step) return `Low (<${(min + step).toFixed(2)})`;
      if (value < min + 2 * step) return `Medium-Low (${(min + step).toFixed(2)}-${(min + 2 * step).toFixed(2)})`;
      if (value < min + 3 * step) return `Medium-High (${(min + 2 * step).toFixed(2)}-${(min + 3 * step).toFixed(2)})`;
      return `High (>${(min + 3 * step).toFixed(2)})`;
    }
  };

  const dynamicDistribution = equipmentData.reduce((acc, curr) => {
    const value = curr[selectedPieData];
    if (typeof value === 'number') {
      const minVal = Math.min(...equipmentData.map(e => e[selectedPieData]));
      const maxVal = Math.max(...equipmentData.map(e => e[selectedPieData]));
      const category = getCategory(value, minVal, maxVal, selectedPieData);
      acc[category] = (acc[category] || 0) + 1;
    } else {
      // Handle non-numeric data for pie chart, e.g., count occurrences
      acc[value] = (acc[value] || 0) + 1;
    }
    return acc;
  }, {});

  const pieChartData = {
    labels: Object.keys(dynamicDistribution),
    datasets: [
      {
        data: Object.values(dynamicDistribution),
        backgroundColor: [
          "rgba(54, 162, 235, 0.8)",
          "rgba(255, 206, 86, 0.8)",
          "rgba(255, 159, 64, 0.8)",
          "rgba(75, 192, 192, 0.8)",
          "rgba(255, 99, 132, 0.8)",
          "rgba(153, 102, 255, 0.8)",
          "rgba(199, 199, 199, 0.8)",
        ],
        borderColor: [
          "rgba(54, 162, 235, 1)",
          "rgba(255, 206, 86, 1)",
          "rgba(255, 159, 64, 1)",
          "rgba(75, 192, 192, 1)",
          "rgba(253, 99, 132, 1)",
          "rgba(153, 102, 255, 1)",
          "rgba(199, 199, 199, 1)",
        ],
        borderWidth: 1,
      },
    ],
  };

  const generateDataInsights = () => {
    if (equipmentData.length === 0) return [];

    const insights = [
      `The dataset contains data for ${equipmentData.length} pieces of equipment.`,
    ];

    numericColumns.forEach(col => {
      const values = equipmentData.map(e => e[col]);
      if (values.length > 0) {
        const minVal = Math.min(...values);
        const maxVal = Math.max(...values);
        const avgVal = values.reduce((sum, val) => sum + val, 0) / values.length;
        insights.push(
          `${col}: Ranges from ${minVal.toFixed(2)} to ${maxVal.toFixed(2)}. Average is <strong>${avgVal.toFixed(2)}</strong>.`
        );
      }
    });

    if (Object.keys(dynamicDistribution).length > 0) {
      insights.push(
        `Distribution of ${selectedPieData}: ${Object.entries(dynamicDistribution)
          .map(([k, v]) => `${k}: ${v} items`)
          .join(", ")}.`
      );
    }

    return insights;
  };

  const insights = generateDataInsights();

  return (
    <div className="min-h-screen bg-gray-100 font-sans">
      <header className="bg-white shadow-md sticky top-0 z-10">
        <div className="container mx-auto p-4 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Analysis Results</h1>
          <div className="flex items-center space-x-4">
            <button
              onClick={handleRestoreDefaults}
              className="bg-gray-500 text-white font-bold py-2 px-4 rounded-lg hover:bg-gray-600 transition-transform transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-gray-300"
            >
              Restore Default Charts
            </button>
            <button
              onClick={() => navigate("/homepage")}
              className="bg-blue-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-blue-700 transition-transform transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-300"
            >
              Back to Home
            </button>
            <button
              onClick={handleDownload}
              className="bg-green-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-700 transition-transform transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-green-300"
            >
              Download PDF
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto p-8">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          <div className="lg:col-span-3 grid grid-cols-1 gap-8">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">
                Parameter Comparison
              </h3>
              <div className="mb-4 flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                  <label htmlFor="bar-x-axis" className="block text-gray-700 text-sm font-bold mb-2">Bar Chart X-Axis:</label>
                  <select
                    id="bar-x-axis"
                    className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
                    value={selectedBarX}
                    onChange={handleBarXChange}
                  >
                    {availableColumns.map(col => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                </div>
                <div className="flex-1 min-w-[200px]">
                  <label className="block text-gray-700 text-sm font-bold mb-2">Bar Chart Y-Axis:</label>
                  <div className="flex flex-wrap gap-2">
                    {numericColumns.map(col => (
                      <label key={col} className="inline-flex items-center text-sm">
                        <input
                          type="checkbox"
                          className="form-checkbox h-4 w-4 text-blue-600"
                          value={col}
                          checked={selectedBarY.includes(col)}
                          onChange={handleBarYChange}
                        />
                        <span className="ml-2 text-gray-700">{col}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
              <div style={{ height: "400px" }}>
                <Bar
                  data={barChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: "top" },
                      title: { display: true, text: "Equipment Parameters" },
                    },
                  }}
                />
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">
                Distribution of {selectedPieData}
              </h3>
              <div className="mb-4">
                <label htmlFor="pie-data" className="block text-gray-700 text-sm font-bold mb-2">Pie Chart Data:</label>
                <select
                  id="pie-data"
                  className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
                  value={selectedPieData}
                  onChange={handlePieDataChange}
                >
                  {numericColumns.map(col => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>
              <div style={{ height: "400px" }}>
                <Pie
                  data={pieChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: "top" },
                      title: { display: true, text: `Distribution of ${selectedPieData}` },
                    },
                  }}
                />
              </div>
            </div>
          </div>

          <div className="lg:col-span-2 bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">
              Data Insights
            </h3>
            <ul className="space-y-4 text-left text-lg">
              {insights.map((insight, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-blue-500 font-bold mr-3 text-2xl leading-tight">›</span>
                  <p className="text-gray-700 ml-2" dangerouslySetInnerHTML={{ __html: insight }}></p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ResultsPage;