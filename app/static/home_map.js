// static/js/home_map.js
document.addEventListener('DOMContentLoaded', async () => {
  const mapEl = document.getElementById('map');
  if (!mapEl || !window.mapboxgl) {
    console.error('Map element ou maplibre manquant');
    return;
  }

  // Désactive la télémétrie Mapbox pour éviter les requêtes events.mapbox.com
  if (typeof mapboxgl.setTelemetryEnabled === 'function') {
    mapboxgl.setTelemetryEnabled(false);
  }
  if (mapboxgl.config) {
    mapboxgl.config.EVENTS_URL = null;
  }

  // Définition des limites du Maroc pour verrouiller le cadrage
  const moroccoBounds = [
    [20.0, -17.0],  // sud-ouest (lat, lon)
    [36.0, -0.5]    // nord-est (lat, lon)
  ];

  // Initialisation de la carte Leaflet
  const map = L.map(mapEl, {
    // Empêche l'affichage de copies horizontales du monde
    // saute automatiquement à la copie principale
    worldCopyJump: true,
    maxBounds: moroccoBounds,      // limite le pannage au Maroc
    maxBoundsViscosity: 1.0,       // colle la vue à ces bornes
    maxZoom: 18
  }).setView([31.5, -7.0], 5);

  // Ajoute le calque MapLibre avec un style libre qui ne dépend pas du schéma
  // "mapbox://" afin d'éviter les erreurs de chargement
  L.mapboxGL({
    style: 'https://demotiles.maplibre.org/style.json',
    gl: mapboxgl,
    // Désactive le rendu de copies multiples du monde
    renderWorldCopies: false,
  }).addTo(map);

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
