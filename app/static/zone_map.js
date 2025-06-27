document.addEventListener('DOMContentLoaded', async () => {
  const mapEl = document.getElementById('zone-map');
  if (!mapEl || !window.mapboxgl || typeof ZONE_ID === 'undefined') {
    console.error('Zone map element ou maplibre manquant');
    return;
  }

  if (typeof mapboxgl.setTelemetryEnabled === 'function') {
    mapboxgl.setTelemetryEnabled(false);
  }
  if (mapboxgl.config) {
    mapboxgl.config.EVENTS_URL = null;
  }

  const map = L.map(mapEl, {
    worldCopyJump: true,
    maxZoom: 18
  }).setView([31.5, -7.0], 5);

  L.mapboxGL({
    style: 'https://demotiles.maplibre.org/style.json',
    gl: mapboxgl,
    renderWorldCopies: false,
  }).addTo(map);

  try {
    const resp = await fetch(`/map/zones/${ZONE_ID}`);
    if (!resp.ok) throw new Error('failed');
    const data = await resp.json();

    if (data.geometry) {
      const zoneLayer = L.geoJSON(data.geometry, {
        style: {
          color: data.color || '#3388ff',
          fillColor: data.color || '#3388ff',
          weight: 2,
          fillOpacity: 0.4
        }
      }).addTo(map);
      map.fitBounds(zoneLayer.getBounds(), { maxZoom: 14 });
    }

    if (data.parcels && data.parcels.features.length) {
      L.geoJSON(data.parcels, {
        style: f => ({ color: '#666', weight: 1 }),
        onEachFeature: (feature, layer) => {
          const prop = feature.properties || {};
          if (prop.is_showroom) {
            const center = layer.getBounds().getCenter();
            L.marker(center, { icon: L.divIcon({ className: 'showroom-marker', html: 'S' }) }).addTo(map);
          }
          if (data.is_available && prop.is_free) {
            layer.on('click', () => {
              const html = `
                <div>
                  <h4 class="font-bold mb-1">${prop.name}</h4>
                  <p>Surface: ${prop.area ?? ''}</p>
                  <a href="/parcels/${feature.id}" class="text-blue-600">Réserver</a>
                </div>`;
              layer.bindPopup(html).openPopup();
            });
          }
        }
      }).addTo(map);
    }
  } catch (err) {
    console.error('Failed to load zone map', err);
  }
});
