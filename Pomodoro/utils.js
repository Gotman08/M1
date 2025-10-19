/**
 * Utility functions
 */
const Utils = {
    /**
     * Show points notification popup
     * @param {number} points - points earned
     * @param {string} message - optional custom message
     */
    showPointsNotification(points, message = null) {
        const notification = document.getElementById('points-notification');
        const text = document.getElementById('points-notification-text');
        
        if (!notification || !text) return;

        const displayText = message || `+${points} pts`;
        text.innerHTML = `⭐ ${displayText}`;

        // Show notification
        notification.classList.add('show');

        // Hide after 2 seconds
        setTimeout(() => {
            notification.classList.remove('show');
        }, 2000);
    },

    /**
     * Show achievement notification
     * @param {string} title - achievement title
     * @param {string} icon - achievement icon
     */
    showAchievementNotification(title, icon = '🏆') {
        const notification = document.getElementById('points-notification');
        const text = document.getElementById('points-notification-text');
        
        if (!notification || !text) return;

        text.innerHTML = `${icon} ${title}`;
        notification.classList.add('show', 'notification-achievement');

        setTimeout(() => {
            notification.classList.remove('show', 'notification-achievement');
        }, 2500);
    }
};
