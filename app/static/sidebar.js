function initSidebar() {
  const sidebar = document.getElementById('sidebar');
  const openBtn = document.getElementById('sidebar-open');
  const closeBtn = document.getElementById('sidebar-close');
  const map = document.getElementById('map') || document.getElementById('zone-map');

  // Always ensure the map is visible when loading a new page
  if (map && map.classList.contains('hidden')) {
    map.classList.remove('hidden');
    if (window._industriaMap) window._industriaMap.invalidateSize();
    if (window._zoneMap) window._zoneMap.invalidateSize();
  }

  function hideMap() {
    if (map && window.innerWidth < 768) {
      map.classList.add('hidden');
    }
  }

  function showMap() {
    if (map && window.innerWidth < 768) {
      map.classList.remove('hidden');
      if (window._industriaMap) window._industriaMap.invalidateSize();
      if (window._zoneMap) window._zoneMap.invalidateSize();
    }
  }

  if (openBtn && sidebar) {
    openBtn.addEventListener('click', () => {
      sidebar.classList.remove('-translate-x-full');
      hideMap();
    });
  }
  if (closeBtn && sidebar) {
    closeBtn.addEventListener('click', () => {
      sidebar.classList.add('-translate-x-full');
      showMap();
    });
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initSidebar);
} else {
  initSidebar();
}
