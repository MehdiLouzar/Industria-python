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

  const center = options.center || [31.5, -7.0];
  const zoom = options.zoom !== undefined ? options.zoom : 5;
  const map = new maplibregl.Map({
    container: el,
    style: options.style || '/static/vendor/maplibre-gl/style.json',
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

  return map;
}
