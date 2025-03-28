document.addEventListener("DOMContentLoaded", function() {
    var widgetContainer = document.getElementById("widget-container");
    var widgetScript = document.createElement("script");
    widgetScript.async = true;
    widgetScript.charset = "utf-8";
    
    if (window.innerWidth < 768) {
      widgetScript.src = "https://c121.travelpayouts.com/content?trs=397564&shmarker=614135&lang=www&layout=S4279&powered_by=true&promo_id=4038";
    } else {
      widgetScript.src = "https://c121.travelpayouts.com/content?trs=397564&shmarker=614135&lang=www&layout=S10391&powered_by=true&promo_id=4038";
    }
    
    widgetContainer.appendChild(widgetScript);
  });