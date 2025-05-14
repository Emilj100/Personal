// Run code when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function() {
  // Get the widget container element by its ID
  var widgetContainer = document.getElementById("widget-container");
  
  // Create a script element to load the hotel widget
  var widgetScript = document.createElement("script");
  widgetScript.async = true;
  widgetScript.charset = "utf-8";
  
  // Choose widget layout based on screen width (mobile vs. desktop)
  if (window.innerWidth < 768) {
    widgetScript.src = "https://c121.travelpayouts.com/content?trs=397564&shmarker=614135&lang=www&layout=S4279&powered_by=true&promo_id=4038";
  } else {
    widgetScript.src = "https://c121.travelpayouts.com/content?trs=397564&shmarker=614135&lang=www&layout=S10391&powered_by=true&promo_id=4038";
  }
  
  // Append the script element to the widget container to load the widget
  widgetContainer.appendChild(widgetScript);
});
