function geojsonBounds(feature) {
  const bounds = new maplibregl.LngLatBounds();
  const coords = feature.type === 'Feature' ? feature.geometry.coordinates : feature.coordinates;
  (function expand(c) {
    if (typeof c[0] === 'number') {
      bounds.extend(c);
    } else {
      c.forEach(expand);
    }
  })(coords);
  return bounds;
}

document.addEventListener('DOMContentLoaded', async () => {
  const mapEl = document.getElementById('zone-map');
  if (!mapEl || typeof ZONE_ID === 'undefined') {
    console.error('Zone map element ou maplibre manquant');
    return;
  }

  const map = createBaseMap(mapEl, '_zoneMap', {
    // [lng, lat]
    center: [-7.0, 31.5],
    zoom: 5,
  });
  if (!map) return;

  map.on('load', async () => {
    try {
      const resp = await fetch(`/map/zones/${ZONE_ID}`);
      if (!resp.ok) throw new Error('failed');
      const data = await resp.json();

      if (data.geometry) {
        map.addSource('zone', { type: 'geojson', data: data.geometry });
        map.addLayer({
          id: 'zone-fill',
          type: 'fill',
          source: 'zone',
          paint: {
            'fill-color': data.color || '#3388ff',
            'fill-opacity': 0.4,
          },
        });
        map.addLayer({
          id: 'zone-outline',
          type: 'line',
          source: 'zone',
          paint: {
            'line-color': data.color || '#3388ff',
            'line-width': 2,
          },
        });
        map.fitBounds(geojsonBounds(data.geometry), { maxZoom: 14 });
      }

      if (data.parcels && data.parcels.features.length) {
        map.addSource('parcels', { type: 'geojson', data: data.parcels });
        map.addLayer({
          id: 'parcels-line',
          type: 'line',
          source: 'parcels',
          paint: {
            'line-color': '#666',
            'line-width': 1,
          },
        });

        if (data.is_available) {
          map.on('click', 'parcels-line', (e) => {
            const feature = e.features[0];
            const prop = feature.properties || {};
            if (!prop.is_free) return;
            const html = `
              <div>
                <h4 class="font-bold mb-1">${prop.name}</h4>
                <p>Surface: ${prop.area ?? ''}</p>
                <a href="/parcels/${feature.id}" class="text-blue-600">Réserver</a>
              </div>`;
            new maplibregl.Popup()
              .setLngLat(e.lngLat)
              .setHTML(html)
              .addTo(map);
          });
        }

        data.parcels.features.forEach((f) => {
          const prop = f.properties || {};
          if (prop.is_showroom) {
            const b = geojsonBounds(f);
            const center = b.getCenter();
            new maplibregl.Marker({ color: '#f87171' })
              .setLngLat(center)
              .addTo(map);
          }
        });
      }
    } catch (err) {
      console.error('Failed to load zone map', err);
    }
  });
});
