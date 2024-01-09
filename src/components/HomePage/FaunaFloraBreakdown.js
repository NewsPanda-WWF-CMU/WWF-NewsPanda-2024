import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import { Bar } from "react-chartjs-2";
import "chart.js/auto";
import csvData from "../../data/test-last-year-nepal-cleaned.csv"; // Path to your CSV file

const colors = [
  "#FF6384",
  "#36A2EB",
  "#FFCE56",
  "#4BC0C0",
  "#9966FF",
  "#FF9F40",
  "#FFCD56",
  "#4D5360",
  "#C9CBCF",
  "#7ACBEE",
  "#4CAF50",
  "#8BC34A",
  "#388E3C",
  "#66BB6A",
  "#2E7D32",
];

const FaunaFloraBreakdown = () => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [],
  });

  useEffect(() => {
    Papa.parse(csvData, {
      download: true,
      header: true,
      complete: (results) => {
        const categoryCounts = results.data.reduce((acc, row) => {
          // Assuming there's a 'Category' column in your CSV
          const categories = row["Flora_and_Fauna"]?.split(",");
          categories?.forEach((category) => {
            category = category.replace(/\(.*?\)/g, "").trim();
            if (category) {
              if (!(category in acc)) {
                acc[category] = 0;
              }
              acc[category]++;
            }
          });
          return acc;
        }, {});

        const labels = Object.keys(categoryCounts);
        const data = Object.values(categoryCounts);
        const backgroundColors = chartData.labels.map(
          (_, index) => colors[index % colors.length]
        );

        setChartData({
          labels: labels,
          datasets: [
            {
              label: "Number of Articles",
              data: data,
              backgroundColor: backgroundColors, // Example background color
            },
          ],
        });
      },
    });
  }, [chartData.labels]);

  const options = {
    indexAxis: "y",
    maintainAspectRatio: false, // Add this to disable maintaining the aspect ratio
    responsive: true, // Make sure this is set to true if you want a responsive chart
    scales: {
      x: {
        beginAtZero: true, // Start the scale at zero
        // You can add more scale options here
      },
      y: {
        // You can adjust the scale for y axis if needed
      },
    },
    plugins: {
      legend: {
        display: false, // Set this to true if you want to display legend
      },
      title: {
        display: true,
        text: "Number of Articles", // Customize chart title
      },
    },
  };

  return (
    <div className="fauna-flora" style={{ height: "500px", width: "100%" }}>
      {" "}
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default FaunaFloraBreakdown;
