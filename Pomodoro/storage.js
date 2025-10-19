/**
 * localStorage management module
 * Handles all data persistence for sessions, rewards, goals, and stats
 */
const Storage = {
    KEYS: {
        SESSIONS: 'pomodoro_sessions',
        STUDY_SESSIONS: 'pomodoro_study_sessions',
        REWARDS: 'pomodoro_rewards',
        GOALS: 'pomodoro_goals',
        STATS: 'pomodoro_stats',
        SHOP: 'pomodoro_shop',
        CURRENT_STUDY_SESSION: 'pomodoro_current_study_session'
    },

    /**
     * Get data from localStorage
     * @param {string} key - storage key
     * @param {*} defaultValue - default value if key doesn't exist
     * @returns {*} parsed data or default value
     */
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('error read storage:', error);
            return defaultValue;
        }
    },

    /**
     * Save data to localStorage
     * @param {string} key - storage key
     * @param {*} value - data to save
     */
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('error write storage:', error);
        }
    },

    /**
     * Get all study sessions
     * @returns {Array} array of session objects
     */
    getSessions() {
        return this.get(this.KEYS.SESSIONS, []);
    },

    /**
     * Save a new session
     * @param {Object} session - session object with startTime, endTime, duration, tags, note
     */
    addSession(session) {
        const sessions = this.getSessions();
        sessions.unshift(session);
        this.set(this.KEYS.SESSIONS, sessions);
    },

    /**
     * Get all study sessions (contexts like "révision maths")
     * @returns {Array} array of study session objects
     */
    getStudySessions() {
        return this.get(this.KEYS.STUDY_SESSIONS, []);
    },

    /**
     * Save a new study session
     * @param {Object} studySession - study session object
     */
    addStudySession(studySession) {
        const studySessions = this.getStudySessions();
        studySessions.unshift(studySession);
        this.set(this.KEYS.STUDY_SESSIONS, studySessions);
    },

    /**
     * Update a study session
     * @param {number} sessionId - session id
     * @param {Object} updates - fields to update
     */
    updateStudySession(sessionId, updates) {
        const studySessions = this.getStudySessions();
        const index = studySessions.findIndex(s => s.id === sessionId);
        if (index !== -1) {
            studySessions[index] = { ...studySessions[index], ...updates };
            this.set(this.KEYS.STUDY_SESSIONS, studySessions);
        }
    },

    /**
     * Get current active study session
     * @returns {Object|null} current study session or null
     */
    getCurrentStudySession() {
        return this.get(this.KEYS.CURRENT_STUDY_SESSION, null);
    },

    /**
     * Set current active study session
     * @param {Object|null} studySession - study session object or null
     */
    setCurrentStudySession(studySession) {
        this.set(this.KEYS.CURRENT_STUDY_SESSION, studySession);
    },

    /**
     * Get reward stats (points, badges)
     * @returns {Object} rewards data
     */
    getRewards() {
        return this.get(this.KEYS.REWARDS, {
            totalPoints: 0,
            badges: [],
            claimedRewards: []
        });
    },

    /**
     * Update rewards data
     * @param {Object} rewards - rewards object
     */
    setRewards(rewards) {
        this.set(this.KEYS.REWARDS, rewards);
    },

    /**
     * Get all goals
     * @returns {Array} array of goal objects
     */
    getGoals() {
        return this.get(this.KEYS.GOALS, []);
    },

    /**
     * Save goals
     * @param {Array} goals - array of goal objects
     */
    setGoals(goals) {
        this.set(this.KEYS.GOALS, goals);
    },

    /**
     * Get shop items (claimed status)
     * @returns {Array} array of shop items with claimed status
     */
    getShop() {
        return this.get(this.KEYS.SHOP, []);
    },

    /**
     * Update shop items
     * @param {Array} shop - array of shop items
     */
    setShop(shop) {
        this.set(this.KEYS.SHOP, shop);
    },

    /**
     * Clear all data (for testing)
     */
    clearAll() {
        Object.values(this.KEYS).forEach(key => {
            localStorage.removeItem(key);
        });
    }
};
