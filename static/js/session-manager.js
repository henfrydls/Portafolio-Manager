/**
 * Session Management JavaScript
 * Handles session timeout warnings and automatic session extension
 */

class SessionManager {
    constructor(options = {}) {
        this.options = {
            checkInterval: 60000, // Check every minute
            warningTime: 300000, // Warn 5 minutes before expiry
            extendUrl: '/api/extend-session/',
            statusUrl: '/api/session-status/',
            loginUrl: '/login/',
            ...options
        };
        
        this.warningShown = false;
        this.sessionData = null;
        this.checkTimer = null;
        
        this.init();
    }
    
    init() {
        // Only run on admin pages
        if (this.isAdminPage()) {
            this.startSessionCheck();
            this.bindEvents();
        }
    }
    
    isAdminPage() {
        return window.location.pathname.includes('admin') || 
               window.location.pathname.includes('dashboard') ||
               document.body.classList.contains('admin-page');
    }
    
    startSessionCheck() {
        this.checkSession();
        this.checkTimer = setInterval(() => {
            this.checkSession();
        }, this.options.checkInterval);
    }
    
    stopSessionCheck() {
        if (this.checkTimer) {
            clearInterval(this.checkTimer);
            this.checkTimer = null;
        }
    }
    
    async checkSession() {
        try {
            const response = await fetch(this.options.statusUrl, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error('Session check failed');
            }
            
            const data = await response.json();
            this.sessionData = data;
            
            if (!data.authenticated || data.session_expired) {
                this.handleSessionExpired();
                return;
            }
            
            // Check if session is about to expire
            if (data.session_age && data.session_age <= this.options.warningTime / 1000) {
                this.showSessionWarning(data.session_age);
            } else {
                this.hideSessionWarning();
            }
            
        } catch (error) {
            console.error('Session check error:', error);
            // Don't show warning on network errors, just log them
        }
    }
    
    showSessionWarning(secondsLeft) {
        if (this.warningShown) return;
        
        this.warningShown = true;
        const minutes = Math.ceil(secondsLeft / 60);
        
        const warningHtml = `
            <div id="session-warning" class="session-warning-banner">
                <div class="session-warning-content">
                    <span class="session-warning-icon">⚠️</span>
                    <span class="session-warning-text">
                        Tu sesión expirará en ${minutes} minuto${minutes !== 1 ? 's' : ''}
                    </span>
                    <div class="session-warning-actions">
                        <button id="extend-session-btn" class="btn-extend-session">
                            Extender Sesión
                        </button>
                        <button id="dismiss-warning-btn" class="btn-dismiss-warning">
                            ✕
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing warning
        this.hideSessionWarning();
        
        // Add warning to page
        document.body.insertAdjacentHTML('afterbegin', warningHtml);
        
        // Bind events
        document.getElementById('extend-session-btn').addEventListener('click', () => {
            this.extendSession();
        });
        
        document.getElementById('dismiss-warning-btn').addEventListener('click', () => {
            this.hideSessionWarning();
        });
    }
    
    hideSessionWarning() {
        const warning = document.getElementById('session-warning');
        if (warning) {
            warning.remove();
        }
        this.warningShown = false;
    }
    
    async extendSession() {
        try {
            const response = await fetch(this.options.extendUrl, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error('Session extension failed');
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.hideSessionWarning();
                this.showSuccessMessage('Sesión extendida correctamente');
            } else {
                throw new Error(data.error || 'Session extension failed');
            }
            
        } catch (error) {
            console.error('Session extension error:', error);
            this.showErrorMessage('Error al extender la sesión');
        }
    }
    
    handleSessionExpired() {
        this.stopSessionCheck();
        this.showSessionExpiredModal();
    }
    
    showSessionExpiredModal() {
        const modalHtml = `
            <div id="session-expired-modal" class="session-modal-overlay">
                <div class="session-modal">
                    <div class="session-modal-header">
                        <h3>Sesión Expirada</h3>
                    </div>
                    <div class="session-modal-body">
                        <p>Tu sesión ha expirado por seguridad. Por favor, inicia sesión nuevamente.</p>
                    </div>
                    <div class="session-modal-footer">
                        <button id="login-again-btn" class="btn-login-again">
                            Iniciar Sesión
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        document.getElementById('login-again-btn').addEventListener('click', () => {
            window.location.href = this.options.loginUrl;
        });
    }
    
    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }
    
    showErrorMessage(message) {
        this.showMessage(message, 'error');
    }
    
    showMessage(message, type = 'info') {
        const messageHtml = `
            <div class="session-message session-message-${type}">
                ${message}
            </div>
        `;
        
        document.body.insertAdjacentHTML('afterbegin', messageHtml);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            const messageEl = document.querySelector('.session-message');
            if (messageEl) {
                messageEl.remove();
            }
        }, 3000);
    }
    
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        // Fallback: try to get from meta tag
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.getAttribute('content');
        }
        
        // Fallback: try to get from form
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            return csrfInput.value;
        }
        
        return '';
    }
    
    bindEvents() {
        // Extend session on user activity
        const activityEvents = ['click', 'keypress', 'scroll', 'mousemove'];
        let lastActivity = Date.now();
        
        const handleActivity = () => {
            const now = Date.now();
            // Only extend if it's been more than 5 minutes since last activity
            if (now - lastActivity > 300000) {
                lastActivity = now;
                // Silently extend session on activity
                if (this.sessionData && this.sessionData.authenticated) {
                    this.extendSession();
                }
            }
        };
        
        activityEvents.forEach(event => {
            document.addEventListener(event, handleActivity, { passive: true });
        });
        
        // Handle page visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                // Check session when page becomes visible
                this.checkSession();
            }
        });
    }
}

