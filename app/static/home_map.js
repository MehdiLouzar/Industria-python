document.addEventListener('DOMContentLoaded', async () => {
  const mapEl = document.getElementById('map');
  if (!mapEl || !window.MAPBOX_TOKEN) return;

  const map = L.map(mapEl).setView([31.5, -7.0], 6);

  L.mapboxGL({
    accessToken: MAPBOX_TOKEN,
    style: 'mapbox://styles/mapbox/streets-v12'
  }).addTo(map);

  const clusters = L.markerClusterGroup();

  try {
    const resp = await fetch('/map/zones');
    if (!resp.ok) throw new Error('failed');
    const data = await resp.json();
    L.geoJSON(data, {
      onEachFeature: (feature, layer) => {
        const name = feature.properties && feature.properties.name;
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
