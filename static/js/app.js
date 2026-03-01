// ============ API Configuration ============
const API_BASE = window.location.origin;

// ============ State ============
const state = {
    mode: 'ask',        // 'ask' | 'chat'
    model: 'llama3',    // 'llama3' | 'gemini'
    category: '',
    messages: [],
    isLoading: false,
    isDark: true,
};

// ============ DOM Elements ============
const $ = (id) => document.getElementById(id);
const chatMessages = $('chatMessages');
const questionInput = $('questionInput');
const sendBtn = $('sendBtn');
const welcomeScreen = $('welcomeScreen');
const categorySelect = $('categorySelect');
const docList = $('docList');
const toastContainer = $('toastContainer');
const chatTitle = $('chatTitle');
const themeToggle = $('themeToggle');
const fileInput = $('fileInput');
const uploadArea = $('uploadArea');

// ============ Initialize ============
document.addEventListener('DOMContentLoaded', () => {
    loadDocuments();
    setupEventListeners();
    autoResizeTextarea();
});

// ============ Event Listeners ============
function setupEventListeners() {
    // Send message
    sendBtn.addEventListener('click', sendMessage);
    questionInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto resize textarea
    questionInput.addEventListener('input', autoResizeTextarea);

    // Mode toggle
    document.querySelectorAll('#modeToggle .mode-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#modeToggle .mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.mode = btn.dataset.mode;
            updateChatTitle();
        });
    });

    // Model toggle
    document.querySelectorAll('#modelToggle .mode-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#modelToggle .mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.model = btn.dataset.model;
            updateChatTitle();
            showToast('info', `Model: ${state.model === 'gemini' ? '✨ Gemini' : '🦙 Llama3'}`);
        });
    });

    // Category filter
    categorySelect.addEventListener('change', (e) => {
        state.category = e.target.value;
    });

    // File upload
    fileInput.addEventListener('change', handleFileUpload);

    // Drag & drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            uploadFile(e.dataTransfer.files[0]);
        }
    });

    // Theme toggle
    themeToggle.addEventListener('click', toggleTheme);

    // Clear chat
    $('btnClearChat').addEventListener('click', clearChat);

    // Sidebar toggle (mobile)
    $('btnToggleSidebar').addEventListener('click', () => {
        $('sidebar').classList.toggle('open');
    });

    // Suggestion chips
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            questionInput.value = chip.dataset.question;
            autoResizeTextarea();
            sendMessage();
        });
    });
}

// ============ Send Message ============
async function sendMessage() {
    const question = questionInput.value.trim();
    if (!question || state.isLoading) return;

    state.isLoading = true;
    sendBtn.disabled = true;

    // Hide welcome screen
    if (welcomeScreen) {
        welcomeScreen.style.display = 'none';
    }

    // Add user message
    addMessage('user', question);
    questionInput.value = '';
    autoResizeTextarea();

    // Show typing indicator
    const typingId = showTyping();

    try {
        const endpoint = state.mode === 'chat' ? '/chat' : '/ask';
        const body = { question, model: state.model };
        if (state.mode === 'ask' && state.category) {
            body.category = state.category;
        }

        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Sunucu hatası');
        }

        const data = await response.json();
        removeTyping(typingId);
        addMessage('assistant', data.answer, data.sources || [], data.model || state.model);

    } catch (error) {
        removeTyping(typingId);
        addMessage('assistant', `⚠️ Hata: ${error.message}. API sunucusunun çalıştığından emin olun.`);
        showToast('error', error.message);
    } finally {
        state.isLoading = false;
        sendBtn.disabled = false;
        questionInput.focus();
    }
}

// ============ Message Rendering ============
function addMessage(role, content, sources = [], model = '') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = role === 'user' ? '👤' : '🤖';

    let sourceTags = '';
    if (sources.length > 0) {
        const uniqueSources = [...new Set(sources)];
        sourceTags = uniqueSources.map(s => `<span class="source-tag">📎 ${s}</span>`).join('');
    }

    let modelBadge = '';
    if (role === 'assistant' && model) {
        const modelLabel = model === 'gemini' ? '✨ Gemini' : '🦙 Llama3';
        modelBadge = `<span class="source-tag" style="background: rgba(255,107,157,0.12); color: var(--accent-secondary);">${modelLabel}</span>`;
    }

    const hasMeta = modelBadge || sourceTags;

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            ${escapeHtml(content).replace(/\n/g, '<br>')}
            ${hasMeta ? `<div class="message-sources">${modelBadge}${sourceTags}</div>` : ''}
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function updateChatTitle() {
    const modeText = state.mode === 'ask' ? '💡 Tek Soru' : '💬 Sohbet';
    const modelText = state.model === 'gemini' ? '✨ Gemini' : '🦙 Llama3';
    chatTitle.textContent = `${modeText} — ${modelText}`;
}

