// Wait for the DOM to fully load before running the script
document.addEventListener("DOMContentLoaded", function() {
    // Get references to the form and results container elements
    const form = document.getElementById("experience-form");
    const resultsContainer = document.getElementById("experience-results");
    let loadingInterval;
  
    // Function to display a loading message with animated dots
    function startLoading() {
        let dots = "";
        resultsContainer.innerHTML = "<div class='text-center py-5'><p class='lead'>Loading experiences<span id='loading-dots'></span></p></div>";
        loadingInterval = setInterval(() => {
            dots += ".";
            if (dots.length > 3) {
                dots = "";
            }
            document.getElementById("loading-dots").textContent = dots;
        }, 500);
    }
  
    // Function to stop the loading animation
    function stopLoading() {
        clearInterval(loadingInterval);
    }
  
    // Listen for form submission to trigger the experience search
    form.addEventListener("submit", function(e) {
        e.preventDefault();
        const city = document.getElementById("city").value.trim();
        // If city field is empty, show an error message
        if (!city) {
            resultsContainer.innerHTML = "<p class='text-danger text-center'>Please enter a city.</p>";
            return;
        }
        startLoading();
        const url = `/api/experience_search/?city=${encodeURIComponent(city)}`;
  
        // Fetch experiences data from the API
        fetch(url)
            .then(response => response.json())
            .then(data => {
                stopLoading();
                if (data.error) {
                    resultsContainer.innerHTML = `<p class="text-danger text-center">${data.error}</p>`;
                } else if (data.data && data.data.length > 0) {
                    let html = `<h3 class="mb-4">Experiences in ${city}:</h3>`;
                    data.data.forEach(item => {
                        let photoHTML = "";
                        // Check if photo URL exists; otherwise, use a placeholder
                        if (item.photo_url) {
                            photoHTML = `<img src="${item.photo_url}" class="img-fluid" alt="${item.name}" style="width:100%; height:200px; object-fit:cover;">`;
                        } else {
                            photoHTML = `<div style="width:100%; height:200px; display:flex; align-items:center; justify-content:center; background:#f0f0f0; color:#888;">No image available</div>`;
                        }
                        // Limit description to 200 characters if needed
                        let description = item.details 
                            ? (item.details.length > 200 ? item.details.substring(0,200) + "..." : item.details)
                            : "No description available.";
                        // Create a "Learn More" button if a web URL is provided
                        let learnMore = item.web_url 
                            ? `<a href="${item.web_url}" target="_blank" class="btn btn-dark mt-2">Learn More</a>`
                            : "";
                        // Append the experience card HTML
                        html += `
                            <div class="card mb-4 shadow-sm">
                                <div class="row g-0">
                                    <div class="col-md-4">
                                        ${photoHTML}
                                    </div>
                                    <div class="col-md-8">
                                        <div class="card-body">
                                            <h5 class="card-title">${item.name}</h5>
                                            <p class="card-text">${description}</p>
                                            ${learnMore}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    resultsContainer.innerHTML = html;
                } else {
                    resultsContainer.innerHTML = "<p class='text-center'>No experiences found for this city.</p>";
                }
            })
            // Handle any errors that occur during the fetch
            .catch(error => {
                console.error("Error:", error);
                stopLoading();
                resultsContainer.innerHTML = "<p class='text-danger text-center'>An error occurred. Please try again later.</p>";
            });
    });
  });
  