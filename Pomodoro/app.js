/**
 * Main application module
 * Coordinates all modules and handles tab navigation and session flow
 */
const App = {
    currentSession: {
        name: '',
        description: ''
    },

    /**
     * Initialize the application
     */
    init() {
        this.initModules();
        this.setupTabs();
        this.setupSessionFlow();
        this.checkExistingSession();
    },

    /**
     * Check if there's an existing study session
     */
    checkExistingSession() {
        const currentSession = Storage.getCurrentStudySession();
        const continueOption = document.getElementById('continue-session-option');
        const newSessionForm = document.getElementById('new-session-form');
        
        if (currentSession) {
            // Show option to continue
            continueOption.style.display = 'block';
            newSessionForm.style.display = 'none';
            
            // Display existing session info
            document.getElementById('existing-session-name').textContent = currentSession.name;
            document.getElementById('existing-session-desc').textContent = currentSession.description || '';
            
            // Calculate stats for this session
            const sessions = Storage.getSessions();
            const relatedSessions = sessions.filter(s => s.sessionName === currentSession.name);
            const totalMinutes = relatedSessions.reduce((sum, s) => sum + Math.floor(s.duration / 60), 0);
            const pomodoroCount = relatedSessions.length;
            
            document.getElementById('existing-session-stats').innerHTML = 
                `🍅 ${pomodoroCount} pomodoros · ⏱️ ${totalMinutes} min · ⭐ ${totalMinutes} pts`;
        } else {
            // Show new session form
            continueOption.style.display = 'none';
            newSessionForm.style.display = 'flex';
        }
    },

    /**
     * Initialize all modules
     */
    initModules() {
        Timer.init();
        Sessions.init();
        Stats.init();
        History.init();
        Rewards.init();
        Goals.init();
    },

    /**
     * Set up session creation flow
     */
    setupSessionFlow() {
        const setupScreen = document.getElementById('session-setup-screen');
        const mainContent = document.getElementById('main-app-content');
        const startSessionBtn = document.getElementById('start-session-btn');
        const continueSessionBtn = document.getElementById('continue-session-btn');
        const createNewSessionBtn = document.getElementById('create-new-session-btn');
        const newSessionBtn = document.getElementById('new-session-btn');
        const endSessionBtn = document.getElementById('end-session-btn');
        const setupNameInput = document.getElementById('setup-session-name');
        const setupDescInput = document.getElementById('setup-session-desc');
        const continueOption = document.getElementById('continue-session-option');
        const newSessionForm = document.getElementById('new-session-form');

        if (!startSessionBtn) {
            console.error('start session button not found');
            return;
        }

        // NOTE: continue existing session
        if (continueSessionBtn) {
            continueSessionBtn.addEventListener('click', () => {
                const currentSession = Storage.getCurrentStudySession();
                if (currentSession) {
                    this.currentSession = currentSession;
                    
                    // Update display
                    document.getElementById('current-session-name').textContent = currentSession.name;
                    document.getElementById('current-session-desc').textContent = currentSession.description || '';
                    
                    // Show main app
                    setupScreen.style.display = 'none';
                    mainContent.style.display = 'block';

                    // Enable all tabs immediately
                    this.enableAllTabs();
                }
            });
        }

        // NOTE: show form to create new session
        if (createNewSessionBtn) {
            createNewSessionBtn.addEventListener('click', () => {
                continueOption.style.display = 'none';
                newSessionForm.style.display = 'flex';
            });
        }

        // NOTE: start new session
        startSessionBtn.addEventListener('click', () => {
            const name = setupNameInput.value.trim();
            const desc = setupDescInput.value.trim();

            if (!name) {
                alert('entre un nom pour la session');
                return;
            }

            // Prevent multiple clicks
            startSessionBtn.disabled = true;

            this.currentSession.name = name;
            this.currentSession.description = desc;
            this.currentSession.startedAt = new Date().toISOString();
            this.currentSession.id = Date.now();
            this.currentSession.isActive = true;

            // Save to storage
            Storage.setCurrentStudySession(this.currentSession);
            Storage.addStudySession(this.currentSession);

            // Update current session display
            document.getElementById('current-session-name').textContent = name;
            document.getElementById('current-session-desc').textContent = desc;

            // Show main app
            setupScreen.style.display = 'none';
            mainContent.style.display = 'block';

            // Enable all tabs immediately
            this.enableAllTabs();

            // Clear inputs
            setupNameInput.value = '';
            setupDescInput.value = '';

            // Re-enable button for next time
            setTimeout(() => {
                startSessionBtn.disabled = false;
            }, 1000);

            // Refresh history
            if (typeof History !== 'undefined') {
                History.render();
            }
        });

        if (!newSessionBtn) {
            console.error('new session button not found');
            return;
        }

        // NOTE: create new session (reset flow)
        newSessionBtn.addEventListener('click', () => {
            if (Timer.isRunning) {
                if (!confirm('une session est en cours arreter et creer nouvelle session ?')) {
                    return;
                }
                Timer.stop();
            }

            // Show setup screen
            setupScreen.style.display = 'block';
            mainContent.style.display = 'none';
            
            // Check if we should show continue option or new form
            this.checkExistingSession();

            // Disable tabs again
            const rewardsTab = document.querySelector('[data-tab="rewards"]');
            const goalsTab = document.querySelector('[data-tab="goals"]');
            if (rewardsTab) rewardsTab.disabled = true;
            if (goalsTab) goalsTab.disabled = true;

            // Switch to stats tab
            this.switchToTab('stats');
        });

        // NOTE: end current session permanently
        if (endSessionBtn) {
            endSessionBtn.addEventListener('click', () => {
                if (!confirm('terminer definitivement cette session d\'etude ?')) {
                    return;
                }

                if (Timer.isRunning) {
                    Timer.stop();
                }

                // Mark session as ended
                if (this.currentSession.id) {
                    Storage.updateStudySession(this.currentSession.id, {
                        isActive: false,
                        endedAt: new Date().toISOString()
                    });
                }

                // Clear current session
                this.currentSession.name = '';
                this.currentSession.description = '';
                Storage.setCurrentStudySession(null);

                // Refresh history
                if (typeof History !== 'undefined') {
                    History.render();
                }

                // Show setup screen
                setupScreen.style.display = 'block';
                mainContent.style.display = 'none';

                // Show new session form
                continueOption.style.display = 'none';
                newSessionForm.style.display = 'flex';

                // Disable tabs
                const rewardsTab = document.querySelector('[data-tab="rewards"]');
                const goalsTab = document.querySelector('[data-tab="goals"]');
                if (rewardsTab) rewardsTab.disabled = true;
                if (goalsTab) goalsTab.disabled = true;
            });
        }
    },

    /**
     * Enable rewards and goals tabs (called when timer starts)
     */
    enableAllTabs() {
        const rewardsTab = document.querySelector('[data-tab="rewards"]');
        const goalsTab = document.querySelector('[data-tab="goals"]');
        rewardsTab.disabled = false;
        goalsTab.disabled = false;
    },

    /**
     * Switch to a specific tab
     * @param {string} tabName - name of tab to switch to
     */
    switchToTab(tabName) {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => {
            content.classList.remove('active');
            content.style.display = 'none';
        });

        const targetButton = document.querySelector(`[data-tab="${tabName}"]`);
        const targetContent = document.getElementById(`${tabName}-tab`);

        if (targetButton && targetContent) {
            targetButton.classList.add('active');
            targetContent.classList.add('active');
            targetContent.style.display = 'block';
        }
    },

    /**
     * Set up tab navigation
     */
    setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                if (button.disabled) return;

                const targetTab = button.dataset.tab;

                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => {
                    content.classList.remove('active');
                    content.style.display = 'none';
                });

                button.classList.add('active');
                const targetElement = document.getElementById(`${targetTab}-tab`);
                if (targetElement) {
                    targetElement.classList.add('active');
                    targetElement.style.display = 'block';
                } else {
                    console.error('tab not found:', `${targetTab}-tab`);
                }
            });
        });
    }
};

// NOTE: initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
