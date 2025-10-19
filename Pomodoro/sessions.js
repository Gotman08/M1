/**
 * Sessions module
 * Manages study session recording, display, and tagging
 */
const Sessions = {
    elements: {
        list: null,
        tagsInput: null,
        noteInput: null,
        saveBtn: null,
        hint: null
    },

    lastSessionId: null,

    /**
     * Initialize sessions module
     */
    init() {
        this.elements.list = document.getElementById('sessions-list');
        this.elements.tagsInput = document.getElementById('session-tags');
        this.elements.noteInput = document.getElementById('session-note');
        this.elements.saveBtn = document.getElementById('save-session-btn');
        this.elements.hint = document.getElementById('session-hint');

        this.elements.saveBtn.addEventListener('click', () => this.saveManually());

        this.render();
    },

    /**
     * Save a new session with tags and note from inputs
     * @param {Object} session - base session object
     */
    saveSession(session) {
        const tagsValue = this.elements.tagsInput.value.trim();
        const noteValue = this.elements.noteInput.value.trim();

        session.id = Date.now();
        session.tags = tagsValue 
            ? tagsValue.split(',').map(tag => tag.trim()).filter(tag => tag)
            : [];
        session.note = noteValue;

        Storage.addSession(session);

        this.lastSessionId = session.id;

        this.elements.saveBtn.style.display = 'inline-block';
        this.elements.hint.style.display = 'block';

        this.render();

        if (typeof Goals !== 'undefined') {
            Goals.updateProgress();
        }
    },

    /**
     * Save tags and note manually to the last session
     */
    saveManually() {
        if (!this.lastSessionId) {
            alert('aucune session recente a modifier');
            return;
        }

        const sessions = Storage.getSessions();
        const sessionIndex = sessions.findIndex(s => s.id === this.lastSessionId);

        if (sessionIndex === -1) {
            alert('session introuvable');
            return;
        }

        const tagsValue = this.elements.tagsInput.value.trim();
        const noteValue = this.elements.noteInput.value.trim();

        sessions[sessionIndex].tags = tagsValue
            ? tagsValue.split(',').map(tag => tag.trim()).filter(tag => tag)
            : [];
        sessions[sessionIndex].note = noteValue;

        Storage.set(Storage.KEYS.SESSIONS, sessions);

        this.elements.tagsInput.value = '';
        this.elements.noteInput.value = '';
        this.elements.saveBtn.style.display = 'none';
        this.elements.hint.style.display = 'none';

        this.render();

        alert('session modifiee');
    },

    /**
     * Render all sessions to DOM
     */
    render() {
        const sessions = Storage.getSessions();

        if (sessions.length === 0) {
            this.elements.list.innerHTML = '<p class="empty-state">aucune session encore</p>';
            return;
        }

        this.elements.list.innerHTML = sessions.map(session => 
            this.renderSessionItem(session)
        ).join('');
    },

    /**
     * Render a single session item
     * @param {Object} session - session object
     * @returns {string} HTML string
     */
    renderSessionItem(session) {
        const startDate = new Date(session.startTime);
        const durationMinutes = Math.floor(session.duration / 60);
        const points = durationMinutes;

        const tagsHtml = session.tags.length > 0
            ? session.tags.map(tag => `<span class="tag">${this.escapeHtml(tag)}</span>`).join('')
            : '';

        const noteHtml = session.note
            ? `<div class="session-note">${this.escapeHtml(session.note)}</div>`
            : '';

        return `
            <div class="session-item">
                <div class="session-header">
                    <span class="session-duration">${durationMinutes} min</span>
                    <span class="session-points">+${points} pts</span>
                </div>
                ${tagsHtml ? `<div class="session-tags">${tagsHtml}</div>` : ''}
                ${noteHtml}
                <div class="session-date">${this.formatDate(startDate)}</div>
            </div>
        `;
    },

    /**
     * Format date for display
     * @param {Date} date - date object
     * @returns {string} formatted date string
     */
    formatDate(date) {
        const now = new Date();
        const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

        if (diffDays === 0) {
            return `aujourd'hui ${date.getHours()}h${String(date.getMinutes()).padStart(2, '0')}`;
        } else if (diffDays === 1) {
            return 'hier';
        } else if (diffDays < 7) {
            return `il y a ${diffDays} jours`;
        } else {
            return date.toLocaleDateString('fr-FR', { 
                day: 'numeric', 
                month: 'short' 
            });
        }
    },

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - text to escape
     * @returns {string} escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Get total study time in minutes
     * @param {Date} startDate - filter sessions from this date
     * @returns {number} total minutes
     */
    getTotalMinutes(startDate = null) {
        const sessions = Storage.getSessions();
        return sessions
            .filter(session => {
                if (!startDate) return true;
                return new Date(session.startTime) >= startDate;
            })
            .reduce((total, session) => total + Math.floor(session.duration / 60), 0);
    },

    /**
     * Get session count
     * @param {Date} startDate - filter sessions from this date
     * @returns {number} session count
     */
    getSessionCount(startDate = null) {
        const sessions = Storage.getSessions();
        if (!startDate) return sessions.length;
        return sessions.filter(session => 
            new Date(session.startTime) >= startDate
        ).length;
    }
};
