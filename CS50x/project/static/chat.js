// chat.js

// Get references to the DOM elements for the chat widget
const chatToggle = document.getElementById('chat-toggle');     // Button to open the chat widget
const chatWidget = document.getElementById('chat-widget');       // Chat widget container
const chatClose = document.getElementById('chat-close');         // Button to close the chat widget
const chatInput = document.getElementById('chat-input');         // Input field for typing chat messages
const chatSend = document.getElementById('chat-send');           // Button to send the chat message
const chatMessages = document.getElementById('chat-messages');     // Container for displaying chat messages

// Global array to store the conversation history
let conversation = [];

// Retrieve CSRF token from the meta tag in the HTML head
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

/**
 * Adds a new chat message to the UI.
 * @param {string} sender - The sender of the message ("You" or "Coach").
 * @param {string} text - The message text.
 */
function addMessage(sender, text) {
    // Create a container div for the message
    const msgContainer = document.createElement('div');
    msgContainer.classList.add('message');

    // Add a specific class based on whether the sender is the user or the coach
    if (sender === 'You') {
        msgContainer.classList.add('user');
    } else {
        msgContainer.classList.add('coach');
    }

    // Create a bubble element to hold the message text
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    bubble.innerHTML = text;

    // Append the bubble to the message container and add it to the chat messages area
    msgContainer.appendChild(bubble);
    chatMessages.appendChild(msgContainer);

    // Automatically scroll the chat to the bottom after adding a new message
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Saves the current conversation history to local storage.
 */
function saveChatHistory() {
    localStorage.setItem("chatHistory", JSON.stringify(conversation));
}

/**
 * Loads the conversation history from local storage and renders it in the UI.
 */
function loadChatHistory() {
    const stored = localStorage.getItem("chatHistory");
    if (stored) {
        conversation = JSON.parse(stored);
        // Render each saved message in the UI
        conversation.forEach(msg => {
            addMessage(msg.sender, msg.text);
        });
    }
}

/**
 * Sends the user's message to the server and handles the response.
 * @param {string} userMessage - The message text from the user.
 */
function sendToServer(userMessage) {
    // Add the user's message to the conversation array and save the history
    conversation.push({ sender: "You", text: userMessage });
    saveChatHistory();

    // Display the user's message in the UI
    addMessage("You", userMessage);
    // Clear the chat input field
    chatInput.value = '';

    // Define a system prompt to set the behavior of the AI assistant (optional)
    const systemPrompt = {
        role: "system",
        content: "You are a friendly and knowledgeable AI Fitness Coach on an English-language health and fitness website."
    };

    // Only send the last 10 messages to keep the payload concise
    const recentConversation = conversation.slice(-10);

    // Convert conversation messages to the format expected by the OpenAI API
    const chatMessages = recentConversation.map(msg => {
        return msg.sender === "You"
            ? { role: "user", content: msg.text }
            : { role: "assistant", content: msg.text };
    });

    // Build the payload with the system prompt and recent conversation
    const payload = {
        messages: [systemPrompt, ...chatMessages]
    };

    // Send the payload to the server via an axios POST request to the /api/fitness_coach endpoint.
    // The CSRF token is included in the request headers.
    axios.post('/api/fitness_coach', payload, {
        headers: {
            "X-CSRFToken": csrfToken
        }
    })
    .then(response => {
        // Extract the AI's reply from the response data
        const reply = response.data.reply;
        // Add the coach's reply to the conversation and save it
        conversation.push({ sender: "Coach", text: reply });
        saveChatHistory();
        // Display the coach's reply in the UI
        addMessage("Coach", reply);
    })
    .catch(error => {
        // Log the error and inform the user that something went wrong
        console.error('Error:', error);
        const errorMsg = 'Sorry, something went wrong.';
        conversation.push({ sender: "Coach", text: errorMsg });
        saveChatHistory();
        addMessage("Coach", errorMsg);
    });
}

// Add event listeners once the DOM content is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // If the chat widget elements are not present, exit the script
    if (!chatToggle || !chatWidget) return;

    // Load any existing chat history from local storage
    loadChatHistory();

    // Event listener for opening the chat widget
    chatToggle.addEventListener('click', () => {
        // Show the chat widget and hide the toggle button
        chatWidget.style.display = 'flex';
        chatToggle.classList.add('hide');

        // If there is no existing conversation, add a welcome message from the AI coach
        if (conversation.length === 0) {
            const welcomeText = "Welcome! I am your AI Fitness Coach. Ask me anything about training and nutrition.";
            conversation.push({ sender: "Coach", text: welcomeText });
            saveChatHistory();
            addMessage("Coach", welcomeText);
        }
    });

    // Event listener for closing the chat widget
    chatClose.addEventListener('click', () => {
        // Hide the chat widget and show the toggle button
        chatWidget.style.display = 'none';
        chatToggle.classList.remove('hide');
    });

    // Event listener for sending a message when the send button is clicked
    chatSend.addEventListener('click', () => {
        const message = chatInput.value.trim();
        // Do nothing if the input is empty
        if (!message) return;
        // Send the message to the server
        sendToServer(message);
    });

    // Event listener to send a message when the Enter key is pressed in the chat input
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent the default action (such as form submission)
            chatSend.click();   // Trigger the send button's click event
        }
    });
});
