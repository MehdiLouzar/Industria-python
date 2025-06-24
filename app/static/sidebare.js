// static/js/sidebar.js
document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('sidebar');
  const toggle  = document.getElementById('sidebarToggle');
  const iconOpen  = document.getElementById('icon-open');
  const iconClose = document.getElementById('icon-close');

  toggle.addEventListener('click', () => {
    // cache / montre la sidebar
    sidebar.classList.toggle('-translate-x-full');
    // switch icônes
    iconOpen.classList.toggle('hidden');
    iconClose.classList.toggle('hidden');
  });
});
