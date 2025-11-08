document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("monthlyTrendChart");
  if (!canvas || typeof Chart === "undefined") return;

  let labels = [];
  let datasets = [];

  try {
    labels = JSON.parse(canvas.dataset.labels || "[]");
    datasets = JSON.parse(canvas.dataset.datasets || "[]");
  } catch (err) {
    console.error("Chart data parse error:", err);
    return;
  }

  const ctx = canvas.getContext("2d");

  new Chart(ctx, {
    type: "line",
    data: { labels, datasets },
    options: {
      plugins: {
        legend: { display: true, position: "bottom" },
      },
      interaction: { mode: "nearest", intersect: false },
      scales: {
        y: { beginAtZero: true, title: { display: true, text: "Hours" } },
        x: { title: { display: true, text: "Month" } },
      },
    },
  });
});
