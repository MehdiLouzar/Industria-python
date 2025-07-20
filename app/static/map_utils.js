function disableTelemetry() {
  if (typeof maplibregl !== 'undefined') {
    if (typeof maplibregl.setTelemetryEnabled === 'function') {
      maplibregl.setTelemetryEnabled(false);
    }
    if (maplibregl.config) {
      maplibregl.config.EVENTS_URL = null;
    }
  }
}

function createBaseMap(el, storeName, options = {}) {
  if (!el || typeof maplibregl === 'undefined') {
    console.error('Map element or MapLibre missing');
    return null;
  }

  disableTelemetry();

  if (storeName && window[storeName]) {
    window[storeName].remove();
  }

  // Style par défaut avec des tuiles OpenStreetMap
  const defaultStyle = {
    version: 8,
    sources: {
      'osm-tiles': {
        type: 'raster',
        tiles: [
          'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
          'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
          'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png'
        ],
        tileSize: 256,
        attribution: '© OpenStreetMap contributors'
      }
    },
    layers: [
      {
        id: 'osm-tiles-layer',
        type: 'raster',
        source: 'osm-tiles',
        minzoom: 0,
        maxzoom: 19
      }
    ]
  };

  // center coordinates are [lng, lat]
  const center = options.center || [-7.0, 31.5];
  const zoom = options.zoom !== undefined ? options.zoom : 5;
  
  const map = new maplibregl.Map({
    container: el,
    style: options.style || defaultStyle,
    center: center,
    zoom: zoom,
    maxZoom: options.maxZoom !== undefined ? options.maxZoom : 18,
  });

  if (options.maxBounds) {
    map.setMaxBounds(options.maxBounds);
  }

  if (storeName) {
    window[storeName] = map;
  }

  // Ajout des contrôles de navigation
  map.addControl(new maplibregl.NavigationControl(), 'top-right');
  
  // Debug : log quand la carte est chargée
  map.on('load', () => {
    console.log('Carte chargée avec succès');
    // Forcer le redimensionnement après le chargement
    setTimeout(() => {
      map.resize();
    }, 100);
  });

  // Redimensionner quand la fenêtre change
  window.addEventListener('resize', () => {
    map.resize();
  });

  // Fix pour les problèmes de hauteur 0
  setTimeout(() => {
    const container = map.getContainer();
    if (container.offsetHeight === 0) {
      console.warn('Hauteur de carte à 0, tentative de correction...');
      // Forcer un recalcul de la mise en page
      container.style.display = 'none';
      container.offsetHeight; // Force reflow
      container.style.display = '';
      map.resize();
    }
  }, 200);

  return map;
}