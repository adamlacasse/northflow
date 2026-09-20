// Main JavaScript file

// Delegated confirmation handler for destructive actions.
// Any clickable element with a `data-confirm="<message>"` attribute will
// prompt the user with that message before its default action (e.g. a
// form submission) is allowed to proceed.
document.addEventListener('DOMContentLoaded', function () {
    document.body.addEventListener('click', function (event) {
        var trigger = event.target.closest('[data-confirm]');
        if (!trigger) {
            return;
        }

        var message = trigger.getAttribute('data-confirm') || 'Are you sure?';
        if (!window.confirm(message)) {
            event.preventDefault();
        }
    });
});
