const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const newChatBtn = document.getElementById("new-chat-btn");

// Handle sending messages
function handleSend() {
  const msg = input.value.trim();
  if (msg) {
    addMessage(msg, "user");
    input.value = "";
    
    // Call the function to send to Flask backend
    sendToBackend(msg);
  }
}

// Handle new chat
newChatBtn.addEventListener("click", () => {
  chatBox.innerHTML = "";
});

// Event listeners
sendBtn.addEventListener("click", handleSend);
input.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    handleSend();
  }
});

// Add message to chat box
function addMessage(text, type) {
  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${type}`;
  msgDiv.textContent = text;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Send message to Flask backend
async function sendToBackend(userInput) {
  try {
    const response = await fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: userInput })
    });

    const data = await response.json();
    const botReply = data.response || data.error || "No response from AI.";
    addMessage(botReply, "bot");
  } catch (error) {
    console.error("Error sending message:", error);
    addMessage("Sorry, I'm having trouble connecting. Please try again later.", "bot");
  }
}