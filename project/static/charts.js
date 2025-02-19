// static/charts.js

// Wait until the DOM is fully loaded before executing the code
document.addEventListener("DOMContentLoaded", () => {
  // ========= CALORIES PAGE =========
  // Retrieve the calorie data from the global window object
  const calData = window.calorieData;

  // Proceed only if calorie data exists
  if (calData) {
    // Check if the elements for the charts exist in the DOM
    const calChartEl = document.getElementById('calorieChart');
    const goalChartEl = document.getElementById('goalChart');

    if (calChartEl && goalChartEl) {
      // Create two charts: one for calorie intake and one for calorie goals

      // --- Bar Chart for Calories ---
      // Get the 2D drawing context from the calorie chart element
      const calorieCtx = calChartEl.getContext('2d');
      // Create a new bar chart using the Chart.js library
      new Chart(calorieCtx, {
        type: 'bar', // Set the chart type to bar
        data: {
          // Use the days from the calorie data as the labels on the x-axis
          labels: calData.days,
          datasets: [{
            label: 'Calories (kcal)', // Label for the dataset
            data: calData.calories,     // Calorie values for each day
            backgroundColor: '#007bff'  // Bar color
          }]
        }
      });

      // --- Line Chart for Calorie Goals ---
      // Get the 2D drawing context from the goal chart element
      const goalCtx = goalChartEl.getContext('2d');
      // Create a new line chart using the Chart.js library
      new Chart(goalCtx, {
        type: 'line', // Set the chart type to line
        data: {
          // Use the same days for the x-axis labels
          labels: calData.days,
          datasets: [
            {
              label: 'Actual Intake',    // Label for the actual calorie intake dataset
              data: calData.calories,      // Calorie intake values
              borderColor: '#007bff',      // Line color for actual intake
              backgroundColor: 'rgba(0, 123, 255, 0.2)', // Fill color under the line
              fill: true,                  // Fill the area under the line
              tension: 0.3                 // Curve tension for smoothness
            },
            {
              label: 'Calorie Goal',       // Label for the calorie goal dataset
              // For each day, map the calorie goal value (same goal for each day)
              data: calData.days.map(() => calData.calorieGoal),
              borderColor: '#ff6384',       // Line color for calorie goal
              borderDash: [5, 5],           // Dashed line style
              tension: 0.3                 // Curve tension for smoothness
            }
          ]
        }
      });
    }
  }
});


   // ========== CHECKIN PAGE ==========
// This block handles the Checkin Page functionality.
// It displays recent checkin entries as cards and creates a bar chart for energy and sleep.

document.addEventListener("DOMContentLoaded", () => {
  // Retrieve checkin data from the global window object
  const chData = window.checkinData;
  if (chData) {
    // Check if the elements for the energy/sleep chart and checkin cards exist on the page
    const chartEl = document.getElementById('energySleepChart');
    const cardsEl = document.getElementById('checkin-cards');
    if (chartEl && cardsEl) {
      // Extract the most recent 6 checkin entries and reverse their order so that the oldest appears first
      let recentData = chData.slice(-6).reverse();

      // Render the checkin cards by clearing any existing content and adding new card HTML for each entry
      cardsEl.innerHTML = "";
      recentData.forEach(entry => {
        const cardHTML = `
          <div class="col-md-4">
            <div class="card p-3 mb-3 shadow-sm">
              <h5>${entry.created_at}</h5>
              <p><strong>Weight:</strong> ${entry.weight} kg</p>
              <p><strong>Energy:</strong> ${entry.energy}/10</p>
              <p><strong>Sleep:</strong> ${entry.sleep} hours</p>
            </div>
          </div>`;
        cardsEl.innerHTML += cardHTML;
      });

      // Prepare data for the chart by mapping dates, energy levels, and sleep hours from the recent checkin data
      const dates = recentData.map(d => d.created_at);
      const energyLevels = recentData.map(d => d.energy);
      const sleepHours = recentData.map(d => d.sleep);

      // Create a bar chart using Chart.js to display Energy Level and Sleep (in hours)
      new Chart(chartEl.getContext('2d'), {
        type: 'bar',
        data: {
          labels: dates, // X-axis labels (dates of checkins)
          datasets: [
            {
              label: 'Energy Level',       // Dataset for energy levels
              data: energyLevels,           // Energy values for each date
              backgroundColor: '#ffca28'     // Bar color for energy levels
            },
            {
              label: 'Sleep (hrs)',         // Dataset for sleep hours
              data: sleepHours,             // Sleep hours for each date
              backgroundColor: '#007bff'     // Bar color for sleep
            }
          ]
        }
      });
    }
  }
});


