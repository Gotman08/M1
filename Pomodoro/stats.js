/**
 * Statistics module
 * Displays detailed session statistics with name, description, time, and points
 */
const Stats = {
    elements: {
        list: null
    },

    /**
     * Initialize stats module
     */
    init() {
        this.elements.list = document.getElementById('stats-list');
        this.render();
    },

    /**
     * Render all session statistics
     */
    render() {
        const sessions = Storage.getSessions();

        if (sessions.length === 0) {
            this.elements.list.innerHTML = '<p class="empty-state">aucune session encore</p>';
            return;
        }

        this.elements.list.innerHTML = sessions.map(session => 
            this.renderStatItem(session)
        ).join('');
    },

    /**
     * Render a single stat item
     * @param {Object} session - session object
     * @returns {string} HTML string
     */
    renderStatItem(session) {
        const startDate = new Date(session.startTime);
        const endDate = new Date(session.endTime);
        const durationMinutes = Math.floor(session.duration / 60);
        const durationSeconds = session.duration % 60;
        const points = durationMinutes;

        const sessionName = session.sessionName || 'session sans nom';
        const sessionDesc = session.sessionDescription || '';

        return `
            <div class="stat-item card" style="margin-bottom: 15px; padding: 15px;">
                <div class="stat-header" style="margin-bottom: 10px;">
                    <h3 style="margin: 0 0 5px 0; color: #1e293b; font-size: 18px;">${this.escapeHtml(sessionName)}</h3>
                    ${sessionDesc ? `<p style="margin: 0; color: #64748b; font-size: 14px;">${this.escapeHtml(sessionDesc)}</p>` : ''}
                </div>
                
                <div class="stat-details" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px;">
                    <div class="stat-box" style="background: #f1f5f9; padding: 10px; border-radius: 8px;">
                        <div style="font-size: 12px; color: #64748b; margin-bottom: 5px;">duree</div>
                        <div style="font-size: 20px; font-weight: bold; color: #6366f1;">${durationMinutes}:${String(durationSeconds).padStart(2, '0')}</div>
                    </div>
                    
                    <div class="stat-box" style="background: #f1f5f9; padding: 10px; border-radius: 8px;">
                        <div style="font-size: 12px; color: #64748b; margin-bottom: 5px;">points</div>
                        <div style="font-size: 20px; font-weight: bold; color: #10b981;">+${points}</div>
                    </div>
                    
                    <div class="stat-box" style="background: #f1f5f9; padding: 10px; border-radius: 8px;">
                        <div style="font-size: 12px; color: #64748b; margin-bottom: 5px;">debut</div>
                        <div style="font-size: 14px; color: #1e293b;">${this.formatTime(startDate)}</div>
                    </div>
                    
                    <div class="stat-box" style="background: #f1f5f9; padding: 10px; border-radius: 8px;">
                        <div style="font-size: 12px; color: #64748b; margin-bottom: 5px;">fin</div>
                        <div style="font-size: 14px; color: #1e293b;">${this.formatTime(endDate)}</div>
                    </div>
                </div>
                
                <div class="stat-date" style="margin-top: 10px; font-size: 13px; color: #94a3b8;">
                    ${this.formatDate(startDate)}
                </div>
            </div>
        `;
    },

    /**
     * Format time for display (HH:MM)
     * @param {Date} date - date object
     * @returns {string} formatted time
     */
    formatTime(date) {
        return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
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
     * Escape HTML to prevent XSS
     * @param {string} text - text to escape
     * @returns {string} escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};
