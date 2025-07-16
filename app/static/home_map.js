// static/js/home_map.js
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
  const mapEl = document.getElementById('map');
  if (!mapEl) {
    console.error('Map element ou maplibre manquant');
    return;
  }

  const moroccoBounds = [
    [-17.0, 20.0],
    [-0.5, 36.0]
  ];

  const map = createBaseMap(mapEl, '_industriaMap', {
    center: [31.5, -7.0],
    zoom: 5,
    maxBounds: moroccoBounds,
  });
  if (!map) return;

  map.on('load', async () => {
    try {
      const resp = await fetch('/map/zones');
      if (!resp.ok) throw new Error('Échec du chargement des zones');
      const data = await resp.json();

      map.addSource('zones', { type: 'geojson', data });
      map.addLayer({
        id: 'zones-fill',
        type: 'fill',
        source: 'zones',
        paint: {
          'fill-color': '#3388ff',
          'fill-opacity': 0.4,
        }
      });
      map.addLayer({
        id: 'zones-outline',
        type: 'line',
        source: 'zones',
        paint: {
          'line-color': '#3388ff',
          'line-width': 2,
        }
      });

      map.on('click', 'zones-fill', async (e) => {
        const feature = e.features[0];
        try {
          const zoneResp = await fetch(`/map/zones/${feature.id}`);
          if (!zoneResp.ok) throw new Error('load zone');
          const zone = await zoneResp.json();
          const link = zone.is_available ?
            `<a href="/zones/${zone.id}" class="text-blue-600">&rarr;</a>` : '';
          const html = `
            <div>
              <h3 class="font-bold mb-1">${zone.name}</h3>
              <p>${zone.description || ''}</p>
              <p>Parcelles disponibles: ${zone.available_parcels ?? 0}</p>
              <p>Activités: ${zone.activities.join(', ')}</p>
              ${link}
            </div>`;
          new maplibregl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(html)
            .addTo(map);
        } catch (e) {
          console.error('Erreur chargement zone', e);
        }
      });

      if (data.features.length) {
        map.fitBounds(geojsonBounds(data), { maxZoom: 8 });
      }
    } catch (err) {
      console.error('Error loading zones', err);
    }
  });
});
