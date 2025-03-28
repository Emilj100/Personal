// static/tripnavigator/ai_chat.js

document.addEventListener('DOMContentLoaded', function() {
  const chatForm = document.getElementById('chatForm');
  const userMessageInput = document.getElementById('userMessage');
  const chatContainer = document.getElementById('chatContainer');

  // Globalt array til chat-historik
  let chatHistoryArray = [];

  // Indlæs historik fra sessionStorage
  loadChatHistory();

  // Håndter formular-indsendelse
  chatForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const userMessage = userMessageInput.value.trim();
    if (!userMessage) return;

    // Tilføj brugerens besked og gem den
    appendMessageBubble('user', userMessage, true, false);
    userMessageInput.value = '';

    // Tilføj en ephemeral "thinking" boble (gemmes ikke)
    const thinkingElem = createEphemeralBubble('ai');

    // Send AJAX POST til /ai/get-response/
    $.ajax({
      type: 'POST',
      url: '/ai/get-response/',
      data: {
        message: userMessage,
        csrfmiddlewaretoken: getCSRFToken()
      },
      success: function(response) {
        if (thinkingElem) {
          chatContainer.removeChild(thinkingElem);
        }
        if (response.message) {
          // Gem og parse AI-svaret som HTML (f.eks. overskrifter og linjeskift)
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

  // Opretter en ephemeral "thinking" boble (ikke gemt i historik)
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
   * Tilføjer en permanent beskedboble og gemmer den i historik, hvis gemIHistorik er true.
   * @param {string} role 'user' eller 'ai'
   * @param {string} text Beskedens indhold
   * @param {boolean} gemIHistorik Skal beskeden gemmes i sessionStorage?
   * @param {boolean} isHtml Skal teksten behandles som HTML (fx med overskrifter og linjeskift)?
   */
  function appendMessageBubble(role, text, gemIHistorik=false, isHtml=false) {
    const bubbleContainer = document.createElement('div');
    bubbleContainer.classList.add('bubble-container', role);

    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('avatar');
    avatarDiv.innerHTML = (role === 'user') ? '<i class="bi bi-person-fill"></i>' : '<i class="bi bi-robot"></i>';

    const messageBubble = document.createElement('div');
    messageBubble.classList.add('message-bubble', role);
    if (isHtml) {
      messageBubble.innerHTML = parseAiMessage(text);
    } else {
      messageBubble.textContent = text;
    }

    const timeStamp = document.createElement('div');
    timeStamp.classList.add('timestamp');
    const now = new Date();
    timeStamp.innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

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

    if (gemIHistorik) {
      const msgObj = {
        role: role,
        text: text,
        isHtml: isHtml,
        timestamp: now.toISOString()
      };
      chatHistoryArray.push(msgObj);
      if (chatHistoryArray.length > 10) {
        chatHistoryArray = chatHistoryArray.slice(-10);
      }
      saveChatHistory();
    }
    return bubbleContainer;
  }

  /**
   * Parser AI's besked for at konvertere **tekst** til <h4> og nye linjeskift til <br>
   */
  function parseAiMessage(text) {
    let parsed = text.replace(/\*\*(.*?)\*\*/g, function(match, p1) {
      return '<h4 style="font-size:1rem; margin:0 0 5px;">' + p1 + '</h4>';
    });
    // Erstat newline-tegn med <br>
    parsed = parsed.replace(/\n/g, '<br>');
    return parsed;
  }

  /**
   * Gemmer chat-historik i sessionStorage
   */
  function saveChatHistory() {
    sessionStorage.setItem('chatHistory', JSON.stringify(chatHistoryArray));
  }

  /**
   * Indlæser chat-historik fra sessionStorage og genindlæser beskederne
   */
  function loadChatHistory() {
    const stored = sessionStorage.getItem('chatHistory');
    if (stored) {
      try {
        chatHistoryArray = JSON.parse(stored) || [];
      } catch (e) {
        console.error("Error parsing chat history:", e);
        chatHistoryArray = [];
      }
      // Ryd chatContainer for at undgå dubletter
      chatContainer.innerHTML = '';
      chatHistoryArray.forEach(msg => {
        appendMessageBubble(msg.role, msg.text, false, msg.isHtml);
      });
    }
  }

  // Foruddefinerede spørgsmål
  window.setPredefined = function(text) {
    userMessageInput.value = text;
    userMessageInput.focus();
  };

  // Hent CSRF-token fra cookies
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
