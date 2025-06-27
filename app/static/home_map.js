// static/js/home_map.js
document.addEventListener('DOMContentLoaded', async () => {
  const mapEl = document.getElementById('map');
  if (!mapEl) {
    console.error('Map element ou maplibre manquant');
    return;
  }

  const moroccoBounds = [
    [20.0, -17.0],  // sud-ouest (lat, lon)
    [36.0, -0.5]    // nord-est (lat, lon)
  ];

  const map = createBaseMap(mapEl, '_industriaMap', {
    center: [31.5, -7.0],
    zoom: 5,
    leaflet: {
      worldCopyJump: true,
      maxBounds: moroccoBounds,
      maxBoundsViscosity: 1.0,
      maxZoom: 18,
    }
  });
  if (!map) return;

  // Clustering et chargement des zones
  const clusters = L.markerClusterGroup();

  try {
    const resp = await fetch('/map/zones');
    if (!resp.ok) throw new Error('Échec du chargement des zones');
    const data = await resp.json();

    L.geoJSON(data, {
      onEachFeature: (feature, layer) => {
        layer.on('click', async () => {
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
            layer.bindPopup(html).openPopup();
          } catch (e) {
            console.error('Erreur chargement zone', e);
          }
        });
      }
    }).eachLayer(l => clusters.addLayer(l));

    map.addLayer(clusters);

    if (clusters.getLayers().length) {
      map.fitBounds(clusters.getBounds(), { maxZoom: 8 });
    }
  } catch (err) {
    console.error('Error loading zones', err);
  }
});
