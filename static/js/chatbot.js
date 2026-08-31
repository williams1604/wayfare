
document.addEventListener('DOMContentLoaded', function() {
    // Inject Chatbot HTML
    const chatbotContainer = document.createElement('div');
    chatbotContainer.id = 'wayfar-chatbot-container';
    chatbotContainer.innerHTML = `
        <div id="chatbot-button" class="fixed bottom-6 right-6 z-50 transition-transform hover:scale-110 cursor-pointer">
            <div class="bg-[#FF6B35] w-14 h-14 rounded-full shadow-lg flex items-center justify-center text-white">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
            </div>
        </div>

        <div id="chatbot-window" class="fixed bottom-24 right-6 w-80 bg-white rounded-lg shadow-2xl z-50 hidden flex flex-col overflow-hidden border border-gray-200" style="height: 400px;">
            <div class="bg-[#2D3142] text-white p-4 flex justify-between items-center">
                <h3 class="font-semibold">Wayfar Assistant</h3>
                <button id="close-chat" class="text-gray-300 hover:text-white">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                </button>
            </div>
            <div id="chat-messages" class="flex-1 p-4 overflow-y-auto bg-gray-50 space-y-3">
                <div class="flex items-start">
                    <div class="bg-gray-200 rounded-lg py-2 px-3 text-sm text-gray-800 max-w-[85%]">
                        👋 Hi there! I'm your Wayfar travel assistant. How can I help you today?
                    </div>
                </div>
            </div>
            <div class="p-3 bg-white border-t border-gray-200">
                <div class="flex items-center space-x-2">
                    <input type="text" id="chat-input" placeholder="Type a message..." class="flex-1 border border-gray-300 rounded-full py-2 px-4 text-sm focus:outline-none focus:border-[#FF6B35]">
                    <button id="send-message" class="bg-[#FF6B35] text-white p-2 rounded-full hover:bg-[#e55a2b] transition">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(chatbotContainer);

    // Event Listeners
    const chatButton = document.getElementById('chatbot-button');
    const chatWindow = document.getElementById('chatbot-window');
    const closeChat = document.getElementById('close-chat');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-message');
    const messagesContainer = document.getElementById('chat-messages');

    function toggleChat() {
        chatWindow.classList.toggle('hidden');
        if (!chatWindow.classList.contains('hidden')) {
            chatInput.focus();
        }
    }

    chatButton.addEventListener('click', toggleChat);
    closeChat.addEventListener('click', toggleChat);

    function addMessage(text, isUser = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = isUser ? 'flex items-end justify-end' : 'flex items-start';
        
        const bubble = document.createElement('div');
        bubble.className = isUser 
            ? 'bg-[#FF6B35] text-white rounded-lg py-2 px-3 text-sm max-w-[85%]' 
            : 'bg-gray-200 text-gray-800 rounded-lg py-2 px-3 text-sm max-w-[85%]';
        bubble.textContent = text;
        
        msgDiv.appendChild(bubble);
        messagesContainer.appendChild(msgDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function handleUserMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        addMessage(text, true);
        chatInput.value = '';

        // Simulate typing delay
        setTimeout(() => {
            const response = getBotResponse(text);
            addMessage(response);
        }, 600);
    }

    sendButton.addEventListener('click', handleUserMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') handleUserMessage();
    });

    function getBotResponse(input) {
        const lowerInput = input.toLowerCase();
        
        if (lowerInput.includes('hello') || lowerInput.includes('hi')) {
            return "Hello! Ready to explore some amazing destinations?";
        }
        if (lowerInput.includes('lost') || lowerInput.includes('location')) {
            return "I can help with that! Are you currently on a trip or looking for a destination on our site?";
        }
        if (lowerInput.includes('package') || lowerInput.includes('price')) {
            return "Our packages start from ₹1.5 Lakhs. You can view all details on our Packages page.";
        }
        if (lowerInput.includes('contact') || lowerInput.includes('help')) {
            return "You can reach our support team at support@wayfare.com or call +1 (555) 123-4567.";
        }
        return "I'm not sure about that. Try asking about 'packages', 'destinations', or 'contacting support'.";
    }
});
