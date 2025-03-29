document.addEventListener("DOMContentLoaded", function () {
  // Get budget data from the HTML element's data attributes
  const budgetData = document.getElementById("budget-data");
  
  const spent = parseFloat(budgetData.dataset.totalSpent);
  const remaining = parseFloat(budgetData.dataset.remaining);
  const categoryLabels = JSON.parse(budgetData.dataset.categoryLabels);
  const categoryValues = JSON.parse(budgetData.dataset.categoryValues);
  
  // Render the budget donut chart using Chart.js
  const donutCtx = document.getElementById("budgetDonutChart").getContext("2d");
  new Chart(donutCtx, {
    type: "doughnut",
    data: {
      labels: ["Spent", "Remaining"],
      datasets: [{
        data: [spent, remaining],
        backgroundColor: ["#28a745", "#e9ecef"],
        hoverBackgroundColor: ["#218838", "#ced4da"]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom" }
      }
    }
  });
  
  // Render the category breakdown bar chart using Chart.js
  const categoryCtx = document.getElementById("categoryBreakdownChart").getContext("2d");
  new Chart(categoryCtx, {
    type: "bar",
    data: {
      labels: categoryLabels,
      datasets: [{
        label: "Expense ($)",
        data: categoryValues,
        backgroundColor: ["#007bff", "#28a745", "#ffc107", "#17a2b8", "#6c757d"],
        borderRadius: 5,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
});
