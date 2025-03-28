var map;

function initOverview(context) {
  const destination = context.destination;
  const opencage_api_key = context.opencage_api_key;
  const activities = context.activities;
  
  console.log("Initializing overview map with destination:", destination);

  if (destination) {
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
    map = L.map('map').setView([55.6761, 12.5683], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    setTimeout(() => { map.invalidateSize(); }, 100);
    addActivityMarkers(activities, opencage_api_key);
  }
}

function addActivityMarkers(activities, opencage_api_key) {
  var markerRefs = {};
  activities.forEach(function(activity) {
    if (activity.address) {
      fetch('https://api.opencagedata.com/geocode/v1/json?q=' + encodeURIComponent(activity.address) + '&key=' + opencage_api_key + '&limit=1')
        .then(response => response.json())
        .then(data => {
          if (data && data.results && data.results.length > 0) {
            var lat = data.results[0].geometry.lat;
            var lon = data.results[0].geometry.lng;
            var marker = L.marker([lat, lon]).addTo(map)
              .bindPopup(activity.title);
            markerRefs[activity.id] = marker;
          }
        })
        .catch(error => console.error('Error with geocoding activity:', error));
    }
  });
  
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

function closeInfoBox() {
  document.getElementById("infoBox").style.display = "none";
}
