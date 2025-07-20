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
    // [lng, lat]
    center: [-7.0, 31.5],
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
        },
        filter: ['!=', '$type', 'Point']
      });
      map.addLayer({
        id: 'zones-outline',
        type: 'line',
        source: 'zones',
        paint: {
          'line-color': '#3388ff',
          'line-width': 2,
        },
        filter: ['!=', '$type', 'Point']
      });

      // load parcels and draw their outlines
      try {
        const pResp = await fetch('/map/parcels');
        if (pResp.ok) {
          const pData = await pResp.json();
          map.addSource('parcels', { type: 'geojson', data: pData });
          map.addLayer({
            id: 'parcels-lines',
            type: 'line',
            source: 'parcels',
            paint: {
              'line-color': '#666',
              'line-width': 1,
            }
          });
        }
      } catch (pErr) {
        console.error('Error loading parcels', pErr);
      }

      const points = {
        type: 'FeatureCollection',
        features: data.features
          .filter(f => f.properties.centroid)
          .map(f => ({
            type: 'Feature',
            id: f.id,
            geometry: f.properties.centroid,
            properties: { name: f.properties.name }
          }))
      };
      map.addSource('zones-centroids', { type: 'geojson', data: points });
      map.addLayer({
        id: 'zones-points',
        type: 'circle',
        source: 'zones-centroids',
        paint: {
          'circle-radius': 6,
          'circle-color': '#3388ff'
        }
      });

      function showPopup(id, lngLat) {
        fetch(`/map/zones/${id}`)
          .then(r => {
            if (!r.ok) throw new Error('load zone');
            return r.json();
          })
          .then(zone => {
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
              .setLngLat(lngLat)
              .setHTML(html)
              .addTo(map);
          })
          .catch(e => console.error('Erreur chargement zone', e));
      }

      map.on('click', 'zones-fill', (e) => {
        const feature = e.features[0];
        showPopup(feature.id, e.lngLat);
      });
      map.on('click', 'zones-points', (e) => {
        const feature = e.features[0];
        showPopup(feature.id, e.lngLat);
      });

      if (data.features.length) {
        map.fitBounds(geojsonBounds(data), { maxZoom: 8 });
      }
    } catch (err) {
      console.error('Error loading zones', err);
    }
  });
});
