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

  useEffect(() => {
    const fetchDataset = async () => {
      setLoading(true);
      setError(null);
      try {
        if (location.state?.dataset) {
          setDataset(location.state.dataset);
        } else if (id) {
          const response = await axios.get(
            `http://127.0.0.1:8000/api/datasets/${id}/`
          );
          setDataset(response.data);
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
      const response = await axios.get(
        `http://127.0.0.1:8000/api/download-report/${id}/`,
        {
          responseType: "blob",
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

  const barChartData = {
    labels: equipmentData.map((e) => e["Equipment Name"]),
    datasets: [
      {
        label: "Flowrate",
        data: equipmentData.map((e) => e.Flowrate),
        backgroundColor: "rgba(54, 162, 235, 0.8)",
        borderColor: "rgba(54, 162, 235, 1)",
        borderWidth: 1,
      },
      {
        label: "Pressure",
        data: equipmentData.map((e) => e.Pressure),
        backgroundColor: "rgba(255, 99, 132, 0.8)",
        borderColor: "rgba(255, 99, 132, 1)",
        borderWidth: 1,
      },
      {
        label: "Temperature",
        data: equipmentData.map((e) => e.Temperature),
        backgroundColor: "rgba(75, 192, 192, 0.8)",
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 1,
      },
    ],
  };

  const getTemperatureCategory = (temperature) => {
    if (temperature < 290) return "Cool (<290°C)";
    if (temperature >= 290 && temperature < 310) return "Warm (290-310°C)";
    if (temperature >= 310 && temperature < 330)
      return "Moderately High (310-330°C)";
    if (temperature >= 330 && temperature < 350) return "High (330-350°C)";
    return "Extremely High (>350°C)";
  };

  const temperatureDistribution = equipmentData.reduce((acc, curr) => {
    const category = getTemperatureCategory(curr.Temperature);
    acc[category] = (acc[category] || 0) + 1;
    return acc;
  }, {});

  const pieChartData = {
    labels: Object.keys(temperatureDistribution),
    datasets: [
      {
        data: Object.values(temperatureDistribution),
        backgroundColor: [
          "rgba(54, 162, 235, 0.8)",
          "rgba(255, 206, 86, 0.8)",
          "rgba(255, 159, 64, 0.8)",
          "rgba(75, 192, 192, 0.8)",
          "rgba(255, 99, 132, 0.8)",
        ],
        borderColor: [
          "rgba(54, 162, 235, 1)",
          "rgba(255, 206, 86, 1)",
          "rgba(255, 159, 64, 1)",
          "rgba(75, 192, 192, 1)",
          "rgba(255, 99, 132, 1)",
        ],
        borderWidth: 1,
      },
    ],
  };

  const generateDataInsights = () => {
    if (equipmentData.length === 0) return [];

    const equipmentWithMax = (prop) =>
      equipmentData.reduce((max, e) => (e[prop] > max[prop] ? e : max), equipmentData[0]);
    const equipmentWithMin = (prop) =>
      equipmentData.reduce((min, e) => (e[prop] < min[prop] ? e : min), equipmentData[0]);

    const maxFlowrateEq = equipmentWithMax("Flowrate");
    const minFlowrateEq = equipmentWithMin("Flowrate");
    const maxPressureEq = equipmentWithMax("Pressure");
    const minPressureEq = equipmentWithMin("Pressure");
    const maxTempEq = equipmentWithMax("Temperature");
    const minTempEq = equipmentWithMin("Temperature");

    return [
      `The dataset includes ${equipmentData.length} pieces of equipment.`,
      `Flowrate: Highest is ${maxFlowrateEq.Flowrate} (${maxFlowrateEq["Equipment Name"]}), Lowest is ${minFlowrateEq.Flowrate} (${minFlowrateEq["Equipment Name"]}).`,
      `Pressure: Highest is ${maxPressureEq.Pressure} (${maxPressureEq["Equipment Name"]}), Lowest is ${minPressureEq.Pressure} (${minPressureEq["Equipment Name"]}).`,
      `Temperature: Highest is ${maxTempEq.Temperature}°C (${maxTempEq["Equipment Name"]}), Lowest is ${minTempEq.Temperature}°C (${minTempEq["Equipment Name"]}).`,
      `The pie chart shows the temperature distribution: ${Object.entries(
        temperatureDistribution
      )
        .map(([k, v]) => `${v} equipment in the ${k} range`)
        .join(", ")}.`,
    ];
  };

  const insights = generateDataInsights();

  return (
    <div className="min-h-screen bg-gray-100 font-sans">
      <header className="bg-white shadow-md sticky top-0 z-10">
        <div className="container mx-auto p-4 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Analysis Results</h1>
          <div>
            <button
              onClick={() => navigate("/")}
              className="bg-blue-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-blue-700 transition-transform transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-300 mr-4"
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
                Temperature Distribution
              </h3>
              <div style={{ height: "400px" }}>
                <Pie
                  data={pieChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: "top" },
                      title: { display: true, text: "Temperature Categories" },
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
            <ul className="space-y-3">
              {insights.map((insight, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-blue-500 font-bold mr-2 text-lg leading-tight">›</span>
                  <p className="text-gray-700 ml-2">{insight}</p>
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