// ========== DASHBOARD PAGE ==========
// This block handles the Dashboard Page functionality.
// It creates a line chart for weight tracking and a combined bar/line chart for calories vs. calorie goal.

document.addEventListener("DOMContentLoaded", () => {
  // Retrieve dashboard data from the global window object
  const dbData = window.dashboardData;
  if (dbData) {
    // Check if the elements for the weight and calorie charts exist on the page
    const weightChartEl = document.getElementById('weightChart');
    const calorieChartEl = document.getElementById('calorieChart');

    // If the weight chart element is available, create a line chart for weight data
    if (weightChartEl) {
      new Chart(weightChartEl.getContext('2d'), {
        type: 'line',
        data: {
          labels: dbData.weightLabels, // X-axis labels for the weight chart (e.g., dates)
          datasets: [
            {
              label: 'Weight (kg)',             // Dataset label for weight
              data: dbData.weightValues,          // Weight values for each label
              borderColor: '#007bff',             // Color of the line
              backgroundColor: 'rgba(0, 123, 255, 0.2)', // Fill color under the line
              fill: true,                         // Enable fill under the line
              tension: 0.3                        // Curve tension for smooth lines
            }
          ]
        },
        options: {
          scales: {
            y: { beginAtZero: false }  // Y-axis will not necessarily start at zero (better for weight data)
          }
        }
      });
    }

    // If the calorie chart element is available, create a combined chart for calories
    if (calorieChartEl) {
      new Chart(calorieChartEl.getContext('2d'), {
        type: 'bar', // Base chart type is bar
        data: {
          labels: dbData.calorieDays, // X-axis labels for the calorie chart (e.g., days)
          datasets: [
            {
              label: 'Calories (kcal)',       // Dataset for actual calorie intake
              data: dbData.calorieValues,       // Calorie values for each day
              backgroundColor: '#007bff'        // Bar color for calorie intake
            },
            {
              label: 'Calorie Goal',           // Dataset for the daily calorie goal
              data: dbData.calorieDays.map(() => dbData.calorieGoal), // Map the same calorie goal for each day
              borderColor: '#ff6384',           // Line color for the calorie goal
              borderDash: [5, 5],               // Dashed line pattern for the calorie goal line
              type: 'line',                    // Render this dataset as a line
              fill: false,                     // Do not fill the area under the goal line
              tension: 0.3                     // Curve tension for smooth line appearance
            }
          ]
        },
        options: {
          scales: {
            y: { beginAtZero: true }  // Y-axis starts at zero for calorie values
          }
        }
      });
    }
  }
});


// ========== TRAINING PAGE ==========
// Wait until the DOM is fully loaded before executing the training page code
document.addEventListener("DOMContentLoaded", () => {
  // Check if training data is available on the global window object
  const trainData = window.trainingData;
  if (trainData) {
    // Get the chart element for training frequency from the DOM
    const freqChartEl = document.getElementById('trainingFrequencyChart');

    if (freqChartEl) {
      // ===== Training Frequency Chart =====
      const freqData = trainData.freqData;
      const freqLabels = freqData.map(d => d.week_range);
      const freqSessions = freqData.map(d => d.sessions);

      // Create a bar chart for training frequency using Chart.js
      new Chart(freqChartEl.getContext('2d'), {
        type: 'bar',
        data: {
          labels: freqLabels,
          datasets: [{
            label: 'Training Sessions',
            data: freqSessions,
            backgroundColor: '#007bff'
          }]
        }
      });
    }
  }
});



   // ========== WEIGHT PAGE ==========
