var map;
var hotelMarker;

var redIcon = new L.Icon({
  iconUrl: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
});

function initMapNavigation(context) {
  const destination = context.destination;
  const opencage_api_key = context.opencage_api_key;
  const activities = context.activities;
  
  console.log("Initializing map with destination:", destination);

  if (destination) {
    fetch('https://api.opencagedata.com/geocode/v1/json?q=' + encodeURIComponent(destination) + '&key=' + opencage_api_key + '&limit=1')
      .then(response => response.json())
      .then(data => {
        console.log("Geocoding result for destination:", data);
        if (data && data.results && data.results.length > 0) {
          const lat = data.results[0].geometry.lat;
          const lon = data.results[0].geometry.lng;
          map = L.map('map').setView([lat, lon], 12);
        } else {
          console.warn("No geocoding result; using fallback center.");
          map = L.map('map').setView([55.6761, 12.5683], 12);
        }
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        setTimeout(() => { map.invalidateSize(); }, 100);
        addActivityMarkers(activities, opencage_api_key);

        if (context.hotel_address && context.hotel_address.trim() !== "" && context.hotel_address.toLowerCase() !== "none") {
          addHotelMarker(context.hotel_address, opencage_api_key);
        }
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
    if (activity.address &&
        activity.address.trim() !== "" &&
        activity.address.toLowerCase() !== "none") {
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
        hotelMarker = L.marker([lat, lon], {icon: redIcon}).addTo(map)
          .bindPopup("Hotel: " + address);
      } else {
        console.warn("No geocoding result for the hotel address.");
      }
    })
    .catch(error => console.error('Error geocoding hotel address:', error));
}

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


function closeInfoBox() {
  document.getElementById("infoBox").style.display = "none";
}

function showMessage(message, type) {
  var msgDiv = document.getElementById('messages');
  msgDiv.innerHTML = `<div class="alert alert-${type}" role="alert">${message}</div>`;
  setTimeout(function() {
    msgDiv.innerHTML = '';
  }, 3000);
}
