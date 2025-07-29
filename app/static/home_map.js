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

  // Masquer l'indicateur de chargement
  const loadingEl = document.getElementById('map-loading');
  
  const moroccoBounds = [
    [-17.0, 20.0],
    [-0.5, 36.0]
  ];

  const map = createBaseMap(mapEl, '_industriaMap', {
    center: [-7.5, 31.5],
    zoom: 5.5,
    maxBounds: moroccoBounds,
  });
  
  if (!map) return;

  map.on('load', async () => {
    if (loadingEl) {
      loadingEl.style.display = 'none';
    }
    
    try {
      const resp = await fetch('/map/zones');
      if (!resp.ok) throw new Error('Échec du chargement des zones');
      const data = await resp.json();

      // Mettre à jour le compteur de zones
      const zoneCountEl = document.getElementById('zone-count');
      if (zoneCountEl) {
        zoneCountEl.textContent = data.features.length;
      }

      // Ajouter les zones
      map.addSource('zones', { type: 'geojson', data });
      
      // Couche de remplissage des zones avec couleur basée sur la disponibilité
      map.addLayer({
        id: 'zones-fill',
        type: 'fill',
        source: 'zones',
        paint: {
          'fill-color': [
            'case',
            ['get', 'is_available'],
            '#F59E0B', // Ambre pour les zones disponibles
            '#9CA3AF'  // Gris pour les zones non disponibles
          ],
          'fill-opacity': [
            'case',
            ['boolean', ['feature-state', 'hover'], false],
            0.6,
            0.4
          ]
        },
        filter: ['!=', '$type', 'Point']
      });
      
      // Contour des zones
      map.addLayer({
        id: 'zones-outline',
        type: 'line',
        source: 'zones',
        paint: {
          'line-color': [
            'case',
            ['get', 'is_available'],
            '#D97706', // Ambre foncé
            '#6B7280'  // Gris foncé
          ],
          'line-width': [
            'case',
            ['boolean', ['feature-state', 'hover'], false],
            3,
            2
          ]
        },
        filter: ['!=', '$type', 'Point']
      });

      // Charger les parcelles
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
              'line-color': '#4B5563',
              'line-width': 1,
              'line-opacity': 0.5
            },
            minzoom: 10 // Ne montrer les parcelles qu'à un zoom élevé
          });
        }
      } catch (pErr) {
        console.error('Error loading parcels', pErr);
      }

      // Créer les données pour le clustering
      const points = {
        type: 'FeatureCollection',
        features: data.features
          .filter(f => f.properties.centroid)
          .map(f => ({
            type: 'Feature',
            id: f.id,
            geometry: f.properties.centroid,
            properties: {
              name: f.properties.name,
              is_available: f.properties.is_available,
              zone_id: f.id
            }
          }))
      };

      // Ajouter la source avec clustering activé
      map.addSource('zones-points', {
        type: 'geojson',
        data: points,
        cluster: true,
        clusterMaxZoom: 14, // Max zoom pour voir les clusters
        clusterRadius: 60, // Rayon de regroupement en pixels
        clusterProperties: {
          // Compter les zones disponibles dans chaque cluster
          'available_count': ['+', ['case', ['get', 'is_available'], 1, 0]]
        }
      });

      // Layer pour les clusters
      map.addLayer({
        id: 'clusters',
        type: 'circle',
        source: 'zones-points',
        filter: ['has', 'point_count'],
        paint: {
          'circle-color': [
            'step',
            ['get', 'point_count'],
            '#51bbd6', // Bleu clair pour 2-5 zones
            5,
            '#f1f075', // Jaune pour 5-10 zones
            10,
            '#f28cb1'  // Rose pour 10+ zones
          ],
          'circle-radius': [
            'step',
            ['get', 'point_count'],
            25, // Taille pour 2-5 zones
            5,
            35, // Taille pour 5-10 zones
            10,
            45  // Taille pour 10+ zones
          ],
          'circle-stroke-width': 3,
          'circle-stroke-color': '#fff',
          'circle-stroke-opacity': 0.9
        }
      });

      // Labels pour les clusters
      map.addLayer({
        id: 'cluster-count',
        type: 'symbol',
        source: 'zones-points',
        filter: ['has', 'point_count'],
        layout: {
          'text-field': '{point_count_abbreviated}',
          'text-font': ['Arial Unicode MS Bold'],
          'text-size': 14
        },
        paint: {
          'text-color': '#000'
        }
      });

      // Sous-label pour les zones disponibles
      map.addLayer({
        id: 'cluster-available',
        type: 'symbol',
        source: 'zones-points',
        filter: ['all', 
          ['has', 'point_count'],
          ['>', ['get', 'available_count'], 0]
        ],
        layout: {
          'text-field': [
            'concat',
            ['to-string', ['get', 'available_count']],
            ' dispo'
          ],
          'text-font': ['Arial Unicode MS Regular'],
          'text-size': 11,
          'text-offset': [0, 1.5]
        },
        paint: {
          'text-color': '#059669'
        }
      });

      // Layer pour les points non-clusterisés (zones individuelles)
      const markers = [];
      let currentZoom = map.getZoom();

      function updateMarkers() {
        // Supprimer les anciens marqueurs
        markers.forEach(m => m.remove());
        markers.length = 0;

        // Obtenir les features visibles
        const features = map.querySourceFeatures('zones-points');
        
        // Créer des marqueurs uniquement pour les points non-clusterisés
        features.forEach(feature => {
          if (!feature.properties.cluster) {
            // Vérifier si un marqueur existe déjà pour cette zone
            if (!markers.find(m => m._element.dataset.zoneId === feature.properties.zone_id)) {
              const el = document.createElement('div');
              el.className = 'custom-marker';
              el.dataset.zoneId = feature.properties.zone_id;
              
              // Style du marqueur inspiré de Google Maps
              el.innerHTML = `
                <div class="marker-container">
                  <div class="marker-pin ${feature.properties.is_available ? 'available' : 'unavailable'}">
                    <div class="marker-icon">
                      <svg viewBox="0 0 24 24" fill="white" width="20" height="20">
                        <path d="M19 3H14.82C14.4 1.84 13.3 1 12 1S9.6 1.84 9.18 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM12 3C12.55 3 13 3.45 13 4S12.55 5 12 5 11 4.55 11 4 11.45 3 12 3ZM7 7H17V19H7V7Z"/>
                      </svg>
                    </div>
                  </div>
                  <div class="marker-label">${feature.properties.name}</div>
                  ${feature.properties.is_available ? '<div class="marker-pulse"></div>' : ''}
                </div>
              `;
              
              // Créer le marqueur
              const marker = new maplibregl.Marker({
                element: el,
                anchor: 'bottom'
              })
              .setLngLat(feature.geometry.coordinates)
              .addTo(map);
              
              // Ajouter l'interactivité
              el.addEventListener('click', (e) => {
                e.stopPropagation();
                showZoneDetails(feature.properties.zone_id, feature.geometry.coordinates);
              });
              
              el.addEventListener('mouseenter', () => {
                el.classList.add('hover');
                map.getCanvas().style.cursor = 'pointer';
              });
              
              el.addEventListener('mouseleave', () => {
                el.classList.remove('hover');
                map.getCanvas().style.cursor = '';
              });
              
              markers.push(marker);
            }
          }
        });
      }

      // Mettre à jour les marqueurs quand la carte bouge ou zoom
      map.on('moveend', updateMarkers);
      map.on('sourcedata', (e) => {
        if (e.sourceId === 'zones-points' && e.isSourceLoaded) {
          updateMarkers();
        }
      });

      // Clic sur un cluster pour zoomer
      map.on('click', 'clusters', (e) => {
        const features = map.queryRenderedFeatures(e.point, {
          layers: ['clusters']
        });
        const clusterId = features[0].properties.cluster_id;
        map.getSource('zones-points').getClusterExpansionZoom(
          clusterId,
          (err, zoom) => {
            if (err) return;

            map.easeTo({
              center: features[0].geometry.coordinates,
              zoom: zoom
            });
          }
        );
      });

      // Changer le curseur sur les clusters
      map.on('mouseenter', 'clusters', () => {
        map.getCanvas().style.cursor = 'pointer';
      });
      map.on('mouseleave', 'clusters', () => {
        map.getCanvas().style.cursor = '';
      });

      // Fonction pour afficher les détails d'une zone
      function showZoneDetails(id, lngLat) {
        fetch(`/map/zones/${id}`)
          .then(r => {
            if (!r.ok) throw new Error('load zone');
            return r.json();
          })
          .then(zone => {
            const availabilityBadge = zone.is_available 
              ? '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Disponible</span>'
              : '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">Complète</span>';
            
            const activitiesHtml = zone.activities && zone.activities.length 
              ? `<div class="mt-3">
                   <strong class="text-sm">Activités autorisées:</strong>
                   <div class="flex gap-2 mt-2 flex-wrap">
                     ${zone.activities.map(activity => 
                       `<div class="activity-icon" title="${activity.label || activity}">
                          ${activity.icon ? 
                            (activity.icon.startsWith('<') ? activity.icon : 
                             activity.icon.startsWith('http') ? `<img src="${activity.icon}" alt="${activity.label}" class="w-6 h-6">` :
                             `<img src="/static/${activity.icon}" alt="${activity.label}" class="w-6 h-6">`) 
                            : `<span class="activity-icon-placeholder">${(activity.label || activity).charAt(0).toUpperCase()}</span>`
                          }
                        </div>`
                     ).join('')}
                   </div>
                 </div>`
              : '';
            
            const actionLink = zone.is_available 
              ? `<a href="/zones/${zone.id}" class="inline-flex items-center mt-3 text-indigo-600 hover:text-indigo-800 font-medium">
                  Voir les détails 
                  <svg class="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </a>` 
              : '';
            
            const html = `
              <div style="min-width: 250px;">
                <div class="flex items-start justify-between mb-2">
                  <h3 class="font-bold text-lg">${zone.name}</h3>
                  ${availabilityBadge}
                </div>
                ${zone.description ? `<p class="text-gray-600 text-sm mb-2">${zone.description}</p>` : ''}
                <div class="text-sm">
                  <div><strong>Parcelles disponibles:</strong> ${zone.available_parcels ?? 0}</div>
                  ${activitiesHtml}
                </div>
                ${actionLink}
              </div>`;
            
            new maplibregl.Popup({
              closeButton: true,
              className: 'zone-popup'
            })
              .setLngLat(lngLat)
              .setHTML(html)
              .addTo(map);
          })
          .catch(e => console.error('Erreur chargement zone', e));
      }

      // Gérer les interactions avec les polygones aussi
      map.on('click', 'zones-fill', (e) => {
        const feature = e.features[0];
        showZoneDetails(feature.id, e.lngLat);
      });

      // Effet de survol sur les zones
      let hoveredZoneId = null;
      
      map.on('mouseenter', 'zones-fill', (e) => {
        if (hoveredZoneId !== null) {
          map.setFeatureState(
            { source: 'zones', id: hoveredZoneId },
            { hover: false }
          );
        }
        hoveredZoneId = e.features[0].id;
        map.setFeatureState(
          { source: 'zones', id: hoveredZoneId },
          { hover: true }
        );
        map.getCanvas().style.cursor = 'pointer';
      });
      
      map.on('mouseleave', 'zones-fill', () => {
        if (hoveredZoneId !== null) {
          map.setFeatureState(
            { source: 'zones', id: hoveredZoneId },
            { hover: false }
          );
        }
        hoveredZoneId = null;
        map.getCanvas().style.cursor = '';
      });

      // Ajuster la vue pour montrer toutes les zones
      if (data.features.length) {
        const bounds = new maplibregl.LngLatBounds();
        data.features.forEach(feature => {
          if (feature.geometry.type !== 'Point') {
            bounds.extend(geojsonBounds(feature));
          }
        });
        map.fitBounds(bounds, { 
          padding: 100,
          maxZoom: 7 
        });
      }

      // Initialiser les marqueurs
      updateMarkers();
      
    } catch (err) {
      console.error('Error loading zones', err);
      if (loadingEl) {
        loadingEl.innerHTML = '<div class="text-red-600">Erreur lors du chargement de la carte</div>';
      }
    }
  });
});

