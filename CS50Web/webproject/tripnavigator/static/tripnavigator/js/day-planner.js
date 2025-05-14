document.addEventListener("DOMContentLoaded", function() {
  "use strict";
  
  // Helper function: Get the value of a cookie by name.
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie("csrftoken");
  
  // Add dragstart listeners to all activity items for drag-and-drop.
  function addDragStartListenerToActivityItems() {
    document.querySelectorAll(".activity-item").forEach(item => {
      item.addEventListener("dragstart", function(e) {
        e.dataTransfer.setData("text/plain", item.getAttribute("data-activity-id"));
        e.dataTransfer.effectAllowed = "move";
      });
    });
  }
  addDragStartListenerToActivityItems();
  
  // Add click listeners to delete buttons for activities.
  function addDeleteListeners() {
    document.querySelectorAll(".delete-activity").forEach(btn => {
      btn.addEventListener("click", function(e) {
        e.stopPropagation(); // Prevent the drag event from triggering.
        const activityElem = btn.parentElement;
        const activityId = activityElem.getAttribute("data-activity-id");
        fetch(window.deleteActivityURL, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrftoken,
          },
          body: new URLSearchParams({ activity_id: activityId }),
        })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              activityElem.parentNode.removeChild(activityElem);
            } else {
              console.error("Failed to delete activity.");
            }
          })
          .catch(error => console.error("Error:", error));
      });
    });
  }
  addDeleteListeners();
  
  // Setup drop zones to handle activity date updates via drag-and-drop.
  document.querySelectorAll(".drop-target").forEach(zone => {
    zone.addEventListener("dragover", function(e) {
      e.preventDefault();
      zone.classList.add("dragover");
    });
    zone.addEventListener("dragleave", function(e) {
      zone.classList.remove("dragover");
    });
    zone.addEventListener("drop", function(e) {
      e.preventDefault();
      zone.classList.remove("dragover");
      const activityId = e.dataTransfer.getData("text/plain");
      const newDate = zone.getAttribute("data-date");
  
      fetch(window.updateActivityDateURL, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": csrftoken,
        },
        body: new URLSearchParams({ activity_id: activityId, date: newDate }),
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Move the activity element to the new day's container.
            const activityElem = document.querySelector(`.activity-item[data-activity-id='${activityId}']`);
            if (activityElem) {
              activityElem.parentNode.removeChild(activityElem);
              const dayContainer = document.getElementById(`day-activities-${newDate}`);
              if (dayContainer) {
                dayContainer.appendChild(activityElem);
              }
            }
          } else {
            alert("Failed to update activity date.");
          }
        })
        .catch(error => console.error("Error:", error));
    });
  });
  
  // Handle submission of the new activity form (inline form).
  document.getElementById("new-activity-form").addEventListener("submit", function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    fetch(form.action || window.location.href, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
        "X-Requested-With": "XMLHttpRequest",
      },
      body: new URLSearchParams(formData),
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          const selectedDate = form.activityDay.value;
          const newActivityId = data.activity_id;
          const newActivityElem = document.createElement("div");
          newActivityElem.classList.add("activity-item");
          newActivityElem.setAttribute("data-activity-id", newActivityId);
          newActivityElem.setAttribute("draggable", "true");
  
          // Build display text including optional start/end times.
          let displayText = form.activityName.value;
          if (form.activityStartTime.value) {
            displayText = `<strong>${form.activityStartTime.value}</strong> – ${displayText}`;
            if (form.activityEndTime.value) {
              displayText += ` (Ends: ${form.activityEndTime.value})`;
            }
          }
          newActivityElem.innerHTML = displayText;
  
          // Add delete button and its event listener.
          const deleteBtn = document.createElement("span");
          deleteBtn.classList.add("delete-activity");
          deleteBtn.innerHTML = "×";
          newActivityElem.appendChild(deleteBtn);
          deleteBtn.addEventListener("click", function(e) {
            e.stopPropagation();
            fetch(window.deleteActivityURL, {
              method: "POST",
              headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrftoken,
              },
              body: new URLSearchParams({ activity_id: newActivityId }),
            })
              .then(response => response.json())
              .then(data => {
                if (data.success) {
                  newActivityElem.parentNode.removeChild(newActivityElem);
                } else {
                  alert("Failed to delete activity.");
                }
              })
              .catch(error => console.error("Error:", error));
          });
  
          // Set up dragstart for the new activity.
          newActivityElem.addEventListener("dragstart", function(e) {
            e.dataTransfer.setData("text/plain", newActivityElem.getAttribute("data-activity-id"));
            e.dataTransfer.effectAllowed = "move";
          });
  
          // Append the new activity to the correct container.
          if (selectedDate) {
            const dayContainer = document.getElementById(`day-activities-${selectedDate}`);
            if (dayContainer) {
              dayContainer.appendChild(newActivityElem);
            }
          } else {
            const unassignedContainer = document.querySelector(".unassigned-activities");
            if (unassignedContainer) {
              unassignedContainer.appendChild(newActivityElem);
            }
          }
          form.reset();
        } else {
          alert("Failed to create activity.");
        }
      })
      .catch(error => console.error("Error:", error));
  });
  
  // Handle new activity creation via a modal form.
  document.getElementById("modal-new-activity-form").addEventListener("submit", function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    fetch(window.dayPlannerURL, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
        "X-Requested-With": "XMLHttpRequest",
      },
      body: new URLSearchParams(formData),
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Get the selected day from the form.
          const selectedDate = form.activityDay.value;
          const newActivityId = data.activity_id;
          const newActivityElem = document.createElement("div");
          newActivityElem.classList.add("activity-item");
          newActivityElem.setAttribute("data-activity-id", newActivityId);
          newActivityElem.setAttribute("draggable", "true");
          let displayText = form.activityName.value;
          if (form.activityStartTime.value) {
            displayText = `<strong>${form.activityStartTime.value}</strong> – ${displayText}`;
            if (form.activityEndTime.value) {
              displayText += ` (Ends: ${form.activityEndTime.value})`;
            }
          }
          newActivityElem.innerHTML = displayText;
  
          // Create and attach a delete button with its event listener.
          const deleteBtn = document.createElement("span");
          deleteBtn.classList.add("delete-activity");
          deleteBtn.innerHTML = "×";
          newActivityElem.appendChild(deleteBtn);
          deleteBtn.addEventListener("click", function(e) {
            e.stopPropagation();
            fetch(window.deleteActivityURL, {
              method: "POST",
              headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrftoken,
              },
              body: new URLSearchParams({ activity_id: newActivityId }),
            })
              .then(response => response.json())
              .then(data => {
                if (data.success) {
                  newActivityElem.parentNode.removeChild(newActivityElem);
                } else {
                  alert("Failed to delete activity.");
                }
              })
              .catch(error => console.error("Error:", error));
          });
  
          newActivityElem.addEventListener("dragstart", function(e) {
            e.dataTransfer.setData("text/plain", newActivityElem.getAttribute("data-activity-id"));
            e.dataTransfer.effectAllowed = "move";
          });
  
          // Append the new activity to the modal's day container or unassigned list.
          if (selectedDate === document.getElementById("selected-day-content").getAttribute("data-date")) {
            document.getElementById("activities-list").appendChild(newActivityElem);
          } else {
            document.getElementById("unassigned-list").appendChild(newActivityElem);
          }
          form.reset();
          document.getElementById("new-activity-modal").style.display = "none";
        } else {
          alert("Failed to create activity.");
        }
      })
      .catch(error => console.error("Error:", error));
  });
});
