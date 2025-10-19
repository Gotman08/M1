/**
 * Goals module
 * Manages objectives with achievement-style circular progress and rewards
 */
const Goals = {
    elements: {
        list: null,
        nameInput: null,
        hoursInput: null,
        periodSelect: null,
        addBtn: null
    },

    // Predefined achievement-style goals with icons and rewards
    predefinedGoals: [
        { name: 'mon petit coeur', hours: 5, period: 'week', icon: '💝', reward: 50, desc: 'etudie 5h cette semaine' },
        { name: 'ma travailleuse', hours: 10, period: 'week', icon: '💖', reward: 100, desc: 'etudie 10h cette semaine' },
        { name: 'mon amour', hours: 20, period: 'month', icon: '💕', reward: 150, desc: 'etudie 20h ce mois' },
        { name: 'ma fierté', hours: 40, period: 'month', icon: '🌹', reward: 250, desc: 'etudie 40h ce mois' },
        { name: 'ma reine', hours: 60, period: 'month', icon: '👑', reward: 500, desc: 'etudie 60h ce mois' },
        { name: 'mon étoile', hours: 2, period: 'week', icon: '✨', reward: 30, desc: 'moyenne 2h/jour cette semaine' }
    ],

    /**
     * Initialize goals module
     */
    init() {
        this.elements.list = document.getElementById('goals-list');
        this.elements.nameInput = document.getElementById('goal-name');
        this.elements.hoursInput = document.getElementById('goal-hours');
        this.elements.periodSelect = document.getElementById('goal-period');
        this.elements.addBtn = document.getElementById('add-goal-btn');

        this.elements.addBtn.addEventListener('click', () => this.addGoal());
        
        // Toggle custom goal form
        const toggleBtn = document.getElementById('toggle-goal-form-btn');
        const customForm = document.getElementById('custom-goal-form');
        if (toggleBtn && customForm) {
            toggleBtn.addEventListener('click', () => {
                const isHidden = customForm.style.display === 'none';
                customForm.style.display = isHidden ? 'grid' : 'none';
                toggleBtn.textContent = isHidden ? '- cacher formulaire' : '+ creer objectif perso';
            });
        }
        
        this.initPredefinedGoals();
        this.render();
    },

    /**
     * Initialize predefined goals if not already created
     */
    initPredefinedGoals() {
        const goals = Storage.getGoals();
        
        // Add predefined goals if not already there
        this.predefinedGoals.forEach(predef => {
            const exists = goals.find(g => g.name === predef.name && g.period === predef.period);
            if (!exists) {
                const goal = {
                    id: Date.now() + Math.random(),
                    name: predef.name,
                    targetMinutes: predef.hours * 60,
                    period: predef.period,
                    icon: predef.icon,
                    reward: predef.reward,
                    desc: predef.desc,
                    claimed: false,
                    createdAt: new Date().toISOString()
                };
                goals.push(goal);
            }
        });
        
        Storage.setGoals(goals);
    },

    /**
     * Add a new goal
     */
    addGoal() {
        const name = this.elements.nameInput.value.trim();
        const hours = parseInt(this.elements.hoursInput.value);
        const period = this.elements.periodSelect.value;

        if (!name || !hours || hours <= 0) {
            alert('remplis tous les champs');
            return;
        }

        const goal = {
            id: Date.now(),
            name: name,
            targetMinutes: hours * 60,
            period: period,
            icon: '🎯',
            reward: hours * 10,
            desc: `objectif perso ${hours}h`,
            claimed: false,
            createdAt: new Date().toISOString()
        };

        const goals = Storage.getGoals();
        goals.push(goal);
        Storage.setGoals(goals);

        this.elements.nameInput.value = '';
        this.elements.hoursInput.value = '';

        this.render();
    },

    /**
     * Claim reward for completed goal
     * @param {number} goalId - goal id
     */
    claimReward(goalId) {
        const goals = Storage.getGoals();
        const goal = goals.find(g => g.id === goalId);
        
        if (!goal) return;
        
        const progress = this.getGoalProgress(goal);
        
        if (progress.percentage < 100) {
            alert('objectif pas encore atteint');
            return;
        }
        
        if (goal.claimed) {
            alert('recompense deja reclamee');
            return;
        }
        
        // Award points
        if (typeof Rewards !== 'undefined') {
            Rewards.addPoints(goal.reward);
        }
        
        goal.claimed = true;
        Storage.setGoals(goals);
        
        // Show notification
        if (typeof Utils !== 'undefined') {
            Utils.showPointsNotification(goal.reward, `objectif ${goal.name} +${goal.reward} pts`);
        }
        
        this.render();
    },

    /**
     * Delete a goal
     * @param {number} goalId - goal id
     */
    deleteGoal(goalId) {
        const goals = Storage.getGoals().filter(g => g.id !== goalId);
        Storage.setGoals(goals);
        this.render();
    },

    /**
     * Get progress for a goal
     * @param {Object} goal - goal object
     * @returns {Object} progress data with current and percentage
     */
    getGoalProgress(goal) {
        const startDate = this.getStartDate(goal.period);
        const currentMinutes = Sessions.getTotalMinutes(startDate);
        const percentage = Math.min((currentMinutes / goal.targetMinutes) * 100, 100);

        return {
            current: currentMinutes,
            target: goal.targetMinutes,
            percentage: percentage
        };
    },

    /**
     * Get start date for period
     * @param {string} period - 'week' or 'month'
     * @returns {Date} start date
     */
    getStartDate(period) {
        const now = new Date();
        
        if (period === 'week') {
            const day = now.getDay();
            const diff = day === 0 ? 6 : day - 1;
            const monday = new Date(now);
            monday.setDate(now.getDate() - diff);
            monday.setHours(0, 0, 0, 0);
            return monday;
        } else if (period === 'month') {
            return new Date(now.getFullYear(), now.getMonth(), 1);
        }
        
        return new Date(0);
    },

    /**
     * Update progress for all goals (called after session)
     */
    updateProgress() {
        this.render();
    },

    /**
     * Render all goals
     */
    render() {
        const goals = Storage.getGoals();

        if (goals.length === 0) {
            this.elements.list.innerHTML = '<p class="empty-state">pas d\'objectif encore</p>';
            return;
        }

        // Render as achievement circles
        this.elements.list.innerHTML = `
            <div class="achievements-grid">
                ${goals.map(goal => this.renderAchievementCircle(goal)).join('')}
            </div>
        `;
    },

    /**
     * Render a single goal as achievement circle
     * @param {Object} goal - goal object
     * @returns {string} HTML string
     */
    renderAchievementCircle(goal) {
        const progress = this.getGoalProgress(goal);
        const percentage = Math.min(progress.percentage, 100);
        const currentHours = (progress.current / 60).toFixed(1);
        const targetHours = (progress.target / 60).toFixed(0);
        const periodText = goal.period === 'week' ? 'semaine' : 'mois';
        const isCompleted = percentage >= 100;
        const isClaimed = goal.claimed;
        
        // SVG circle calculation
        const radius = 45;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (percentage / 100) * circumference;
        
        const completedClass = isCompleted ? 'achievement-completed' : '';
        const claimedClass = isClaimed ? 'achievement-claimed' : '';

        return `
            <div class="achievement-circle ${completedClass} ${claimedClass}" 
                 onclick="${isCompleted && !isClaimed ? `Goals.claimReward(${goal.id})` : ''}"
                 style="cursor: ${isCompleted && !isClaimed ? 'pointer' : 'default'}">
                <svg class="progress-ring" width="120" height="120">
                    <circle class="progress-ring-bg" cx="60" cy="60" r="${radius}" />
                    <circle class="progress-ring-fill" 
                            cx="60" cy="60" r="${radius}"
                            style="stroke-dasharray: ${circumference}; stroke-dashoffset: ${offset}" />
                </svg>
                <div class="achievement-content">
                    <div class="achievement-icon">${goal.icon || '🎯'}</div>
                    <div class="achievement-name">${this.escapeHtml(goal.name)}</div>
                    <div class="achievement-progress">${Math.round(percentage)}%</div>
                    ${isCompleted && !isClaimed ? '<div class="achievement-claim">click reclamer</div>' : ''}
                    ${isClaimed ? '<div class="achievement-claimed-badge">✓</div>' : ''}
                </div>
                <div class="achievement-details">
                    <div class="achievement-desc">${goal.desc || `${targetHours}h / ${periodText}`}</div>
                    <div class="achievement-reward">🏆 ${goal.reward || 0} pts</div>
                    <div class="achievement-stats">${currentHours}h / ${targetHours}h</div>
                </div>
            </div>
        `;
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
