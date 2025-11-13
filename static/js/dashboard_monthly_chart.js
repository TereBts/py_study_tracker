/* eslint-env browser */
/* global document, window, Chart */

/**
 * Monthly Trend Chart
 * -------------------
 * Renders a responsive Chart.js line chart showing total study hours
 * per goal across the past 12 months. Data and labels are passed in
 * via data attributes on the canvas element.
 */

const monthlyCanvas = document.getElementById("monthlyTrendChart");

if (monthlyCanvas) {
  // Parse labels and dataset JSON embedded via Django template
  const labels = JSON.parse(monthlyCanvas.dataset.labels || "[]");
  const datasets = JSON.parse(monthlyCanvas.dataset.datasets || "[]");

  // Detect small-screen devices for responsive scaling
  const isMobile = window.matchMedia("(max-width: 576px)").matches;

  // Derived sizes (no ternaries for strict linter)
  let legendBoxWidth;
  let legendFontSize;
  let legendPadding;
  let ticksFontSize;
  let xMaxRotation;
  let xMaxTicks;
  let paddingBottom;

  if (isMobile) {
    legendBoxWidth = 10;
    legendFontSize = 8;
    legendPadding = 4;
    ticksFontSize = 8;
    xMaxRotation = 0;
    xMaxTicks = 4;
    paddingBottom = 4;
  } else {
    legendBoxWidth = 14;
    legendFontSize = 10;
    legendPadding = 8;
    ticksFontSize = 10;
    xMaxRotation = 40;
    xMaxTicks = 8;
    paddingBottom = 10;
  }

  // Initialize Chart.js instance
  new Chart(monthlyCanvas, {
    data: { datasets, labels },
    options: {
      interaction: {
        intersect: false,
        mode: "index"
      },
      layout: {
        padding: {
          bottom: paddingBottom,
          left: 0,
          right: 4,
          top: 8
        }
      },
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            boxWidth: legendBoxWidth,
            font: { size: legendFontSize },
            padding: legendPadding
          },
          position: "bottom"
        },
        tooltip: {
          enabled: true
        }
      },
      responsive: true,
      scales: {
        x: {
          ticks: {
            font: { size: ticksFontSize },
            maxRotation: xMaxRotation,
            maxTicksLimit: xMaxTicks,
            minRotation: 0
          },
          title: {
            display: !isMobile,
            text: "Month"
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            drawBorder: false
          },
          ticks: {
            font: { size: ticksFontSize },
            stepSize: 1
          },
          title: {
            display: !isMobile,
            text: "Hours"
          }
        }
      }
    },
    type: "line"
  });
}
