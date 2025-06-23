const CRUD_CONFIG = {
  countries: {
    display: ['id', 'name', 'code'],
    fields: [
      {name: 'name', label: 'Nom', type: 'text'},
      {name: 'code', label: 'Code', type: 'text'}
    ]
  },
  regions: {
    display: ['id', 'name', 'country_id'],
    fields: [
      {name: 'name', label: 'Nom', type: 'text'},
      {name: 'country_id', label: 'Pays', type: 'select', optionsEndpoint: '/api/countries'}
    ]
  },
  roles: {
    display: ['id', 'name'],
    fields: [
      {name: 'name', label: 'Nom', type: 'text'}
    ]
  },
  users: {
    display: ['id', 'first_name', 'last_name', 'email', 'user_role'],
    fields: [
      {name: 'first_name', label: 'Prénom', type: 'text'},
      {name: 'last_name', label: 'Nom', type: 'text'},
      {name: 'email', label: 'Email', type: 'text'},
      {name: 'is_active', label: 'Actif', type: 'checkbox'},
      {name: 'user_role', label: 'Rôle', type: 'select', optionsEndpoint: '/api/roles'}
    ]
  },
  amenities: {
    display: ['id', 'label'],
    fields: [
      {name: 'amenities_key', label: 'Key', type: 'text'},
      {name: 'label', label: 'Label', type: 'text'},
      {name: 'icon', label: 'Icon', type: 'file', uploadEndpoint: '/api/amenities/$id/icon'}
    ]
  },
  zone_types: {
    display: ['id', 'name'],
    fields: [
      {name: 'name', label: 'Nom', type: 'text'}
    ]
  },
  zones: {
    display: ['id', 'name', 'zone_type_id', 'zone_description', 'region_id'],
    fields: [
      {name: 'name', label: 'Nom', type: 'text'},
      {name: 'zone_type_id', label: 'Type', type: 'select', optionsEndpoint: '/api/zone_types'},
      {name: 'zone_description', label: 'Description', type: 'text'},
      {name: 'is_available', label: 'Disponible', type: 'checkbox'},
      {name: 'country_id', label: 'Pays', type: 'select', optionsEndpoint: '/api/countries', transient: true},
      {name: 'region_id', label: 'Région', type: 'select', optionsEndpoint: '/api/countries/$country_id/regions', dependsOn: 'country_id', mapEndpoint: '/api/regions'},
      {name: 'total_area', label: 'Superficie totale', type: 'number'},
      {name: 'total_parcels', label: 'Parcelles totales', type: 'number'},
      {name: 'available_parcels', label: 'Parcelles dispo', type: 'number'},
      {name: 'color', label: 'Couleur', type: 'text'},
      {name: 'lambert_x', label: 'Lambert X', type: 'number'},
      {name: 'lambert_y', label: 'Lambert Y', type: 'number'}
      ]
  },
  activities: {
    display: ['id', 'label'],
    fields: [
      {name: 'activities_key', label: 'Key', type: 'text'},
      {name: 'label', label: 'Label', type: 'text'},
      {name: 'icon', label: 'Icon', type: 'file', uploadEndpoint: '/api/activities/$id/icon'}
    ]
  },
  parcels: {
    display: ['id', 'zone_id', 'area', 'is_free'],
    fields: [
      {name: 'zone_id', label: 'Zone', type: 'select', optionsEndpoint: '/api/zones'},
      {name: 'area', label: 'Superficie', type: 'number'},
      {name: 'is_free', label: 'Libre', type: 'checkbox'},
      {name: 'is_available', label: 'Disponible', type: 'checkbox'},
      {name: 'is_showroom', label: 'Showroom', type: 'checkbox'},
      {name: 'CoS', label: 'CoS', type: 'number'},
      {name: 'CuS', label: 'CuS', type: 'number'},
      {name: 'photos', label: 'Photos', type: 'file', multiple: true, uploadEndpoint: '/api/parcels/$id/photo'},
      {name: 'lambert_x', label: 'Lambert X', type: 'number'},
      {name: 'lambert_y', label: 'Lambert Y', type: 'number'}
      ]
  },
  activity_logs: {
    display: ['id', 'user_id', 'action', 'target', 'timestamp'],
    fields: [
      {name: 'user_id', label: 'Utilisateur', type: 'select', optionsEndpoint: '/api/users'},
      {name: 'action', label: 'Action', type: 'text'},
      {name: 'target', label: 'Cible', type: 'text'}
    ]
  },
  appointment_statuses: {
    display: ['id', 'status_name'],
    fields: [
      {name: 'status_name', label: 'Statut', type: 'text'}
    ]
  },
  appointments: {
    display: ['id', 'parcel_id', 'appointment_status_id', 'user_id', 'requested_date'],
    fields: [
      {name: 'parcel_id', label: 'Parcelle', type: 'select', optionsEndpoint: '/api/parcels'},
      {name: 'appointment_status_id', label: 'Statut', type: 'select', optionsEndpoint: '/api/appointment_statuses'},
      {name: 'user_id', label: 'Utilisateur', type: 'select', optionsEndpoint: '/api/users'},
      {name: 'requested_date', label: 'Date demandée', type: 'date'},
      {name: 'confirmed_date', label: 'Date confirmée', type: 'datetime-local'},
      {name: 'appointment_message', label: 'Message', type: 'text'},
      {name: 'contact_phone', label: 'Téléphone', type: 'text'},
      {name: 'company_name', label: 'Entreprise', type: 'text'},
      {name: 'job_title', label: 'Titre', type: 'text'}
    ]
  },
  zone_activities: {
    display: ['zone_id', 'activity_id'],
    fields: [
      {name: 'zone_id', label: 'Zone', type: 'select', optionsEndpoint: '/api/zones'},
      {name: 'activity_id', label: 'Activité', type: 'select', optionsEndpoint: '/api/activities'}
    ]
  },
  parcel_amenities: {
    display: ['parcel_id', 'amenity_id'],
    fields: [
      {name: 'parcel_id', label: 'Parcelle', type: 'select', optionsEndpoint: '/api/parcels'},
      {name: 'amenity_id', label: 'Équipement', type: 'select', optionsEndpoint: '/api/amenities'}
    ]
  }
};
