document.addEventListener('DOMContentLoaded', function() {

    // 1. Auto-dismiss Django Alert Messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        // Safety check: ensure Bootstrap is loaded before calling its API
        if (typeof bootstrap !== 'undefined') {
            setTimeout(function() {
                try {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                } catch (e) {
                    // Fallback: hide manually if Bootstrap API fails
                    alert.style.display = 'none';
                }
            }, 5000);
        }
    });

    // 2. Initialize Bootstrap Tooltips
    // Added safety check to prevent errors if Bootstrap JS isn't ready
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl)
        });
    }

    // 3. Add smooth fade-in to main content areas
    const mainBlocks = document.querySelectorAll('.container');
    mainBlocks.forEach(block => {
        // Ensure the element is visible enough to animate
        block.style.opacity = "0";
        block.style.transition = "opacity 0.5s ease-in-out";

        // Trigger the fade-in after a micro-delay
        setTimeout(() => {
            block.style.opacity = "1";
            block.classList.add('fade-in');
        }, 10);
    });
});