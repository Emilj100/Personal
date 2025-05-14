var map;

// Initialize the overview map with a given destination and activity markers.
function initOverview(context) {
  const destination = context.destination;
  const opencage_api_key = context.opencage_api_key;
  const activities = context.activities;
  
  console.log("Initializing overview map with destination:", destination);

  if (destination) {
    // Geocode the destination using the OpenCage API.
    fetch('https://api.opencagedata.com/geocode/v1/json?q=' + encodeURIComponent(destination) + '&key=' + opencage_api_key + '&limit=1')
      .then(response => response.json())
      .then(data => {
        console.log("OpenCage geocoding result (destination):", data);
        if (data && data.results && data.results.length > 0) {
          const lat = data.results[0].geometry.lat;
          const lon = data.results[0].geometry.lng;
          map = L.map('map').setView([lat, lon], 12);
        } else {
          console.warn("No geocoding results for destination. Using fallback center.");
          map = L.map('map').setView([55.6761, 12.5683], 12);
        }
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        setTimeout(() => { map.invalidateSize(); }, 100);
        addActivityMarkers(activities, opencage_api_key);
      })
      .catch(err => {
        console.error("Error geocoding destination:", err);
        map = L.map('map').setView([55.6761, 12.5683], 12);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        setTimeout(() => { map.invalidateSize(); }, 100);
        addActivityMarkers(activities, opencage_api_key);
      });
  } else {
    // Use fallback center if no destination is provided.
    map = L.map('map').setView([55.6761, 12.5683], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    setTimeout(() => { map.invalidateSize(); }, 100);
    addActivityMarkers(activities, opencage_api_key);
  }
}

// Add markers for each activity based on their address.
function addActivityMarkers(activities, opencage_api_key) {
  var markerRefs = {};
  activities.forEach(function(activity) {
    if (activity.address) {
      // Geocode the activity's address.
      fetch('https://api.opencagedata.com/geocode/v1/json?q=' + encodeURIComponent(activity.address) + '&key=' + opencage_api_key + '&limit=1')
        .then(response => response.json())
        .then(data => {
          if (data && data.results && data.results.length > 0) {
            var lat = data.results[0].geometry.lat;
            var lon = data.results[0].geometry.lng;
            // Create a marker and bind a popup with the activity title.
            var marker = L.marker([lat, lon]).addTo(map)
              .bindPopup(activity.title);
            markerRefs[activity.id] = marker;
          }
        })
        .catch(error => console.error('Error with geocoding activity:', error));
    }
  });
  
  // Expose a function to focus on a marker by its activity id.
  window.focusOnMarker = function(markerId) {
    var marker = markerRefs[markerId];
    if (marker) {
      map.setView(marker.getLatLng(), 15);
      marker.openPopup();
      // Display the InfoBox with marker details.
      document.getElementById("infoTitle").textContent = marker.getPopup().getContent();
      document.getElementById("infoDetails").textContent = "";
      document.getElementById("infoBox").style.display = "block";
    }
  }
}

// Hide the InfoBox overlay.
function closeInfoBox() {
  document.getElementById("infoBox").style.display = "none";
}
