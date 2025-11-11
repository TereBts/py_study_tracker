const monthlyCanvas = document.getElementById("monthlyTrendChart");

if (monthlyCanvas) {
  const labels = JSON.parse(monthlyCanvas.dataset.labels || "[]");
  const datasets = JSON.parse(monthlyCanvas.dataset.datasets || "[]");
  const isMobile = window.matchMedia("(max-width: 576px)").matches;

  new Chart(monthlyCanvas, {
    type: "line",
    data: {
      labels,
      datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false, // use CSS height
      interaction: {
        mode: "index",
        intersect: false,
      },
      layout: {
        padding: {
          top: 8,
          right: 4,
          bottom: isMobile ? 4 : 10,
          left: 0,
        },
      },
      plugins: {
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
        tooltip: {
          enabled: true,
        },
      },
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
            minRotation: isMobile ? 0 : 0,
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
            drawBorder: false,
          },
        },
      },
    },
  });
}
