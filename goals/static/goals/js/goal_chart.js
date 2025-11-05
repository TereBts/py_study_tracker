// static/goals/js/goal_chart.js

window.addEventListener("DOMContentLoaded", function () {
  const labels = JSON.parse(document.getElementById("chartData").dataset.labels);
  const hoursCompleted = JSON.parse(document.getElementById("chartData").dataset.hoursCompleted);
  const hoursTarget = JSON.parse(document.getElementById("chartData").dataset.hoursTarget);
  const lessonsCompleted = JSON.parse(document.getElementById("chartData").dataset.lessonsCompleted);
  const lessonsTarget = JSON.parse(document.getElementById("chartData").dataset.lessonsTarget);

  const ctx = document.getElementById("goalTrendChart").getContext("2d");

  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Hours completed",
          data: hoursCompleted,
          borderWidth: 2,
          tension: 0.35,
          spanGaps: true,
          pointRadius: 2,
        },
        {
          label: "Hours target",
          data: hoursTarget,
          borderWidth: 2,
          borderDash: [6, 6],
          tension: 0.35,
          spanGaps: true,
          pointRadius: 0,
        },
        {
          label: "Lessons completed",
          data: lessonsCompleted,
          borderWidth: 2,
          tension: 0.35,
          spanGaps: true,
          pointRadius: 2,
          yAxisID: "y2",
        },
        {
          label: "Lessons target",
          data: lessonsTarget,
          borderWidth: 2,
          borderDash: [6, 6],
          tension: 0.35,
          spanGaps: true,
          pointRadius: 0,
          yAxisID: "y2",
        },
      ].filter((ds) => ds.data && ds.data.some((v) => v !== null)),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          title: { display: true, text: "Hours" },
          beginAtZero: true,
        },
        y2: {
          title: { display: true, text: "Lessons" },
          beginAtZero: true,
          position: "right",
          grid: { drawOnChartArea: false },
          ticks: { precision: 0 },
        },
        x: {
          ticks: { autoSkip: true, maxRotation: 0 },
        },
      },
      plugins: {
        legend: { display: true },
        tooltip: { mode: "index", intersect: false },
      },
      elements: { point: { hitRadius: 8 } },
    },
  });

  document.getElementById("goalTrendChart").parentElement.style.minHeight = "320px";
});
