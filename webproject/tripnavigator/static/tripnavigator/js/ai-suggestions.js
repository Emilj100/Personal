document.addEventListener("DOMContentLoaded", function() {
  const generateBtn = document.getElementById("generateBtn");
  const suggestionsContainer = document.getElementById("suggestionsContainer");
  const messageArea = document.getElementById("messageArea");

  generateBtn.addEventListener("click", function() {
    suggestionsContainer.innerHTML = '<div class="col-12 text-center"><p>Generating suggestions... Please wait.</p></div>';

    fetch(window.generateSuggestionsUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
      console.log("Received suggestions:", data);
      suggestionsContainer.innerHTML = ''; 
      if (data.suggestions && data.suggestions.length > 0) {
        data.suggestions.forEach(function(suggestion) {
          const cardHTML = `
            <div class="col-md-4 col-lg-3">
              <div class="card h-100" style="border: none; border-radius: 1rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div class="card-body d-flex flex-column">
                  <div class="d-flex align-items-center mb-3">
                    <i class="bi ${suggestion.icon} fs-1 text-${suggestion.color} me-2"></i>
                    <h5 class="card-title mb-0">${suggestion.title}</h5>
                  </div>
                  <p class="card-text flex-grow-1">${suggestion.description}</p>
                  <p class="card-text"><small class="text-muted">${suggestion.extra}</small></p>
                  <button class="btn btn-outline-primary btn-sm mt-2" onclick="addToPlan('${suggestion.title.replace(/'/g, "\\'")}')">Add to Plan</button>
                </div>
              </div>
            </div>
          `;
          suggestionsContainer.innerHTML += cardHTML;
        });
      } else {
        suggestionsContainer.innerHTML = '<div class="col-12 text-center"><p>No suggestions found.</p></div>';
      }
    })
    .catch(error => {
      console.error("Error generating suggestions:", error);
      suggestionsContainer.innerHTML = '<div class="col-12 text-center"><p class="text-danger">Failed to generate suggestions.</p></div>';
    });
  });

  function showMessage(text, type) {
    messageArea.innerHTML = `<div class="alert alert-${type}" role="alert">${text}</div>`;
    setTimeout(() => {
      messageArea.innerHTML = '';
    }, 4000);
  }

  window.addToPlan = function(suggestionTitle) {
    fetch(window.addToPlanUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: new URLSearchParams({
        title: suggestionTitle
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showMessage("Activity added to plan! You can view it in the Day Planner.", "success");
      } else {
        showMessage("Failed to add activity: " + data.error, "danger");
      }
    })
    .catch(error => {
      console.error("Error adding activity:", error);
      showMessage("Error adding activity.", "danger");
    });
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
