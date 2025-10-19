/**
 * History module
 * Displays all study sessions with their details and statistics
 */
const History = {
    elements: {
        list: null
    },

    /**
     * Initialize history module
     */
    init() {
        this.elements.list = document.getElementById('history-list');
        this.render();
    },

    /**
     * Render all study sessions
     */
    render() {
        const studySessions = Storage.getStudySessions();

        if (studySessions.length === 0) {
            this.elements.list.innerHTML = '<p class="empty-state">aucune session etude encore</p>';
            return;
        }

        this.elements.list.innerHTML = studySessions.map(studySession => 
            this.renderStudySessionCard(studySession)
        ).join('');
    },

    /**
     * Render a study session card
     * @param {Object} studySession - study session object
     * @returns {string} HTML string
     */
    renderStudySessionCard(studySession) {
        const sessions = Storage.getSessions();
        const relatedSessions = sessions.filter(s => 
            s.sessionName === studySession.name
        );

        const totalMinutes = relatedSessions.reduce((sum, s) => 
            sum + Math.floor(s.duration / 60), 0
        );
        const totalPoints = totalMinutes;
        const sessionCount = relatedSessions.length;

        const startDate = new Date(studySession.startedAt);
        const isActive = studySession.isActive !== false;
        const statusBadge = isActive 
            ? '<span class="status-badge status-active">en cours</span>'
            : '<span class="status-badge status-ended">terminee</span>';

        return `
            <div class="history-card ${isActive ? 'history-card-active' : ''}" onclick="History.showDetails(${studySession.id})">
                <div class="history-header">
                    <div>
                        <h3>${this.escapeHtml(studySession.name)}</h3>
                        ${statusBadge}
                    </div>
                    <span class="history-date">${this.formatDate(startDate)}</span>
                </div>
                ${studySession.description ? 
                    `<p class="history-desc">${this.escapeHtml(studySession.description)}</p>` : ''
                }
                <div class="history-stats">
                    <div class="history-stat">
                        <span class="stat-label">pomodoros</span>
                        <span class="stat-value">🍅 ${sessionCount}</span>
                    </div>
                    <div class="history-stat">
                        <span class="stat-label">temps total</span>
                        <span class="stat-value">⏱️ ${totalMinutes} min</span>
                    </div>
                    <div class="history-stat">
                        <span class="stat-label">points</span>
                        <span class="stat-value">⭐ ${totalPoints}</span>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Show detailed view of a study session
     * @param {number} studySessionId - study session id
     */
    showDetails(studySessionId) {
        const studySessions = Storage.getStudySessions();
        const studySession = studySessions.find(s => s.id === studySessionId);
        
        if (!studySession) return;

        const sessions = Storage.getSessions();
        const relatedSessions = sessions.filter(s => 
            s.sessionName === studySession.name
        );

        const totalMinutes = relatedSessions.reduce((sum, s) => 
            sum + Math.floor(s.duration / 60), 0
        );

        const isActive = studySession.isActive !== false;
        const statusBadge = isActive 
            ? '<span class="status-badge status-active">en cours</span>'
            : '<span class="status-badge status-ended">terminee</span>';
        
        const endInfo = studySession.endedAt 
            ? `<p style="color: var(--text-muted); font-size: 14px;">terminee le ${this.formatDate(new Date(studySession.endedAt))}</p>`
            : '';

        // Create modal
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <div>
                        <h2>${this.escapeHtml(studySession.name)}</h2>
                        ${statusBadge}
                    </div>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">✕</button>
                </div>
                ${studySession.description ? 
                    `<p class="modal-desc">${this.escapeHtml(studySession.description)}</p>` : ''
                }
                ${endInfo}
                <div class="modal-summary">
                    <div class="summary-box">
                        <div class="summary-icon">🍅</div>
                        <div class="summary-text">
                            <div class="summary-value">${relatedSessions.length}</div>
                            <div class="summary-label">pomodoros</div>
                        </div>
                    </div>
                    <div class="summary-box">
                        <div class="summary-icon">⏱️</div>
                        <div class="summary-text">
                            <div class="summary-value">${totalMinutes}</div>
                            <div class="summary-label">minutes</div>
                        </div>
                    </div>
                    <div class="summary-box">
                        <div class="summary-icon">⭐</div>
                        <div class="summary-text">
                            <div class="summary-value">${totalMinutes}</div>
                            <div class="summary-label">points</div>
                        </div>
                    </div>
                </div>
                <h3>détail des pomodoros</h3>
                <div class="modal-sessions-list">
                    ${relatedSessions.map(s => this.renderSessionDetail(s)).join('')}
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Close on overlay click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    },

    /**
     * Render session detail in modal
     * @param {Object} session - session object
     * @returns {string} HTML string
     */
    renderSessionDetail(session) {
        const startDate = new Date(session.startTime);
        const endDate = new Date(session.endTime);
        const durationMinutes = Math.floor(session.duration / 60);
        const durationSeconds = session.duration % 60;

        return `
            <div class="session-detail">
                <div class="session-detail-time">
                    ${this.formatTime(startDate)} - ${this.formatTime(endDate)}
                </div>
                <div class="session-detail-duration">
                    ${durationMinutes}:${String(durationSeconds).padStart(2, '0')}
                </div>
                <div class="session-detail-points">
                    +${durationMinutes} pts
                </div>
                <div class="session-detail-date">
                    ${this.formatDate(startDate)}
                </div>
            </div>
        `;
    },

    /**
     * Format time (HH:MM)
     * @param {Date} date
     * @returns {string}
     */
    formatTime(date) {
        return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    },

    /**
     * Format date
     * @param {Date} date
     * @returns {string}
     */
    formatDate(date) {
        const now = new Date();
        const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

        if (diffDays === 0) {
            return `aujourd'hui`;
        } else if (diffDays === 1) {
            return 'hier';
        } else if (diffDays < 7) {
            return `il y a ${diffDays} jours`;
        } else {
            return date.toLocaleDateString('fr-FR', { 
                day: 'numeric', 
                month: 'long',
                year: 'numeric'
            });
        }
    },

    /**
     * Escape HTML
     * @param {string} text
     * @returns {string}
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};
