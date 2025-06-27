// static/js/home_map.js
document.addEventListener('DOMContentLoaded', async () => {
  const mapEl = document.getElementById('map');
  if (!mapEl || !window.MAPBOX_TOKEN || !window.mapboxgl) {
    console.error('Map element, token ou mapboxgl manquant');
    return;
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
  }).setView([31.5, -7.0], 6);

  // Ajout du calque Mapbox GL, sans répéter le monde
  L.mapboxGL({
    accessToken: MAPBOX_TOKEN,
    style: 'mapbox://styles/mapbox/streets-v12',
    gl: mapboxgl,
    // Désactive le rendu de copies multiples du monde
    renderWorldCopies: false
  }).addTo(map);

  // Clustering et chargement des zones
  const clusters = L.markerClusterGroup();

  try {
    const resp = await fetch('/map/zones');
    if (!resp.ok) throw new Error('Échec du chargement des zones');
    const data = await resp.json();

    L.geoJSON(data, {
      onEachFeature: (feature, layer) => {
        const name = feature.properties?.name;
        if (name) layer.bindPopup(name);
      }
    }).eachLayer(l => clusters.addLayer(l));

    map.addLayer(clusters);

    if (clusters.getLayers().length) {
      map.fitBounds(clusters.getBounds(), { maxZoom: 12 });
    }
  } catch (err) {
    console.error('Error loading zones', err);
  }
});
