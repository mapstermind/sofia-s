/**
 * SOFIA-S chart helpers
 * Initialise Chart.js charts from server-rendered JSON data.
 */

function initResponsesChart(canvasId, data) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  if (!data || !Array.isArray(data.labels) || data.labels.length === 0) return;

  new Chart(canvas, {
    type: "bar",
    data: data,
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.parsed.y} response${ctx.parsed.y === 1 ? "" : "s"}`,
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { precision: 0 },
        },
      },
    },
  });
}
