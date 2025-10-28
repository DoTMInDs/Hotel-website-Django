const mobileMenu = document.getElementById('mobile-menu');
const navLinks = document.getElementById('nav-links');

mobileMenu.addEventListener('click', () => {
    console.log('clicked');
    mobileMenu.classList.toggle('change');
    navLinks.classList.toggle('showing');
});

// Enhanced Price Toggle with Modern Animation
const viewPrices = document.querySelectorAll('.view_price');

for (const viewPrice of viewPrices) {
    viewPrice.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        const button = e.currentTarget;
        const pk = button.dataset.pk;
        let priceTag = document.getElementById('priceTag-' + pk);
        
        if (priceTag) {
            const isVisible = priceTag.classList.contains('active-price-tag');
            
            if (isVisible) {
                // Hide price
                priceTag.classList.remove('active-price-tag');
                button.innerHTML = '<i class="fas fa-eye mr-1"></i>View Price';
                button.classList.remove('bg-gradient-to-r', 'from-emerald-500', 'to-green-600');
                button.classList.add('bg-gradient-to-r', 'from-rose-500', 'to-pink-600');
            } else {
                // Show price with animation
                priceTag.classList.add('active-price-tag');
                button.innerHTML = '<i class="fas fa-eye-slash mr-1"></i>Hide Price';
                button.classList.remove('bg-gradient-to-r', 'from-rose-500', 'to-pink-600');
                button.classList.add('bg-gradient-to-r', 'from-emerald-500', 'to-green-600');
            }
        }
    });
}
//------------- LOGIN-&-SIGN-UP-section----------------------//

// Toast Notification System
class ToastNotification {
    constructor() {
        this.container = document.getElementById('toast-container');
        this.toasts = [];
    }

    show(type, title, message, duration = 5000) {
        const toast = this.createToast(type, title, message);
        this.container.appendChild(toast);
        this.toasts.push(toast);

        // Show the toast
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);

        // Auto remove after duration
        setTimeout(() => {
            this.remove(toast);
        }, duration);

        return toast;
    }

    createToast(type, title, message) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || icons.info}</div>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="toastNotification.remove(this.parentElement)">×</button>
        `;

        return toast;
    }

    remove(toast) {
        if (toast && toast.parentElement) {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.parentElement.removeChild(toast);
                }
                this.toasts = this.toasts.filter(t => t !== toast);
            }, 300);
        }
    }

    success(title, message, duration) {
        return this.show('success', title, message, duration);
    }

    error(title, message, duration) {
        return this.show('error', title, message, duration);
    }

    warning(title, message, duration) {
        return this.show('warning', title, message, duration);
    }

    info(title, message, duration) {
        return this.show('info', title, message, duration);
    }
}

// Initialize toast notification system
const toastNotification = new ToastNotification();

// Make it globally available
window.toastNotification = toastNotification;

// Check for URL parameters to show payment notifications
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const paymentStatus = urlParams.get('payment_status');
    const paymentMessage = urlParams.get('payment_message');
    
    if (paymentStatus && paymentMessage) {
        if (paymentStatus === 'success') {
            toastNotification.success('Payment Successful!', paymentMessage, 8000);
        } else if (paymentStatus === 'error') {
            toastNotification.error('Payment Failed', paymentMessage, 8000);
        } else if (paymentStatus === 'warning') {
            toastNotification.warning('Payment Warning', paymentMessage, 8000);
        }
        
        // Clean up URL parameters
        const newUrl = window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);
    }
});
