import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Bar, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const ResultsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [dataset, setDataset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDataset = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/datasets/${id}/`);
        setDataset(response.data);
      } catch (err) {
        setError('Failed to fetch dataset details.');
      } finally {
        setLoading(false);
      }
    };
    fetchDataset();
  }, [id]);

  const handleDownload = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/download-report/${id}/`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
    } catch (err) {
      setError('Failed to download PDF report.');
    }
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p className="text-red-500">{error}</p>;
  if (!dataset) return null;

  const equipmentData = dataset.equipment_data || [];

  const barChartData = {
    labels: equipmentData.map(e => e.name),
    datasets: [
      {
        label: 'Flowrate',
        data: equipmentData.map(e => e.flowrate),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
      },
      {
        label: 'Pressure',
        data: equipmentData.map(e => e.pressure),
        backgroundColor: 'rgba(255, 99, 132, 0.6)',
      },
      {
        label: 'Temperature',
        data: equipmentData.map(e => e.temperature),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
      },
    ],
  };

  const equipmentTypes = equipmentData.reduce((acc, curr) => {
    acc[curr.equipment_type] = (acc[curr.equipment_type] || 0) + 1;
    return acc;
  }, {});

  const pieChartData = {
    labels: Object.keys(equipmentTypes),
    datasets: [
      {
        data: Object.values(equipmentTypes),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
          'rgba(255, 159, 64, 0.6)',
        ],
      },
    ],
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto p-4">
        <div className="flex justify-between items-center mb-4">
          <button onClick={() => navigate('/')} className="bg-blue-500 text-white px-4 py-2 rounded-md">Go Back to Home</button>
          <button onClick={handleDownload} className="bg-green-500 text-white px-4 py-2 rounded-md">Download PDF Report</button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">Dataset Summary</h2>
          <p><strong>Total Equipment:</strong> {equipmentData.length}</p>
          {/* Add more summary details as needed */}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold mb-4">Parameter Comparison</h3>
            <Bar data={barChartData} />
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold mb-4">Equipment Type Distribution</h3>
            <Pie data={pieChartData} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mt-8">
          <h3 className="text-xl font-bold mb-4">Data Insights</h3>
          <p>This is a placeholder for auto-generated data insights. Based on the visualized data, we can observe trends and distributions of chemical equipment parameters. For example, the bar chart highlights the differences in flowrate, pressure, and temperature across various equipment, while the pie chart illustrates the proportion of each equipment type within the dataset.</p>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;