function showTyping() {
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.id = id;
    div.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(div);
    scrollToBottom();
    return id;
}

function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============ File Upload ============
function handleFileUpload(e) {
    if (e.target.files.length > 0) {
        uploadFile(e.target.files[0]);
    }
}

async function uploadFile(file) {
    const allowed = ['.txt', '.pdf', '.md'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowed.includes(ext)) {
        showToast('error', `Desteklenmeyen dosya türü: ${ext}`);
        return;
    }

    showToast('info', `${file.name} yükleniyor...`);

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Yükleme başarısız');
        }

        const data = await response.json();
        showToast('success', data.message);
        loadDocuments();
        fileInput.value = '';
    } catch (error) {
        showToast('error', error.message);
    }
}

// ============ Document List ============
async function loadDocuments() {
    try {
        const response = await fetch(`${API_BASE}/documents`);
        if (!response.ok) throw new Error('Dökümanlar yüklenemedi');

        const data = await response.json();
        renderDocuments(data.documents);
        $('apiStatus').textContent = 'API Bağlı';
    } catch (error) {
        docList.innerHTML = `
            <div class="status-badge" style="border-left: 2px solid var(--error);">
                ⚠️ API bağlantısı yok
            </div>
        `;
        $('apiStatus').textContent = 'API Bağlantısı Yok';
    }
}

function renderDocuments(docs) {
    if (docs.length === 0) {
        docList.innerHTML = `
            <div class="status-badge">
                📭 Henüz döküman yok
            </div>
        `;
        return;
    }

    const icons = {
        '.txt': '📄',
        '.pdf': '📕',
        '.md': '📝',
    };

    docList.innerHTML = docs.map(doc => {
        const ext = '.' + doc.split('.').pop().toLowerCase();
        const icon = icons[ext] || '📄';
        return `<div class="doc-item">
            <span class="doc-icon">${icon}</span>
            <span class="doc-name">${doc}</span>
        </div>`;
    }).join('');
}

// ============ Theme ============
function toggleTheme() {
    state.isDark = !state.isDark;
    document.documentElement.setAttribute('data-theme', state.isDark ? 'dark' : 'light');
    themeToggle.classList.toggle('active', state.isDark);
}

// ============ Clear Chat ============
function clearChat() {
    state.messages = [];
    chatMessages.innerHTML = '';

    // Re-show welcome screen
    const welcome = document.createElement('div');
    welcome.className = 'chat-welcome';
    welcome.id = 'welcomeScreen';
    welcome.innerHTML = `
        <div class="welcome-icon">🧠</div>
        <h3>Merhaba! Ben AI Bilgi Asistanınız</h3>
        <p>Yüklediğiniz dökümanlardan bilgi çıkararak sorularınızı cevaplıyorum. Bir soru sorarak başlayın!</p>
        <div class="welcome-suggestions">
            <button class="suggestion-chip" data-question="NLP nedir?">NLP nedir?</button>
            <button class="suggestion-chip" data-question="Overfitting nedir?">Overfitting nedir?</button>
            <button class="suggestion-chip" data-question="Python ne için kullanılır?">Python ne için kullanılır?</button>
        </div>
    `;
    chatMessages.appendChild(welcome);

    // Re-bind suggestion chips
    welcome.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            questionInput.value = chip.dataset.question;
            autoResizeTextarea();
            sendMessage();
        });
    });

    showToast('info', 'Sohbet temizlendi');
}

// ============ Toast Notifications ============
function showToast(type, message) {
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `${icons[type] || ''} ${message}`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// ============ Auto Resize Textarea ============
function autoResizeTextarea() {
    questionInput.style.height = 'auto';
    questionInput.style.height = Math.min(questionInput.scrollHeight, 120) + 'px';
}
