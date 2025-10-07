// ===== Global State =====
let currentFile = null;
let isInitialized = false;

// ===== DOM Elements =====
const uploadSection = document.getElementById('upload-section');
const chatSection = document.getElementById('chat-section');
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const uploadStatus = document.getElementById('upload-status');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const resetBtn = document.getElementById('reset-btn');
const statusText = document.getElementById('status-text');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    checkSystemStatus();
});

function initializeEventListeners() {
    // File input events
    fileInput.addEventListener('change', handleFileSelect);
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadBtn.addEventListener('click', handleUpload);

    // Drag and drop events
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // Chat events
    sendBtn.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    // Auto-resize textarea
    chatInput.addEventListener('input', autoResizeTextarea);

    // Reset button
    resetBtn.addEventListener('click', handleReset);
}

// ===== File Upload Handlers =====
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        setCurrentFile(file);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');

    const file = e.dataTransfer.files[0];
    if (file) {
        if (file.name.endsWith('.csv')) {
            setCurrentFile(file);
            // Simulate file input selection for consistency
            const dt = new DataTransfer();
            dt.items.add(file);
            fileInput.files = dt.files;
        } else {
            showStatus('Please drop a CSV file', 'error');
        }
    }
}

function setCurrentFile(file) {
    currentFile = file;
    uploadBtn.disabled = false;
    uploadArea.querySelector('.upload-text').innerHTML = `
        <strong>Selected:</strong> ${file.name} (${formatFileSize(file.size)})
    `;
    showStatus('', '');
}

async function handleUpload() {
    if (!currentFile) {
        showStatus('Please select a CSV file first', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', currentFile);

    try {
        showLoading('Uploading and initializing RAG system...');
        uploadBtn.disabled = true;

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        hideLoading();

        if (result.success) {
            showStatus(
                `✅ ${result.message}<br>Loaded ${result.vehicle_count} vehicles from ${result.filename}`,
                'success'
            );
            isInitialized = true;

            // Wait a moment then switch to chat interface
            setTimeout(() => {
                switchToChatInterface(result);
            }, 1500);
        } else {
            showStatus(`❌ ${result.message || result.error}`, 'error');
            uploadBtn.disabled = false;
        }
    } catch (error) {
        hideLoading();
        showStatus(`❌ Upload failed: ${error.message}`, 'error');
        uploadBtn.disabled = false;
    }
}

// ===== Chat Handlers =====
async function handleSendMessage() {
    const message = chatInput.value.trim();

    if (!message) {
        return;
    }

    if (!isInitialized) {
        addMessage('Please upload a CSV file first', 'system');
        return;
    }

    // Add user message to UI
    addMessage(message, 'user');
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // Disable input while processing
    chatInput.disabled = true;
    sendBtn.disabled = true;

    try {
        showLoading('Thinking...');

        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        const result = await response.json();

        hideLoading();

        if (result.success) {
            addMessage(result.response, 'assistant');
        } else {
            addMessage(`Error: ${result.error || result.response}`, 'system');
        }
    } catch (error) {
        hideLoading();
        addMessage(`Error sending message: ${error.message}`, 'system');
    } finally {
        // Re-enable input
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

function addMessage(content, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Convert bullet points to proper list format
    let formattedContent = content;
    if (type === 'assistant') {
        // Convert bullet points (•) to HTML list
        formattedContent = formattedContent.replace(/•\s+(.+?)(?=\n|$)/g, '<li>$1</li>');
        if (formattedContent.includes('<li>')) {
            formattedContent = formattedContent.replace(/(<li>.*?<\/li>)+/gs, '<ul>$&</ul>');
        }
        // Preserve line breaks
        formattedContent = formattedContent.replace(/\n/g, '<br>');
    }

    contentDiv.innerHTML = formattedContent;
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function handleReset() {
    if (!confirm('Are you sure you want to upload a new CSV? This will clear the current chat session.')) {
        return;
    }

    try {
        showLoading('Resetting system...');

        const response = await fetch('/api/reset', {
            method: 'POST'
        });

        const result = await response.json();

        hideLoading();

        if (result.success) {
            // Reset state
            isInitialized = false;
            currentFile = null;

            // Clear UI
            chatMessages.innerHTML = '';
            uploadStatus.innerHTML = '';
            uploadStatus.className = 'status-message';

            // Reset upload area
            uploadArea.querySelector('.upload-text').innerHTML = `
                <strong>Drop your CSV file here</strong> or
                <label for="file-input" class="file-label">browse</label>
            `;
            uploadBtn.disabled = true;
            fileInput.value = '';

            // Switch back to upload interface
            chatSection.classList.add('hidden');
            uploadSection.classList.remove('hidden');
        } else {
            alert(`Reset failed: ${result.error}`);
        }
    } catch (error) {
        hideLoading();
        alert(`Reset failed: ${error.message}`);
    }
}

// ===== UI Helpers =====
function switchToChatInterface(uploadResult) {
    uploadSection.classList.add('hidden');
    chatSection.classList.remove('hidden');

    // Update status bar
    statusText.textContent = `${uploadResult.filename} - ${uploadResult.vehicle_count} vehicles loaded`;

    // Focus on chat input
    chatInput.focus();
}

function showStatus(message, type) {
    if (!message) {
        uploadStatus.innerHTML = '';
        uploadStatus.className = 'status-message';
        return;
    }

    uploadStatus.innerHTML = message;
    uploadStatus.className = `status-message ${type}`;
}

function showLoading(message = 'Processing...') {
    loadingText.textContent = message;
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

function autoResizeTextarea() {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 150) + 'px';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

async function checkSystemStatus() {
    try {
        const response = await fetch('/api/status');
        const result = await response.json();

        if (result.success && result.status.initialized) {
            // System is already initialized (from a previous session)
            isInitialized = true;
            switchToChatInterface({
                filename: result.status.filename,
                vehicle_count: result.status.vehicle_count
            });
        }
    } catch (error) {
        // Silent fail - user will need to upload a file
        console.log('No active session');
    }
}

// ===== Utility Functions =====
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Prevent form submission on enter in textarea
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
    }
});
