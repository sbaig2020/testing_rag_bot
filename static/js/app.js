// AI RAG Bot Frontend Application
class AIRagBot {
    constructor() {
        this.socket = null;
        this.currentSessionId = null;
        this.settings = {
            model: 'claude-3-sonnet-20240229',
            temperature: 0.7,
            maxTokens: 4000,
            ragResults: 5,
            systemPrompt: ''
        };
        this.isConnected = false;
        this.isTyping = false;
        
        this.init();
    }

    init() {
        this.initializeSocket();
        this.bindEvents();
        this.loadSettings();
        this.updateStats();
        this.createInitialSession();
    }

    initializeSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.isConnected = true;
            this.updateConnectionStatus('Connected');
            this.showToast('Connected to AI RAG Bot', 'success');
        });

        this.socket.on('disconnect', () => {
            this.isConnected = false;
            this.updateConnectionStatus('Disconnected');
            this.showToast('Disconnected from server', 'error');
        });

        this.socket.on('user_message', (data) => {
            this.displayMessage('user', data.message, data.timestamp);
        });

        this.socket.on('ai_response', (data) => {
            this.hideTypingIndicator();
            this.displayMessage('assistant', data.response, data.timestamp, data.context_info);
        });

        this.socket.on('error', (data) => {
            this.hideTypingIndicator();
            this.showToast(data.error || 'An error occurred', 'error');
        });
    }

    bindEvents() {
        // Header controls
        document.getElementById('settingsBtn').addEventListener('click', () => this.openModal('settingsModal'));
        document.getElementById('documentsBtn').addEventListener('click', () => this.openDocumentsModal());
        document.getElementById('statsBtn').addEventListener('click', () => this.openStatsModal());

        // Session management
        document.getElementById('newSessionBtn').addEventListener('click', () => this.createNewSession());

        // File upload
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleFileDrop.bind(this));
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));

        // Chat controls
        document.getElementById('ragToggle').addEventListener('click', this.toggleRAG.bind(this));
        document.getElementById('clearChatBtn').addEventListener('click', this.clearChat.bind(this));
        document.getElementById('exportChatBtn').addEventListener('click', this.exportChat.bind(this));

        // Message input
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');

        messageInput.addEventListener('keydown', this.handleMessageKeydown.bind(this));
        messageInput.addEventListener('input', this.handleMessageInput.bind(this));
        sendBtn.addEventListener('click', this.sendMessage.bind(this));

        // Modal controls
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', this.closeModals.bind(this));
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeModals();
        });

        // Settings
        document.getElementById('saveSettingsBtn').addEventListener('click', this.saveSettings.bind(this));
        document.getElementById('temperatureSlider').addEventListener('input', this.updateTemperatureDisplay.bind(this));
        document.getElementById('ragResultsSlider').addEventListener('input', this.updateRagResultsDisplay.bind(this));

        // Document search
        document.getElementById('searchDocsBtn').addEventListener('click', () => this.openModal('docSearchModal'));
        document.getElementById('executeSearchBtn').addEventListener('click', this.searchDocuments.bind(this));
        document.getElementById('refreshDocsBtn').addEventListener('click', this.loadDocuments.bind(this));
    }

    // Session Management
    async createInitialSession() {
        try {
            const response = await fetch('/api/session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    system_prompt: this.settings.systemPrompt,
                    settings: this.settings
                })
            });

            const data = await response.json();
            if (data.session_id) {
                this.currentSessionId = data.session_id;
                this.socket.emit('join_session', { session_id: this.currentSessionId });
                this.updateSessionTitle('New Session');
                this.loadSessions();
            }
        } catch (error) {
            console.error('Error creating session:', error);
            this.showToast('Failed to create session', 'error');
        }
    }

    async createNewSession() {
        try {
            const response = await fetch('/api/session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    system_prompt: this.settings.systemPrompt,
                    settings: this.settings
                })
            });

            const data = await response.json();
            if (data.session_id) {
                // Leave current session
                if (this.currentSessionId) {
                    this.socket.emit('leave_session', { session_id: this.currentSessionId });
                }

                // Join new session
                this.currentSessionId = data.session_id;
                this.socket.emit('join_session', { session_id: this.currentSessionId });
                
                // Clear chat and update UI
                this.clearChatMessages();
                this.updateSessionTitle('New Session');
                this.loadSessions();
                this.showToast('New session created', 'success');
            }
        } catch (error) {
            console.error('Error creating new session:', error);
            this.showToast('Failed to create new session', 'error');
        }
    }

    async loadSessions() {
        try {
            const response = await fetch('/api/statistics');
            const data = await response.json();
            
            const sessionsList = document.getElementById('sessionsList');
            sessionsList.innerHTML = '';

            if (data.chat_sessions && data.chat_sessions.sessions) {
                data.chat_sessions.sessions.forEach(session => {
                    const sessionElement = this.createSessionElement(session);
                    sessionsList.appendChild(sessionElement);
                });
            }
        } catch (error) {
            console.error('Error loading sessions:', error);
        }
    }

    createSessionElement(session) {
        const div = document.createElement('div');
        div.className = `session-item ${session.session_id === this.currentSessionId ? 'active' : ''}`;
        div.innerHTML = `
            <div class="session-title">${session.last_message ? session.last_message.substring(0, 30) + '...' : 'New Session'}</div>
            <div class="session-time">${new Date(session.created_at).toLocaleString()}</div>
        `;
        
        div.addEventListener('click', () => this.switchSession(session.session_id));
        return div;
    }

    async switchSession(sessionId) {
        if (sessionId === this.currentSessionId) return;

        try {
            // Leave current session
            if (this.currentSessionId) {
                this.socket.emit('leave_session', { session_id: this.currentSessionId });
            }

            // Join new session
            this.currentSessionId = sessionId;
            this.socket.emit('join_session', { session_id: sessionId });

            // Load session messages
            await this.loadSessionMessages(sessionId);
            this.loadSessions(); // Refresh session list
            this.showToast('Switched to session', 'info');
        } catch (error) {
            console.error('Error switching session:', error);
            this.showToast('Failed to switch session', 'error');
        }
    }

    async loadSessionMessages(sessionId) {
        try {
            const response = await fetch(`/api/session/${sessionId}/messages`);
            const data = await response.json();

            this.clearChatMessages();
            
            if (data.messages) {
                data.messages.forEach(message => {
                    if (message.role !== 'system') {
                        this.displayMessage(message.role, message.content, message.timestamp, message.metadata);
                    }
                });
            }
        } catch (error) {
            console.error('Error loading session messages:', error);
        }
    }

    // Message Handling
    handleMessageKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    }

    handleMessageInput(e) {
        const textarea = e.target;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message || !this.currentSessionId) return;

        const useRag = document.getElementById('useRagCheckbox').checked;

        // Clear input and show typing indicator
        messageInput.value = '';
        messageInput.style.height = 'auto';
        this.showTypingIndicator();

        try {
            // Send via WebSocket for real-time updates
            this.socket.emit('send_message', {
                session_id: this.currentSessionId,
                message: message,
                use_rag: useRag
            });
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.showToast('Failed to send message', 'error');
        }
    }

    displayMessage(role, content, timestamp, metadata = null) {
        const messagesContainer = document.getElementById('chatMessages');
        
        // Remove welcome message if it exists
        const welcomeMessage = messagesContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.innerHTML = this.formatMessageContent(content);

        contentDiv.appendChild(textDiv);

        // Add context info for assistant messages
        if (role === 'assistant' && metadata && metadata.retrieved_documents > 0) {
            const contextDiv = document.createElement('div');
            contextDiv.className = 'context-info';
            contextDiv.innerHTML = `
                <div><strong>RAG Context:</strong> ${metadata.retrieved_documents} documents retrieved</div>
                ${metadata.sources ? `<div class="context-sources"><strong>Sources:</strong> ${metadata.sources.join(', ')}</div>` : ''}
            `;
            contentDiv.appendChild(contextDiv);
        }

        // Add timestamp
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        metaDiv.innerHTML = `
            <span>${new Date(timestamp).toLocaleTimeString()}</span>
            ${metadata && metadata.usage ? `<span>Tokens: ${metadata.usage.input_tokens + metadata.usage.output_tokens}</span>` : ''}
        `;
        contentDiv.appendChild(metaDiv);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    formatMessageContent(content) {
        // Basic markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    showTypingIndicator() {
        this.isTyping = true;
        document.getElementById('typingIndicator').classList.remove('hidden');
    }

    hideTypingIndicator() {
        this.isTyping = false;
        document.getElementById('typingIndicator').classList.add('hidden');
    }

    clearChatMessages() {
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.innerHTML = '';
    }

    async clearChat() {
        if (!this.currentSessionId) return;

        if (confirm('Are you sure you want to clear this conversation?')) {
            try {
                // Create a new session instead of clearing
                await this.createNewSession();
            } catch (error) {
                console.error('Error clearing chat:', error);
                this.showToast('Failed to clear chat', 'error');
            }
        }
    }

    async exportChat() {
        if (!this.currentSessionId) return;

        const format = prompt('Export format (json, txt, md):', 'txt');
        if (!format) return;

        try {
            const response = await fetch(`/api/session/${this.currentSessionId}/export?format=${format}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `conversation_${this.currentSessionId}.${format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showToast('Chat exported successfully', 'success');
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            console.error('Error exporting chat:', error);
            this.showToast('Failed to export chat', 'error');
        }
    }

    // File Upload
    handleDragOver(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
    }

    handleFileDrop(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files);
        this.uploadFiles(files);
    }

    handleFileSelect(e) {
        const files = Array.from(e.target.files);
        this.uploadFiles(files);
        e.target.value = ''; // Reset input
    }

    async uploadFiles(files) {
        const progressContainer = document.getElementById('uploadProgress');
        const progressFill = progressContainer.querySelector('.progress-fill');
        const progressText = progressContainer.querySelector('.progress-text');

        progressContainer.classList.remove('hidden');

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            
            try {
                progressText.textContent = `Uploading ${file.name}...`;
                progressFill.style.width = `${((i + 0.5) / files.length) * 100}%`;

                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (response.ok) {
                    this.showToast(`${file.name} uploaded successfully`, 'success');
                    progressFill.style.width = `${((i + 1) / files.length) * 100}%`;
                } else {
                    throw new Error(result.error || 'Upload failed');
                }
            } catch (error) {
                console.error('Upload error:', error);
                this.showToast(`Failed to upload ${file.name}: ${error.message}`, 'error');
            }
        }

        progressContainer.classList.add('hidden');
        this.updateStats();
    }

    // Settings
    loadSettings() {
        const saved = localStorage.getItem('aiRagBotSettings');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
        }

        // Update UI
        document.getElementById('modelSelect').value = this.settings.model;
        document.getElementById('temperatureSlider').value = this.settings.temperature;
        document.getElementById('maxTokensInput').value = this.settings.maxTokens;
        document.getElementById('ragResultsSlider').value = this.settings.ragResults;
        document.getElementById('systemPromptInput').value = this.settings.systemPrompt;

        this.updateTemperatureDisplay();
        this.updateRagResultsDisplay();
    }

    saveSettings() {
        this.settings = {
            model: document.getElementById('modelSelect').value,
            temperature: parseFloat(document.getElementById('temperatureSlider').value),
            maxTokens: parseInt(document.getElementById('maxTokensInput').value),
            ragResults: parseInt(document.getElementById('ragResultsSlider').value),
            systemPrompt: document.getElementById('systemPromptInput').value
        };

        localStorage.setItem('aiRagBotSettings', JSON.stringify(this.settings));
        this.closeModals();
        this.showToast('Settings saved', 'success');
    }

    updateTemperatureDisplay() {
        const value = document.getElementById('temperatureSlider').value;
        document.getElementById('temperatureValue').textContent = value;
    }

    updateRagResultsDisplay() {
        const value = document.getElementById('ragResultsSlider').value;
        document.getElementById('ragResultsValue').textContent = value;
    }

    toggleRAG() {
        const toggle = document.getElementById('ragToggle');
        const checkbox = document.getElementById('useRagCheckbox');
        
        checkbox.checked = !checkbox.checked;
        toggle.classList.toggle('active', checkbox.checked);
    }

    // Documents
    async openDocumentsModal() {
        this.openModal('documentsModal');
        await this.loadDocuments();
    }

    async loadDocuments() {
        try {
            const response = await fetch('/api/documents');
            const data = await response.json();

            const documentsList = document.getElementById('documentsList');
            documentsList.innerHTML = '';

            if (data.documents && data.documents.length > 0) {
                data.documents.forEach(doc => {
                    const docElement = this.createDocumentElement(doc);
                    documentsList.appendChild(docElement);
                });
            } else {
                documentsList.innerHTML = '<p class="text-center text-muted">No documents uploaded yet.</p>';
            }
        } catch (error) {
            console.error('Error loading documents:', error);
            this.showToast('Failed to load documents', 'error');
        }
    }

    createDocumentElement(doc) {
        const div = document.createElement('div');
        div.className = 'document-item';
        div.innerHTML = `
            <div class="document-info">
                <h4>${doc.source_file}</h4>
                <div class="document-meta">
                    Type: ${doc.file_type} | Chunks: ${doc.chunks} | Created: ${new Date(doc.created_at).toLocaleString()}
                </div>
            </div>
            <div class="document-actions">
                <button class="btn btn-outline" onclick="aiRagBot.deleteDocument('${doc.source_file}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        return div;
    }

    async deleteDocument(sourceFile) {
        if (!confirm(`Are you sure you want to delete ${sourceFile}?`)) return;

        try {
            const response = await fetch(`/api/documents/${encodeURIComponent(sourceFile)}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Document deleted successfully', 'success');
                await this.loadDocuments();
                this.updateStats();
            } else {
                throw new Error('Delete failed');
            }
        } catch (error) {
            console.error('Error deleting document:', error);
            this.showToast('Failed to delete document', 'error');
        }
    }

    async searchDocuments() {
        const query = document.getElementById('searchQueryInput').value.trim();
        if (!query) return;

        try {
            const response = await fetch('/api/documents/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, n_results: this.settings.ragResults })
            });

            const data = await response.json();
            const resultsContainer = document.getElementById('searchResults');
            resultsContainer.innerHTML = '';

            if (data.results && data.results.length > 0) {
                data.results.forEach(result => {
                    const resultElement = this.createSearchResultElement(result);
                    resultsContainer.appendChild(resultElement);
                });
            } else {
                resultsContainer.innerHTML = '<p class="text-center text-muted">No results found.</p>';
            }
        } catch (error) {
            console.error('Error searching documents:', error);
            this.showToast('Search failed', 'error');
        }
    }

    createSearchResultElement(result) {
        const div = document.createElement('div');
        div.className = 'search-result';
        div.innerHTML = `
            <div class="search-result-content">${result.content.substring(0, 200)}...</div>
            <div class="search-result-meta">
                <span>Source: ${result.metadata.source_file}</span>
                <span>Similarity: ${(1 - result.distance).toFixed(3)}</span>
            </div>
        `;
        return div;
    }

    // Statistics
    async openStatsModal() {
        this.openModal('statsModal');
        await this.loadStatistics();
    }

    async loadStatistics() {
        try {
            const response = await fetch('/api/statistics');
            const data = await response.json();

            const statsContent = document.getElementById('statisticsContent');
            statsContent.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Total Documents</h3>
                        <div class="stat-number">${data.vector_store.total_documents || 0}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Chat Sessions</h3>
                        <div class="stat-number">${data.chat_sessions.total_sessions || 0}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Active Sessions</h3>
                        <div class="stat-number">${data.chat_sessions.active_sessions || 0}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Embedding Model</h3>
                        <div class="stat-number" style="font-size: 1rem;">${data.vector_store.embedding_model || 'N/A'}</div>
                    </div>
                </div>
                <div class="settings-section">
                    <h3>File Types</h3>
                    <div class="document-meta">
                        ${Object.entries(data.vector_store.file_types || {}).map(([type, count]) => 
                            `${type}: ${count}`
                        ).join(' | ')}
                    </div>
                </div>
                <div class="settings-section">
                    <h3>System Configuration</h3>
                    <div class="document-meta">
                        Max File Size: ${data.system.max_file_size} | 
                        Allowed Extensions: ${data.system.allowed_extensions.join(', ')} | 
                        Default Model: ${data.system.default_model}
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error loading statistics:', error);
            document.getElementById('statisticsContent').innerHTML = '<p class="text-center text-muted">Failed to load statistics.</p>';
        }
    }

    async updateStats() {
        try {
            const response = await fetch('/api/statistics');
            const data = await response.json();

            document.getElementById('docCount').textContent = data.vector_store.total_documents || 0;
            document.getElementById('chunkCount').textContent = Object.values(data.vector_store.file_types || {}).reduce((a, b) => a + b, 0);
        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }

    // UI Helpers
    openModal(modalId) {
        document.getElementById(modalId).classList.add('show');
    }

    closeModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('show');
        });
    }

    updateConnectionStatus(status) {
        document.getElementById('sessionStatus').textContent = status;
        document.getElementById('sessionStatus').className = `status-indicator ${status.toLowerCase()}`;
    }

    updateSessionTitle(title) {
        document.getElementById('sessionTitle').textContent = title;
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-${this.getToastIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;

        document.getElementById('toastContainer').appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    showLoading() {
        document.getElementById('loadingOverlay').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.add('hidden');
    }
}

// Initialize the application
let aiRagBot;
document.addEventListener('DOMContentLoaded', () => {
    aiRagBot = new AIRagBot();
});

// Make aiRagBot globally accessible for inline event handlers
window.aiRagBot = aiRagBot;
