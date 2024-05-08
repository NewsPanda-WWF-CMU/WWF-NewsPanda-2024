import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import { Bar } from "react-chartjs-2";
import "chart.js/auto";
import csvData from "../../data/current-nepal-articles.csv"; // Path to your CSV file

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
        let filteredData = results.data
          .filter((row) => {
            const hasPublishedDate =
              row.publishedAt && new Date(row.publishedAt).getTime() > 0;
            const isLandscapeNotNone = row["Landscape-Location"];
            const hasAuthor = row["author"];
            return hasPublishedDate && isLandscapeNotNone && hasAuthor;
          })
          .sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));

        let categoryCounts = filteredData.reduce((acc, row) => {
          const categories = row["Flora_and_Fauna"]?.split(",");
          categories?.forEach((category) => {
            if (category === "nan") {
              return;
            }
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

        // Sort the categories by count in descending order
        let sortedCategories = Object.entries(categoryCounts).sort(
          (a, b) => b[1] - a[1]
        );

        sortedCategories = sortedCategories.filter(
          (category) => category[1] > 1
        );
        // Separate the sorted data back into labels and data arrays
        const labels = sortedCategories.map((item) => item[0]);
        const data = sortedCategories.map((item) => item[1]);

        // Assign a color to each category
        const backgroundColors = labels.map(
          (_, index) => colors[index % colors.length]
        );

        setChartData({
          labels: labels,
          datasets: [
            {
              label: "Number of Articles",
              data: data,
              backgroundColor: backgroundColors, // Assigning colors
            },
          ],
        });
      },
    });
  }, []);

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
