/**
 * Pomodoro timer module
 * Handles timer state, start/stop/reset functionality with countdown
 */
const Timer = {
    startTime: null,
    remainingSeconds: 25 * 60,
    intervalId: null,
    isRunning: false,
    mode: 'work',
    workSessionCount: 0,
    lastPointMinute: 0,
    autoMode: false,

    DURATIONS: {
        work: 25 * 60,
        shortBreak: 5 * 60,
        longBreak: 15 * 60
    },

    elements: {
        display: null,
        startBtn: null,
        stopBtn: null,
        skipBtn: null,
        resetBtn: null,
        sessionInfo: null,
        modeIndicator: null,
        sessionCounter: null,
        autoModeBtn: null
    },

    /**
     * Initialize timer with DOM elements
     */
    init() {
        this.elements.display = document.getElementById('timer-display');
        this.elements.startBtn = document.getElementById('start-btn');
        this.elements.stopBtn = document.getElementById('stop-btn');
        this.elements.skipBtn = document.getElementById('skip-btn');
        this.elements.resetBtn = document.getElementById('reset-btn');
        this.elements.sessionInfo = document.getElementById('session-info');
        this.elements.modeIndicator = document.getElementById('mode-indicator');
        this.elements.sessionCounter = document.getElementById('session-counter');
        this.elements.autoModeBtn = document.getElementById('auto-mode-btn');

        this.setupEventListeners();
        this.updateDisplay();
        this.updateModeDisplay();
        this.updateAutoModeBtn();
    },

    /**
     * Set up button click handlers
     */
    setupEventListeners() {
        this.elements.startBtn.addEventListener('click', () => this.start());
        this.elements.stopBtn.addEventListener('click', () => this.stop());
        this.elements.skipBtn.addEventListener('click', () => this.skip());
        this.elements.resetBtn.addEventListener('click', () => this.reset());
        this.elements.autoModeBtn.addEventListener('click', () => this.toggleAutoMode());
    },

    /**
     * Start the timer
     */
    start() {
        if (this.isRunning) return;

        this.startTime = new Date();
        this.isRunning = true;
        this.lastPointMinute = 0; // Track last minute for point award

        // Enable all tabs when timer starts
        if (typeof App !== 'undefined') {
            App.enableAllTabs();
        }

        this.intervalId = setInterval(() => {
            this.remainingSeconds--;
            this.updateDisplay();

            // Award points every minute in real-time
            const elapsedSeconds = this.DURATIONS[this.mode] - this.remainingSeconds;
            const currentMinute = Math.floor(elapsedSeconds / 60);
            
            if (this.mode === 'work' && currentMinute > this.lastPointMinute) {
                this.lastPointMinute = currentMinute;
                
                // Award 1 point per minute
                if (typeof Rewards !== 'undefined') {
                    Rewards.addPoints(1);
                }
            }

            if (this.remainingSeconds <= 0) {
                this.complete();
            }
        }, 1000);

        this.elements.startBtn.disabled = true;
        this.elements.stopBtn.disabled = false;
        this.updateSessionInfo();
    },

    /**
     * Stop the timer and save session (only for work mode)
     */
    stop() {
        if (!this.isRunning) return;

        this.isRunning = false;
        clearInterval(this.intervalId);

        const endTime = new Date();
        const totalDuration = this.DURATIONS[this.mode];
        const elapsedSeconds = totalDuration - this.remainingSeconds;
        const durationMinutes = Math.floor(elapsedSeconds / 60);

        if (this.mode === 'work' && durationMinutes > 0) {
            const session = {
                startTime: this.startTime.toISOString(),
                endTime: endTime.toISOString(),
                duration: elapsedSeconds,
                sessionName: (typeof App !== 'undefined' && App.currentSession) ? App.currentSession.name : '',
                sessionDescription: (typeof App !== 'undefined' && App.currentSession) ? App.currentSession.description : '',
                tags: [],
                note: ''
            };

            if (typeof Sessions !== 'undefined') {
                Sessions.saveSession(session);
            }

            // Points already added in real-time, no need to add here
            // Just check for badges
            if (typeof Rewards !== 'undefined') {
                Rewards.checkBadges();
            }

            if (typeof Stats !== 'undefined') {
                Stats.render();
            }

            if (typeof History !== 'undefined') {
                History.render();
            }
        }

        this.elements.startBtn.disabled = false;
        this.elements.stopBtn.disabled = true;
        this.elements.sessionInfo.style.display = 'none';
    },

    /**
     * Skip to next phase (work -> break or break -> work)
     */
    skip() {
        if (this.isRunning) {
            this.stop();
        }

        if (this.mode === 'work') {
            this.workSessionCount++;
            this.switchToBreak();
        } else {
            this.switchToWork();
        }
    },

    /**
     * Complete a timer cycle (work or break)
     */
    complete() {
        this.isRunning = false;
        clearInterval(this.intervalId);

        const endTime = new Date();
        const elapsedSeconds = this.DURATIONS[this.mode];
        const durationMinutes = Math.floor(elapsedSeconds / 60);

        if (this.mode === 'work') {
            this.workSessionCount++;

            const session = {
                startTime: this.startTime.toISOString(),
                endTime: endTime.toISOString(),
                duration: elapsedSeconds,
                sessionName: (typeof App !== 'undefined' && App.currentSession) ? App.currentSession.name : '',
                sessionDescription: (typeof App !== 'undefined' && App.currentSession) ? App.currentSession.description : '',
                tags: [],
                note: ''
            };

            if (typeof Sessions !== 'undefined') {
                Sessions.saveSession(session);
            }

            // Points already added in real-time, just check badges
            if (typeof Rewards !== 'undefined') {
                Rewards.checkBadges();
            }

            if (typeof Stats !== 'undefined') {
                Stats.render();
            }

            if (typeof History !== 'undefined') {
                History.render();
            }

            this.switchToBreak();
        } else {
            this.switchToWork();
        }

        this.playNotification();

        // Auto-start if auto mode enabled
        if (this.autoMode) {
            setTimeout(() => this.start(), 2000);
        }
    },

    /**
     * Switch to break mode (5min or 15min)
     */
    switchToBreak() {
        if (this.workSessionCount % 4 === 0) {
            this.mode = 'longBreak';
            alert('bravo 25min terminees pause 15min');
        } else {
            this.mode = 'shortBreak';
            alert('bravo 25min terminees pause 5min');
        }

        this.remainingSeconds = this.DURATIONS[this.mode];
        this.updateDisplay();
        this.updateModeDisplay();
        this.updateSessionInfo();

        this.elements.startBtn.disabled = false;
        this.elements.stopBtn.disabled = true;
    },

    /**
     * Switch to work mode
     */
    switchToWork() {
        this.mode = 'work';
        alert('pause terminee retour au travail');
        
        this.remainingSeconds = this.DURATIONS.work;
        this.updateDisplay();
        this.updateModeDisplay();
        this.updateSessionInfo();

        this.elements.startBtn.disabled = false;
        this.elements.stopBtn.disabled = true;
    },

    /**
     * Reset timer to current mode default
     */
    reset() {
        if (this.isRunning) {
            this.stop();
        }

        this.remainingSeconds = this.DURATIONS[this.mode];
        this.startTime = null;
        this.lastPointMinute = 0;
        this.updateDisplay();
        this.elements.sessionInfo.style.display = 'none';
    },

    /**
     * Update timer display (countdown)
     */
    updateDisplay() {
        const minutes = Math.floor(this.remainingSeconds / 60);
        const seconds = this.remainingSeconds % 60;
        this.elements.display.textContent = 
            `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

        const color = this.mode === 'work' ? '#6366f1' : '#10b981';
        this.elements.display.style.color = color;
    },

    /**
     * Update mode indicator display
     */
    updateModeDisplay() {
        const modeLabel = this.elements.modeIndicator.querySelector('.mode-label');
        const sessionCounter = this.workSessionCount % 4;
        
        if (this.mode === 'work') {
            modeLabel.textContent = 'mode travail';
            modeLabel.style.color = '#6366f1';
        } else if (this.mode === 'shortBreak') {
            modeLabel.textContent = 'pause courte';
            modeLabel.style.color = '#10b981';
        } else {
            modeLabel.textContent = 'pause longue';
            modeLabel.style.color = '#10b981';
        }

        this.elements.sessionCounter.textContent = sessionCounter;
    },

    /**
     * Update session info display
     */
    updateSessionInfo() {
        if (this.isRunning) {
            const modeText = this.mode === 'work' ? 'travail' : 
                           this.mode === 'shortBreak' ? 'pause 5min' : 'pause 15min';
            this.elements.sessionInfo.innerHTML = `<p>session ${modeText} en cours</p>`;
            this.elements.sessionInfo.style.display = 'block';
        }
    },

    /**
     * Play notification sound (browser notification)
     */
    playNotification() {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('pomodoro', { body: 'session terminee' });
        }
    },

    /**
     * Get current elapsed time in minutes
     * @returns {number} minutes elapsed
     */
    getElapsedMinutes() {
        const totalDuration = this.DURATIONS[this.mode];
        return Math.floor((totalDuration - this.remainingSeconds) / 60);
    },

    /**
     * Toggle auto mode on/off
     */
    toggleAutoMode() {
        this.autoMode = !this.autoMode;
        this.updateAutoModeBtn();
    },

    /**
     * Update auto mode button display
     */
    updateAutoModeBtn() {
        if (this.autoMode) {
            this.elements.autoModeBtn.textContent = 'auto on';
            this.elements.autoModeBtn.classList.add('active');
        } else {
            this.elements.autoModeBtn.textContent = 'auto off';
            this.elements.autoModeBtn.classList.remove('active');
        }
    }
};
