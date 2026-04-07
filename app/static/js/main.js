/* SolarTrack — main JS */

// Sidebar toggle (mobile)
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', (e) => {
      if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }
});

// Global Chart.js defaults
if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#9ca3af';
  Chart.defaults.borderColor = '#374151';
  Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";
}

// Confirm delete
function confirmDelete(formId, itemName) {
  if (confirm(`Delete "${itemName}"? This cannot be undone.`)) {
    document.getElementById(formId).submit();
  }
}
