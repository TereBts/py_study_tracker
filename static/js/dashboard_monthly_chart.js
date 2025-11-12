/**
 * Monthly Trend Chart
 * -------------------
 * Renders a responsive Chart.js line chart showing total study hours
 * per goal across the past 12 months. Data and labels are passed in
 * via data attributes on the canvas element.
 *
 * This script:
 *  - Parses JSON labels and datasets from <canvas data-*>
 *  - Detects mobile viewport size for responsive font/layout adjustments
 *  - Configures Chart.js options for a clean, minimal dashboard look
 */

const monthlyCanvas = document.getElementById("monthlyTrendChart");

if (monthlyCanvas) {
  // Parse labels and dataset JSON embedded via Django template
  const labels = JSON.parse(monthlyCanvas.dataset.labels || "[]");
  const datasets = JSON.parse(monthlyCanvas.dataset.datasets || "[]");

  // Detect small-screen devices for responsive scaling
  const isMobile = window.matchMedia("(max-width: 576px)").matches;

  // Initialize Chart.js instance
  new Chart(monthlyCanvas, {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false, // Let CSS control height for flexible layouts

      // Tooltip and hover interaction settings
      interaction: {
        mode: "index",
        intersect: false,
      },

      // Fine-tuned internal padding for both mobile and desktop views
      layout: {
        padding: {
          top: 8,
          right: 4,
          bottom: isMobile ? 4 : 10,
          left: 0,
        },
      },

      plugins: {
        // Legend configuration
        legend: {
          position: "bottom",
          labels: {
            boxWidth: isMobile ? 10 : 14,
            font: {
              size: isMobile ? 8 : 10,
            },
            padding: isMobile ? 4 : 8,
          },
        },

        // Tooltip behaviour
        tooltip: {
          enabled: true,
        },
      },

      // Axis styling and label behaviour
      scales: {
        x: {
          title: {
            display: !isMobile,
            text: "Month",
          },
          ticks: {
            autoSkip: true,
            maxTicksLimit: isMobile ? 4 : 8,
            maxRotation: isMobile ? 0 : 40,
            minRotation: 0,
            font: {
              size: isMobile ? 8 : 10,
            },
          },
        },
        y: {
          beginAtZero: true,
          title: {
            display: !isMobile,
            text: "Hours",
          },
          ticks: {
            stepSize: 1,
            font: {
              size: isMobile ? 8 : 10,
            },
          },
          grid: {
            drawBorder: false, // Softer look without hard axis border
          },
        },
      },
    },
  });
}
