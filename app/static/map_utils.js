function disableTelemetry() {
  if (typeof mapboxgl !== 'undefined') {
    if (typeof mapboxgl.setTelemetryEnabled === 'function') {
      mapboxgl.setTelemetryEnabled(false);
    }
    if (mapboxgl.config) {
      mapboxgl.config.EVENTS_URL = null;
    }
  }
}

function createBaseMap(el, storeName, options = {}) {
  if (!el || typeof mapboxgl === 'undefined') {
    console.error('Map element or MapLibre missing');
    return null;
  }

  disableTelemetry();

  if (storeName && window[storeName]) {
    window[storeName].remove();
  }

  const leafletOpts = Object.assign({ worldCopyJump: true, maxZoom: 18 }, options.leaflet || {});
  const center = options.center || [31.5, -7.0];
  const zoom = options.zoom !== undefined ? options.zoom : 5;
  const map = L.map(el, leafletOpts).setView(center, zoom);

  if (storeName) {
    window[storeName] = map;
  }

  L.mapboxGL({
    style: options.style || 'https://demotiles.maplibre.org/style.json',
    gl: mapboxgl,
    renderWorldCopies: false,
  }).addTo(map);

  return map;
}