// CSS styles for session management
const sessionStyles = `
<style>
.session-warning-banner {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #ff9a56 0%, #ff6b6b 100%);
    color: white;
    z-index: 10000;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    animation: slideDown 0.3s ease-out;
}

.session-warning-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.session-warning-icon {
    font-size: 1.2rem;
    margin-right: 0.5rem;
}

.session-warning-text {
    flex: 1;
    font-weight: 500;
}

.session-warning-actions {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

.btn-extend-session {
    background: rgba(255,255,255,0.2);
    color: white;
    border: 1px solid rgba(255,255,255,0.3);
    padding: 0.5rem 1rem;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background-color 0.3s ease;
}

.btn-extend-session:hover {
    background: rgba(255,255,255,0.3);
}

.btn-dismiss-warning {
    background: none;
    border: none;
    color: white;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0.25rem;
    opacity: 0.7;
    transition: opacity 0.3s ease;
}

.btn-dismiss-warning:hover {
    opacity: 1;
}

.session-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10001;
    animation: fadeIn 0.3s ease-out;
}

.session-modal {
    background: white;
    border-radius: 10px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    max-width: 400px;
    width: 90%;
    animation: scaleIn 0.3s ease-out;
}

.session-modal-header {
    padding: 1.5rem 1.5rem 0;
    border-bottom: 1px solid #eee;
}

.session-modal-header h3 {
    margin: 0;
    color: #333;
    font-size: 1.3rem;
}

.session-modal-body {
    padding: 1.5rem;
    color: #666;
    line-height: 1.5;
}

.session-modal-footer {
    padding: 0 1.5rem 1.5rem;
    text-align: right;
}

.btn-login-again {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 5px;
    cursor: pointer;
    font-weight: 500;
    transition: transform 0.2s ease;
}

.btn-login-again:hover {
    transform: translateY(-1px);
}

.session-message {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    border-radius: 5px;
    color: white;
    font-weight: 500;
    z-index: 10002;
    animation: slideInRight 0.3s ease-out;
}

.session-message-success {
    background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
}

.session-message-error {
    background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
}

@keyframes slideDown {
    from { transform: translateY(-100%); }
    to { transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes scaleIn {
    from { transform: scale(0.9); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

@keyframes slideInRight {
    from { transform: translateX(100%); }
    to { transform: translateX(0); }
}

@media (max-width: 768px) {
    .session-warning-content {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
    }
    
    .session-warning-actions {
        justify-content: center;
    }
    
    .session-message {
        top: 10px;
        right: 10px;
        left: 10px;
        text-align: center;
    }
}
</style>
`;

// Add styles to document
document.head.insertAdjacentHTML('beforeend', sessionStyles);

// Initialize session manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.sessionManager = new SessionManager();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SessionManager;
}