// Wait for the DOM to be fully loaded before running the script
document.addEventListener('DOMContentLoaded', function() {
  // Get references to DOM elements: chat form, user message input, and chat container
  const chatForm = document.getElementById('chatForm');
  const userMessageInput = document.getElementById('userMessage');
  const chatContainer = document.getElementById('chatContainer');

  // Initialize an array to store the chat history
  let chatHistoryArray = [];

  // Load any saved chat history from sessionStorage
  loadChatHistory();

  // Listen for the chat form submission
  chatForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const userMessage = userMessageInput.value.trim();
    // If the input is empty, do nothing
    if (!userMessage) return;

    // Append the user's message bubble to the chat and clear the input field
    appendMessageBubble('user', userMessage, true, false);
    userMessageInput.value = '';

    // Create an ephemeral AI bubble (e.g., "AI is thinking...")
    const thinkingElem = createEphemeralBubble('ai');

    // Send the user's message to the AI via AJAX POST request
    $.ajax({
      type: 'POST',
      url: '/ai/get-response/',
      data: {
        message: userMessage,
        csrfmiddlewaretoken: getCSRFToken()
      },
      success: function(response) {
        // Remove the ephemeral "thinking" bubble
        if (thinkingElem) {
          chatContainer.removeChild(thinkingElem);
        }
        // Append the AI's response; handle errors if provided
        if (response.message) {
          appendMessageBubble('ai', response.message, true, true);
        } else if (response.error) {
          appendMessageBubble('ai', "Error: " + response.error, true, false);
        }
      },
      error: function(xhr, status, error) {
        if (thinkingElem) {
          chatContainer.removeChild(thinkingElem);
        }
        console.error("AJAX error:", xhr.responseText);
        appendMessageBubble('ai', "Error: " + error, true, false);
      }
    });
  });

  // Function to create an ephemeral bubble (e.g., "AI is thinking...")
  function createEphemeralBubble(role) {
    const bubbleContainer = document.createElement('div');
    bubbleContainer.classList.add('bubble-container', role);

    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('avatar');
    avatarDiv.innerHTML = (role === 'user') ? '<i class="bi bi-person-fill"></i>' : '<i class="bi bi-robot"></i>';

    const messageBubble = document.createElement('div');
    messageBubble.classList.add('message-bubble', role);
    messageBubble.innerHTML = "AI is thinking<span class='dots'><span class='dot'>.</span><span class='dot'>.</span><span class='dot'>.</span></span>";

    const timeStamp = document.createElement('div');
    timeStamp.classList.add('timestamp');
    const now = new Date();
    timeStamp.innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // For user, timestamp is added before the avatar; for AI, after the message bubble
    if (role === 'user') {
      bubbleContainer.appendChild(timeStamp);
      bubbleContainer.appendChild(avatarDiv);
      bubbleContainer.appendChild(messageBubble);
    } else {
      bubbleContainer.appendChild(avatarDiv);
      bubbleContainer.appendChild(messageBubble);
      bubbleContainer.appendChild(timeStamp);
    }

    chatContainer.appendChild(bubbleContainer);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return bubbleContainer;
  }

  /**
   * Append a message bubble to the chat.
   *
   * @param {string} role - 'user' or 'ai'
   * @param {string} text - Message content
   * @param {boolean} gemIHistorik - Whether to save the message in chat history
   * @param {boolean} isHtml - Whether the text contains HTML to parse
   */
  function appendMessageBubble(role, text, gemIHistorik=false, isHtml=false) {
    const bubbleContainer = document.createElement('div');
    bubbleContainer.classList.add('bubble-container', role);

    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('avatar');
    avatarDiv.innerHTML = (role === 'user') ? '<i class="bi bi-person-fill"></i>' : '<i class="bi bi-robot"></i>';

    const messageBubble = document.createElement('div');
    messageBubble.classList.add('message-bubble', role);
    // If isHtml is true, parse the message as HTML; otherwise set as text
    if (isHtml) {
      messageBubble.innerHTML = parseAiMessage(text);
    } else {
      messageBubble.textContent = text;
    }

    const timeStamp = document.createElement('div');
    timeStamp.classList.add('timestamp');
    const now = new Date();
    timeStamp.innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Order the elements differently for user and AI messages
    if (role === 'user') {
      bubbleContainer.appendChild(timeStamp);
      bubbleContainer.appendChild(avatarDiv);
      bubbleContainer.appendChild(messageBubble);
    } else {
      bubbleContainer.appendChild(avatarDiv);
      bubbleContainer.appendChild(messageBubble);
      bubbleContainer.appendChild(timeStamp);
    }

    chatContainer.appendChild(bubbleContainer);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Save the message in history if requested
    if (gemIHistorik) {
      const msgObj = {
        role: role,
        text: text,
        isHtml: isHtml,
        timestamp: now.toISOString()
      };
      chatHistoryArray.push(msgObj);
      // Keep only the latest 10 messages in history
      if (chatHistoryArray.length > 10) {
        chatHistoryArray = chatHistoryArray.slice(-10);
      }
      saveChatHistory();
    }
    return bubbleContainer;
  }

  // Replace markdown-style **text** with HTML heading elements for AI messages
  function parseAiMessage(text) {
    let parsed = text.replace(/\*\*(.*?)\*\*/g, function(match, p1) {
      return '<h4 style="font-size:1rem; margin:0 0 5px;">' + p1 + '</h4>';
    });
    parsed = parsed.replace(/\n/g, '<br>');
    return parsed;
  }

  // Save chat history in sessionStorage
  function saveChatHistory() {
    sessionStorage.setItem('chatHistory', JSON.stringify(chatHistoryArray));
  }

  // Load saved chat history from sessionStorage and render it
  function loadChatHistory() {
    const stored = sessionStorage.getItem('chatHistory');
    if (stored) {
      try {
        chatHistoryArray = JSON.parse(stored) || [];
      } catch (e) {
        console.error("Error parsing chat history:", e);
        chatHistoryArray = [];
      }
      chatContainer.innerHTML = '';
      chatHistoryArray.forEach(msg => {
        appendMessageBubble(msg.role, msg.text, false, msg.isHtml);
      });
    }
  }

  // Set predefined text into the user message input and focus it
  window.setPredefined = function(text) {
    userMessageInput.value = text;
    userMessageInput.focus();
  };

  // Function to retrieve the CSRF token from cookies
  function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, 10) === 'csrftoken=') {
          cookieValue = decodeURIComponent(cookie.substring(10));
          break;
        }
      }
    }
    return cookieValue;
  }
});
