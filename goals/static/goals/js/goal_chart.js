/**
 * Goal Trend Chart
 * ----------------
 * Renders a dual-axis line chart (hours and lessons) showing progress
 * over recent weeks for a specific goal. Data is passed in from Django
 * templates via <script type="application/json"> tags for safety.
 *
 * Features:
 *  - Two datasets per metric (completed vs. target)
 *  - Distinct left/right Y-axes for hours and lessons
 *  - Responsive layout with graceful scaling
 *  - Dotted lines for targets to visually separate them from actuals
 */

window.addEventListener("DOMContentLoaded", function () {
  // Parse JSON data safely from <script type="application/json"> tags.
  const labels = JSON.parse(document.getElementById("chart-labels").textContent);
  const hoursCompleted = JSON.parse(document.getElementById("chart-hours-completed").textContent);
  const hoursTarget = JSON.parse(document.getElementById("chart-hours-target").textContent);
  const lessonsCompleted = JSON.parse(document.getElementById("chart-lessons-completed").textContent);
  const lessonsTarget = JSON.parse(document.getElementById("chart-lessons-target").textContent);

  // Get canvas context (skip rendering if element not found).
  const canvas = document.getElementById("goalTrendChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  /**
   * Instantiate Chart.js line chart.
   * Each dataset corresponds to one metric line (hours or lessons).
   * Target lines use dashed styling for distinction.
   */
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
          yAxisID: "y2", // Map to right-hand Y-axis
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
      // Filter out datasets with no valid data to avoid empty lines
      ].filter(ds => Array.isArray(ds.data) && ds.data.some(v => v !== null)),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,

      // Axis configuration
      scales: {
        y: {
          title: { display: true, text: "Hours" },
          beginAtZero: true,
        },
        y2: {
          title: { display: true, text: "Lessons" },
          beginAtZero: true,
          position: "right",
          grid: { drawOnChartArea: false }, // Prevent overlapping grids
          ticks: { precision: 0 },          // Integer-only labels
        },
        x: {
          ticks: { autoSkip: true, maxRotation: 0 },
        },
      },

      // Plugin behaviour: legend + tooltips
      plugins: {
        legend: { display: true },
        tooltip: { mode: "index", intersect: false },
      },

      // Increase click area for small data points
      elements: { point: { hitRadius: 8 } },
    },
  });

  // Ensure minimum vertical space for the chart container
  canvas.parentElement.style.minHeight = "320px";
});
