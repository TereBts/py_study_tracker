/*jslint browser */
/*global Chart */

/**
 * Goal Trend Chart
 * ----------------
 * Renders a dual-axis line chart showing hours + lessons progress
 * using safe JSON extracted via <script type="application/json"> tags.
 */

window.addEventListener("DOMContentLoaded", function () {
  // Parse labels
  const labelEl = document.getElementById("chart-labels");
  const labels = JSON.parse(labelEl.textContent);

  // Parse hours completed
  const hoursCompletedEl =
    document.getElementById("chart-hours-completed");
  const hoursCompleted = JSON.parse(
    hoursCompletedEl.textContent
  );

  // Parse hours target
  const hoursTargetEl =
    document.getElementById("chart-hours-target");
  const hoursTarget = JSON.parse(
    hoursTargetEl.textContent
  );

  // Parse lessons completed
  const lessonsCompletedEl =
    document.getElementById("chart-lessons-completed");
  const lessonsCompleted = JSON.parse(
    lessonsCompletedEl.textContent
  );

  // Parse lessons target
  const lessonsTargetEl =
    document.getElementById("chart-lessons-target");
  const lessonsTarget = JSON.parse(
    lessonsTargetEl.textContent
  );

  // Get canvas (skip rendering if missing)
  const canvas = document.getElementById("goalTrendChart");
  if (!canvas) {
    return;
  }

  const ctx = canvas.getContext("2d");

  // Build datasets and filter out empty ones
  let datasets = [
    {
      borderWidth: 2,
      data: hoursCompleted,
      label: "Hours completed",
      pointRadius: 2,
      spanGaps: true,
      tension: 0.35
    },
    {
      borderDash: [6, 6],
      borderWidth: 2,
      data: hoursTarget,
      label: "Hours target",
      pointRadius: 0,
      spanGaps: true,
      tension: 0.35
    },
    {
      borderWidth: 2,
      data: lessonsCompleted,
      label: "Lessons completed",
      pointRadius: 2,
      spanGaps: true,
      tension: 0.35,
      yAxisID: "y2"
    },
    {
      borderDash: [6, 6],
      borderWidth: 2,
      data: lessonsTarget,
      label: "Lessons target",
      pointRadius: 0,
      spanGaps: true,
      tension: 0.35,
      yAxisID: "y2"
    }
  ];

  datasets = datasets.filter(function (ds) {
    return Array.isArray(ds.data) &&
      ds.data.some(function (v) { return v !== null; });
  });

  // Create Chart.js instance
  new Chart(ctx, {
    data: {
      datasets: datasets,
      labels: labels
    },
    options: {
      elements: {
        point: { hitRadius: 8 }
      },
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true },
        tooltip: {
          intersect: false,
          mode: "index"
        }
      },
      responsive: true,
      scales: {
        x: {
          ticks: {
            autoSkip: true,
            maxRotation: 0
          }
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Hours"
          }
        },
        y2: {
          beginAtZero: true,
          grid: { drawOnChartArea: false },
          position: "right",
          ticks: { precision: 0 },
          title: {
            display: true,
            text: "Lessons"
          }
        }
      }
    },
    type: "line"
  });

  // Ensure minimum height to prevent layout collapse
  canvas.parentElement.style.minHeight = "320px";
});
