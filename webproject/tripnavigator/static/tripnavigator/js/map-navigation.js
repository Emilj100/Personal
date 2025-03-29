// Global map variable and hotel marker variable.
var map;
var hotelMarker;

// Define a custom red icon for the hotel marker.
var redIcon = new L.Icon({
  iconUrl: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
});

// Initialize the map navigation with a destination and activity markers.
function initMapNavigation(context) {
  const destination = context.destination;
  const opencage_api_key = context.opencage_api_key;
  const activities = context.activities;
  
  console.log("Initializing map with destination:", destination);

  if (destination) {
    // Geocode the destination using the OpenCage API.
    fetch('https://api.opencagedata.com/geocode/v1/json?q=' + encodeURIComponent(destination) + '&key=' + opencage_api_key + '&limit=1')
      .then(response => response.json())
      .then(data => {
        console.log("Geocoding result for destination:", data);
        if (data && data.results && data.results.length > 0) {
          const lat = data.results[0].geometry.lat;
          const lon = data.results[0].geometry.lng;
          // Set map view based on geocoded coordinates.
          map = L.map('map').setView([lat, lon], 12);
        } else {
          console.warn("No geocoding result; using fallback center.");
          map = L.map('map').setView([55.6761, 12.5683], 12);
        }
        // Add OpenStreetMap tile layer.
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        // Allow the map to adjust its size.
        setTimeout(() => { map.invalidateSize(); }, 100);
        // Add markers for each activity.
        addActivityMarkers(activities, opencage_api_key);

        // If a hotel address is provided, add the hotel marker.
        if (context.hotel_address && context.hotel_address.trim() !== "" && context.hotel_address.toLowerCase() !== "none") {
          addHotelMarker(context.hotel_address, opencage_api_key);
        }
      })
      .catch(err => {
        console.error("Error geocoding destination:", err);
        // Use fallback coordinates in case of an error.
        map = L.map('map').setView([55.6761, 12.5683], 12);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        setTimeout(() => { map.invalidateSize(); }, 100);
        addActivityMarkers(activities, opencage_api_key);
      });
  } else {
    // If no destination is provided, use fallback coordinates.
    map = L.map('map').setView([55.6761, 12.5683], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    setTimeout(() => { map.invalidateSize(); }, 100);
    addActivityMarkers(activities, opencage_api_key);
  }
}

// Add markers on the map for each activity based on its address.
function addActivityMarkers(activities, opencage_api_key) {
  var markerRefs = {};
  activities.forEach(function(activity) {
    if (activity.address &&
        activity.address.trim() !== "" &&
        activity.address.toLowerCase() !== "none") {
      // Geocode the activity address.
      fetch('https://api.opencagedata.com/geocode/v1/json?q=' + encodeURIComponent(activity.address) + '&key=' + opencage_api_key + '&limit=1')
        .then(response => response.json())
        .then(data => {
          if (data && data.results && data.results.length > 0) {
            var lat = data.results[0].geometry.lat;
            var lon = data.results[0].geometry.lng;
            // Create and add a marker with a popup showing the activity title.
            var marker = L.marker([lat, lon]).addTo(map)
              .bindPopup(activity.title);
            markerRefs[activity.id] = marker;
          }
        })
        .catch(error => console.error('Error with geocoding activity:', error));
    }
  });

  // Global function to focus on a marker when an activity is clicked.
  window.focusOnMarker = function(markerId) {
    var marker = markerRefs[markerId];
    if (marker) {
      map.setView(marker.getLatLng(), 15);
      marker.openPopup();
      document.getElementById("infoTitle").textContent = marker.getPopup().getContent();
      document.getElementById("infoDetails").textContent = "";
      document.getElementById("infoBox").style.display = "block";
    }
  }
}

// Add a hotel marker on the map using the provided hotel address.
function addHotelMarker(address, opencage_api_key) {
  fetch('https://api.opencagedata.com/geocode/v1/json?q=' + encodeURIComponent(address) + '&key=' + opencage_api_key + '&limit=1')
    .then(response => response.json())
    .then(data => {
      if (data && data.results && data.results.length > 0) {
        var lat = data.results[0].geometry.lat;
        var lon = data.results[0].geometry.lng;
        if (hotelMarker) {
          map.removeLayer(hotelMarker);
        }
        // Create a hotel marker with the custom red icon.
        hotelMarker = L.marker([lat, lon], {icon: redIcon}).addTo(map)
          .bindPopup("Hotel: " + address);
      } else {
        console.warn("No geocoding result for the hotel address.");
      }
    })
    .catch(error => console.error('Error geocoding hotel address:', error));
}

// Helper function to get a cookie value by its name.
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
}

// Update the hotel address: add a hotel marker and send the new address to the server.
function updateHotelAddress() {
  var newAddress = document.getElementById("hotelAddressInput").value;
  if (newAddress && newAddress.trim() !== "" && newAddress.toLowerCase() !== "none") {
    addHotelMarker(newAddress, window.mapNavigationContext.opencage_api_key);

    fetch('/travel_plan/' + window.mapNavigationContext.travel_plan_id + '/update-hotel-address/', {
      method: 'POST',
      headers: {
         'Content-Type': 'application/json',
         'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ hotel_address: newAddress })
    })
    .then(response => response.json().then(data => ({ status: response.status, body: data })))
    .then(result => {
      if (result.status === 200) {
        showMessage("Hotel address has been updated.", "success");
      } else {
        console.error("Error updating hotel address:", result.body);
        showMessage("Error updating hotel address: " + result.body.error, "danger");
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showMessage("Error updating hotel address.", "danger");
    });
  }
}

// Hide the InfoBox overlay.
function closeInfoBox() {
  document.getElementById("infoBox").style.display = "none";
}

// Display a temporary message to the user.
function showMessage(message, type) {
  var msgDiv = document.getElementById('messages');
  msgDiv.innerHTML = `<div class="alert alert-${type}" role="alert">${message}</div>`;
  setTimeout(function() {
    msgDiv.innerHTML = '';
  }, 3000);
}