// Wait until the DOM content is fully loaded before executing the code
document.addEventListener("DOMContentLoaded", () => {
  // Check if weight data is available on the global window object
  const wData = window.weightData;
  if (wData) {
    // Get the canvas element where the weight chart will be rendered
    const weightChartEl = document.getElementById('weightChart');
    if (weightChartEl) {
      // Retrieve graph data or use an empty array if not available
      const graphData = wData.graphData || [];
      // Extract dates from the graph data for the x-axis labels
      const dates = graphData.map(d => d.created_at);
      // Extract weight values from the graph data for the y-axis data points
      const weights = graphData.map(d => d.weight);

      // Create a line chart using Chart.js to display weight over time
      new Chart(weightChartEl.getContext('2d'), {
        type: 'line',
        data: {
          labels: dates, // X-axis labels (dates)
          datasets: [{
            label: 'Weight (kg)',  // Label for the dataset
            data: weights,         // Weight values for each date
            borderColor: '#007bff', // Color of the line
            backgroundColor: 'rgba(0, 123, 255, 0.2)', // Fill color under the line
            fill: true,            // Enable filling under the line
            tension: 0.3           // Smoothness of the line curve
          }]
        },
        options: {
          responsive: true,            // Make the chart responsive
          maintainAspectRatio: false,  // Allow the chart to adjust its aspect ratio
          scales: {
            y: { beginAtZero: false }  // Y-axis will not force start at zero
          }
        }
      });
    }
  }
});

// ========== CALORIETRACKER PAGE ==========
// This section sets up a pie chart for the calorietracker page

// Wait until the DOM content is fully loaded before executing the code
document.addEventListener("DOMContentLoaded", () => {
  let nutritionPieChart; // Variable to hold the Chart.js instance for the nutrition pie chart

  // Initialize the pie chart when the nutrition tab is activated (using Bootstrap tab event)
  document.querySelector('#nutrition-tab').addEventListener('shown.bs.tab', () => {
    // Get the 2D drawing context of the canvas element for the nutrition pie chart
    const ctx = document.getElementById('nutritionPieChart').getContext('2d');

    // Retrieve macronutrient values from the DOM, provided via Jinja templating
    const macroData = {
      proteins: parseFloat(document.getElementById('macro-proteins').textContent) || 0,
      carbohydrates: parseFloat(document.getElementById('macro-carbohydrates').textContent) || 0,
      fats: parseFloat(document.getElementById('macro-fats').textContent) || 0
    };

    // If the nutrition pie chart is not already initialized, create it
    if (!nutritionPieChart) {
      // Prepare the data object for the pie chart
      const data = {
        labels: ['Proteins', 'Carbohydrates', 'Fats'],
        datasets: [{
          data: [macroData.proteins, macroData.carbohydrates, macroData.fats],
          backgroundColor: ['#36A2EB', '#FFCE56', '#FF6384'],
          hoverOffset: 4
        }]
      };

      // Create a new pie chart using Chart.js
      nutritionPieChart = new Chart(ctx, {
        type: 'pie',
        data: data,
        options: {
          responsive: true, // Make the chart responsive
          plugins: {
            legend: {
              position: 'top', // Position the legend at the top
            },
            tooltip: {
              callbacks: {
                // Customize the tooltip label to show the value with one decimal place followed by "g"
                label: function(tooltipItem) {
                  return tooltipItem.label + ': ' + tooltipItem.raw.toFixed(1) + ' g';
                }
              }
            }
          }
        }
      });
    } else {
      // If the chart already exists, update its data with the new macronutrient values
      nutritionPieChart.data.datasets[0].data = [
        macroData.proteins,
        macroData.carbohydrates,
        macroData.fats
      ];
      nutritionPieChart.update(); // Refresh the chart to reflect the new data
    }
  });
});
