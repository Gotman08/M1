/**
 * Rewards module
 * Manages points, badges, and reward shop
 */
const Rewards = {
    elements: {
        totalPoints: null,
        badgesCount: null,
        badgesList: null,
        shopList: null
    },

    // FIXME: customize badges with personal achievements
    badges: [
        { id: 'first-session', name: 'mon étoile', desc: '1 session complete', icon: '✨', requirement: () => Sessions.getSessionCount() >= 1 },
        { id: 'week-warrior', name: 'ma courageuse', desc: '5 sessions en 1 semaine', icon: '💖', requirement: () => {
            const weekAgo = new Date();
            weekAgo.setDate(weekAgo.getDate() - 7);
            return Sessions.getSessionCount(weekAgo) >= 5;
        }},
        { id: 'marathoner', name: 'ma guerrière', desc: '10h total', icon: '⚔️', requirement: () => Sessions.getTotalMinutes() >= 600 },
        { id: 'dedicated', name: 'mon trésor', desc: '20 sessions total', icon: '💎', requirement: () => Sessions.getSessionCount() >= 20 },
        { id: 'champion', name: 'ma championne', desc: '30h total', icon: '🏆', requirement: () => Sessions.getTotalMinutes() >= 1800 },
        { id: 'legend', name: 'ma reine', desc: '50 sessions total', icon: '👑', requirement: () => Sessions.getSessionCount() >= 50 }
    ],

    // NOTE: customize shop items with personal rewards
    shopItems: [
        { id: 'message-1', name: 'je viens chez toi', desc: 'visite surprise', icon: '❤️', cost: 50 },
        { id: 'ubereats', name: 'ubereats offert', desc: 'je te paie un ubereats', icon: '🍔', cost: 100 },
        { id: 'massage', name: 'massage', desc: 'massage dos 10min', icon: '💆‍♀️', cost: 150 },
        { id: 'film', name: 'choix film', desc: 'tu choisis le film', icon: '🎬', cost: 120 },
        { id: 'restaurant', name: 'resto', desc: 'resto de ton choix', icon: '🍽️', cost: 300 },
        { id: 'surprise', name: 'surprise', desc: 'surprise speciale', icon: '🎁', cost: 500 }
    ],

    /**
     * Initialize rewards module
     */
    init() {
        this.elements.totalPoints = document.getElementById('total-points');
        this.elements.badgesCount = document.getElementById('badges-count');
        this.elements.badgesList = document.getElementById('badges-list');
        this.elements.shopList = document.getElementById('shop-list');

        this.checkBadges();
        this.render();
    },

    /**
     * Add points for completed study time
     * @param {number} minutes - minutes studied
     */
    addPoints(minutes) {
        const rewards = Storage.getRewards();
        rewards.totalPoints += minutes;
        Storage.setRewards(rewards);
        this.checkBadges();
        this.render();

        // Show notification
        if (typeof Utils !== 'undefined') {
            Utils.showPointsNotification(minutes);
        }
    },

    /**
     * Check and unlock badges
     */
    checkBadges() {
        const rewards = Storage.getRewards();
        let newBadges = false;

        this.badges.forEach(badge => {
            if (!rewards.badges.includes(badge.id) && badge.requirement()) {
                rewards.badges.push(badge.id);
                newBadges = true;

                // Show achievement notification
                if (typeof Utils !== 'undefined') {
                    Utils.showAchievementNotification(`badge ${badge.name} debloque`, badge.icon);
                }
            }
        });

        if (newBadges) {
            Storage.setRewards(rewards);
        }
    },

    /**
     * Claim a shop item
     * @param {string} itemId - shop item id
     */
    claimReward(itemId) {
        const rewards = Storage.getRewards();
        const item = this.shopItems.find(i => i.id === itemId);

        if (!item) return;

        if (rewards.totalPoints < item.cost) {
            alert('pas assez de points');
            return;
        }

        if (rewards.claimedRewards.includes(itemId)) {
            alert('deja reclame');
            return;
        }

        rewards.totalPoints -= item.cost;
        rewards.claimedRewards.push(itemId);
        Storage.setRewards(rewards);

        alert(`bravo tu as reclame: ${item.name}`);
        this.render();
    },

    /**
     * Render all rewards UI
     */
    render() {
        const rewards = Storage.getRewards();
        
        this.elements.totalPoints.textContent = rewards.totalPoints;
        this.elements.badgesCount.textContent = rewards.badges.length;

        this.renderBadges(rewards);
        this.renderShop(rewards);
    },

    /**
     * Render badges list
     * @param {Object} rewards - rewards data
     */
    renderBadges(rewards) {
        if (rewards.badges.length === 0) {
            this.elements.badgesList.innerHTML = '<p class="empty-state">pas de badge encore</p>';
            return;
        }

        const badgesHtml = this.badges.map(badge => {
            const unlocked = rewards.badges.includes(badge.id);
            const lockedClass = unlocked ? '' : 'badge-locked';
            
            return `
                <div class="badge-item ${lockedClass}">
                    <div class="badge-icon">${badge.icon}</div>
                    <div class="badge-name">${badge.name}</div>
                    <div class="badge-desc">${badge.desc}</div>
                </div>
            `;
        }).join('');

        this.elements.badgesList.innerHTML = badgesHtml;
    },

    /**
     * Render shop items
     * @param {Object} rewards - rewards data
     */
    renderShop(rewards) {
        const shopHtml = this.shopItems.map(item => {
            const claimed = rewards.claimedRewards.includes(item.id);
            const canAfford = rewards.totalPoints >= item.cost;
            const claimedClass = claimed ? 'shop-claimed' : '';
            
            return `
                <div class="shop-item ${claimedClass}">
                    <div class="shop-icon">${item.icon}</div>
                    <div class="shop-name">${item.name}</div>
                    <div class="shop-desc">${item.desc}</div>
                    <div class="shop-cost">${item.cost} pts</div>
                    <button 
                        class="shop-btn" 
                        onclick="Rewards.claimReward('${item.id}')"
                        ${!canAfford || claimed ? 'disabled' : ''}
                    >
                        ${claimed ? 'reclame' : 'acheter'}
                    </button>
                </div>
            `;
        }).join('');

        this.elements.shopList.innerHTML = shopHtml;
    },

    /**
     * Get date from one week ago
     * @returns {Date} date one week ago
     */
    getDateWeekAgo() {
        const date = new Date();
        date.setDate(date.getDate() - 7);
        return date;
    }
};