// Ajouter les styles CSS pour les marqueurs et clusters
const style = document.createElement('style');
style.textContent = `
  .custom-marker {
    cursor: pointer;
    transform-origin: bottom center;
    transition: transform 0.2s ease;
  }
  
  .custom-marker.hover {
    transform: scale(1.1);
    z-index: 1000;
  }
  
  .marker-container {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .marker-pin {
    width: 40px;
    height: 40px;
    background: #DC2626;
    border-radius: 50% 50% 50% 0;
    transform: rotate(-45deg);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    position: relative;
    transition: all 0.2s ease;
  }
  
  .marker-pin.available {
    background: #F59E0B;
  }
  
  .marker-pin.unavailable {
    background: #6B7280;
  }
  
  .marker-pin::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-top: 8px solid;
    border-top-color: inherit;
  }
  
  .marker-icon {
    transform: rotate(45deg);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .marker-label {
    margin-top: 15px;
    background: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    white-space: nowrap;
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .marker-pulse {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(45deg);
    width: 40px;
    height: 40px;
    border-radius: 50% 50% 50% 0;
    background: rgba(245, 158, 11, 0.4);
    animation: pulse 2s ease-out infinite;
    z-index: -1;
  }
  
  .marker-pin.unavailable .marker-pulse {
    background: rgba(107, 114, 128, 0.4);
    animation: none;
  }
  
  @keyframes pulse {
    0% {
      transform: translate(-50%, -50%) rotate(45deg) scale(1);
      opacity: 1;
    }
    100% {
      transform: translate(-50%, -50%) rotate(45deg) scale(2);
      opacity: 0;
    }
  }
  
  .zone-popup .maplibregl-popup-content {
    padding: 10px;
    border-radius: 12px;
    box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.2);
    width: 400px;
    height: auto;
    max-height: 300px;
  }
  
  .zone-popup .maplibregl-popup-close-button {
    font-size: 10px;
    padding: 5px;
    color: #6B7280;
  }
  
  .zone-popup .maplibregl-popup-close-button:hover {
    color: #374151;
    background-color: #F3F4F6;
  }
  
  .activity-icon {
    width: 32px;
    height: 32px;
    background: #F3F4F6;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
    border: 1px solid #E5E7EB;
    transition: all 0.2s ease;
  }
  
  .activity-icon:hover {
    background: #E5E7EB;
    transform: scale(1.1);
  }
  
  .activity-icon img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
  
  .activity-icon svg {
    width: 20px;
    height: 20px;
    fill: #374151;
  }
  
  .activity-icon-placeholder {
    font-weight: bold;
    color: #6B7280;
    font-size: 14px;
  }
`;
document.head.appendChild(style);