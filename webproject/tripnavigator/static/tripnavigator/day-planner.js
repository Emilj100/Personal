document.addEventListener("DOMContentLoaded", function() {
    "use strict";
    
    // CSRF-token helper
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
  
    // Tilføj dragstart til alle activity-item elementer
    function addDragStartListenerToActivityItems() {
      document.querySelectorAll(".activity-item").forEach(item => {
        item.addEventListener("dragstart", function(e) {
          e.dataTransfer.setData("text/plain", item.getAttribute("data-activity-id"));
          e.dataTransfer.effectAllowed = "move";
        });
      });
    }
    addDragStartListenerToActivityItems();
  
    /* --- Slet aktivitet (Delete button) --- */
    function addDeleteListeners() {
      document.querySelectorAll(".delete-activity").forEach(btn => {
        btn.addEventListener("click", function(e) {
          e.stopPropagation(); // Forhindrer event bubbling
          const activityElem = btn.parentElement;
          const activityId = activityElem.getAttribute("data-activity-id");
          // Slet aktiviteten direkte uden alert
          fetch(window.deleteActivityURL, {
            method: "POST",
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
              "X-CSRFToken": csrftoken,
            },
            body: new URLSearchParams({
              activity_id: activityId,
            }),
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
  
    /* --- Drop på dagens header (drop-target) --- */
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
          body: new URLSearchParams({
            activity_id: activityId,
            date: newDate,
          }),
        })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              const activityElem = document.querySelector(
                `.activity-item[data-activity-id='${activityId}']`
              );
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
  
    /* --- AJAX til "Create New Activity" formular --- */
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
  
            let displayText = form.activityName.value;
            if (form.activityStartTime.value) {
              displayText = `<strong>${form.activityStartTime.value}</strong> – ${displayText}`;
              if (form.activityEndTime.value) {
                displayText += ` (Ends: ${form.activityEndTime.value})`;
              }
            }
            newActivityElem.innerHTML = displayText;
            // Tilføj delete-knap til den nye aktivitet
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
                body: new URLSearchParams({
                  activity_id: newActivityId,
                }),
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
  
    /* --- AJAX for New Activity Modal Form --- */
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
                body: new URLSearchParams({
                  activity_id: newActivityId,
                }),
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
  