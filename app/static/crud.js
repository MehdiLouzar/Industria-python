function getLabel(obj) {
  return obj.name
    || obj.label
    || obj.status_name
    || obj.code
    || obj.activities_key
    || obj.amenities_key
    || obj.id;
}

function normalizeText(text) {
  return text
    ? text.toString().normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
    : '';
}

async function initCrud() {
  const container = document.getElementById('crud-app');
  if (!container) return;

  const resource = container.dataset.resource;
  const cfg = CRUD_CONFIG[resource];
  if (!cfg) {
    container.innerHTML = `<p>Configuration manquante pour ${resource}</p>`;
    return;
  }

  // Modal et form
  const modal     = document.getElementById('form-modal');
  const form      = document.getElementById('item-form');
  const formTitle = document.getElementById('form-title');
  const cancelBtn = document.getElementById('cancel-btn');
  const deleteBtn = document.getElementById('delete-btn');
  const closeBtn  = document.getElementById('close-btn');
  const saveBtn   = document.getElementById('save-btn');
  const searchBox = document.getElementById('search-box');

  let allItems    = [];
  let currentId   = null;
  const ITEMS_PER_PAGE = 10;
  let currentPage = 1;
  let searchQuery = '';
  const selectMaps = {};

  // map des labels de champs
  const labelMap = {};
  cfg.fields.forEach(f => {
    labelMap[f.name] = f.label || f.name;
  });

  // Chargement des listes pour <select>
  async function loadSelectMaps() {
    const selects = cfg.fields.filter(f => f.type === 'select');
    await Promise.all(selects.map(async f => {
      let url = f.mapEndpoint || f.optionsEndpoint;
      if (!url) return;
      if (url.includes('$')) {
        url = url.replace(/\$[^/]+/, '').replace(/\/\//g, '/');
      }
      const resp = await fetch(url, { credentials: 'same-origin' });
      if (!resp.ok) return;
      const data = await resp.json();
      selectMaps[f.name] = Object.fromEntries(data.map(o => [o.id, getLabel(o)]));
    }));
  }

  // Fermeture modal
  function closeModal() {
    modal.classList.add('hidden');
  }
  cancelBtn.addEventListener('click', e => { e.preventDefault(); closeModal(); });
  if (deleteBtn) {
    deleteBtn.addEventListener('click', e => {
      e.preventDefault();
      if (currentId) {
        deleteItem(currentId);
        closeModal();
      }
    });
  }
  if (closeBtn) {
    closeBtn.addEventListener('click', e => { e.preventDefault(); closeModal(); });
  }

  // Charge dynamiquement les options d'un <select>
  async function loadOptions(field, selectEl, selectedValue) {
    let url = field.optionsEndpoint;
    if (field.dependsOn) {
      const depVal = form.querySelector(`[name="${field.dependsOn}"]`).value;
      if (!depVal) {
        selectEl.innerHTML = '';
        return;
      }
      url = url.replace(`$${field.dependsOn}`, depVal);
    }
    const resp = await fetch(url, { credentials: 'same-origin' });
    if (!resp.ok) return;
    const data = await resp.json();

    selectEl.innerHTML = '';
    const emptyOpt = document.createElement('option');
    emptyOpt.value = '';
    emptyOpt.textContent = '';
    selectEl.appendChild(emptyOpt);

    data.forEach(opt => {
      const option = document.createElement('option');
      option.value = opt.id;
      option.textContent = getLabel(opt);
      selectEl.appendChild(option);
    });

    if (selectedValue != null) {
      selectEl.value = selectedValue;
    }
  }

  // Construction du formulaire (création / modification)
  function renderForm(item = {}) {
    form.innerHTML = '';
    cfg.fields.forEach(f => {
      const wrapper = document.createElement('div');
      const label = document.createElement('label');
      label.textContent = f.label;
      label.className = 'block text-sm';
      wrapper.appendChild(label);

      let input;
      if (f.type === 'select') {
        input = document.createElement('select');
        input.className = 'w-full border border-gray-300 p-2 rounded';
        if (f.dependsOn) {
          input.disabled = true;
          const depEl = form.querySelector(`[name="${f.dependsOn}"]`);
          depEl.addEventListener('change', async () => {
            await loadOptions(f, input, item[f.name]);
            input.disabled = false;
          });
        }
        loadOptions(f, input, item[f.name]);
      }
      else if (f.type === 'multiselect') {
        input = document.createElement('div');
        input.className = 'flex flex-col gap-1';
        input.dataset.field = f.name;

        const optionsPromise = fetch(f.optionsEndpoint, { credentials: 'same-origin' }).then(r => r.json());
        const selectedPromise = item.id ?
          fetch(f.linkEndpoint, { credentials: 'same-origin' })
            .then(r => r.json())
            .then(list => list.filter(o => o[f.parentKey] === item.id)
                              .map(o => o[f.childKey]))
          : Promise.resolve([]);
        Promise.all([optionsPromise, selectedPromise]).then(([options, selected]) => {
          input.dataset.original = JSON.stringify(selected);
          options.forEach(opt => {
            const lbl = document.createElement('label');
            lbl.className = 'inline-flex items-center gap-1';
            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.name = f.name;
            cb.value = opt.id;
            if (selected.includes(opt.id)) cb.checked = true;
            lbl.append(cb, document.createTextNode(getLabel(opt)));
            input.appendChild(lbl);
          });
        });
      }
      else if (f.type === 'checkbox') {
        input = document.createElement('input');
        input.type = 'checkbox';
        input.className = 'ml-2';
        input.checked = !!item[f.name];
      } 
      else if (f.type === 'file') {
        input = document.createElement('input');
        input.type = 'file';
        if (f.multiple) input.multiple = true;
        input.className = 'w-full';

        const preview = document.createElement('div');
        preview.className = 'flex flex-wrap gap-2 mt-2';

        const existing = Array.isArray(item[f.name]) ? [...item[f.name]] : (item[f.name] ? [item[f.name]] : []);
        input.dataset.existing = JSON.stringify(existing);

        // Keep selected files across multiple changes for multi-upload fields
        const selectedFiles = [];

        function syncFileInput() {
          const dt = new DataTransfer();
          selectedFiles.forEach(f => dt.items.add(f));
          input.files = dt.files;
        }

        function renderPreviews() {
          preview.innerHTML = '';
          existing.forEach((path, idx) => {
            const holder = document.createElement('div');
            holder.className = 'relative inline-block';
            const img = document.createElement('img');
            img.src = '/static/' + path;
            img.className = 'h-20 w-20 object-cover rounded';
            const rm = document.createElement('button');
            rm.type = 'button';
            rm.innerHTML = '&times;';
            rm.className = 'absolute -top-1 -right-1 bg-white rounded-full text-red-600 text-xs';
            rm.addEventListener('click', () => {
              existing.splice(idx, 1);
              input.dataset.existing = JSON.stringify(existing);
              renderPreviews();
            });
            holder.append(img, rm);
            preview.append(holder);
          });

          selectedFiles.forEach((file, idx) => {
            const holder = document.createElement('div');
            holder.className = 'relative inline-block';
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            img.className = 'h-20 w-20 object-cover rounded';
            const rm = document.createElement('button');
            rm.type = 'button';
            rm.innerHTML = '&times;';
            rm.className = 'absolute -top-1 -right-1 bg-white rounded-full text-red-600 text-xs';
            rm.addEventListener('click', () => {
              selectedFiles.splice(idx, 1);
              syncFileInput();
              renderPreviews();
            });
            holder.append(img, rm);
            preview.append(holder);
          });
        }

        input.addEventListener('change', () => {
          if (!f.multiple) {
            existing.length = 0;
            input.dataset.existing = JSON.stringify(existing);
            selectedFiles.length = 0;
          }
          Array.from(input.files).forEach(f => selectedFiles.push(f));
          syncFileInput();
          renderPreviews();
        });

        // Initial sync for edit mode
        syncFileInput();
        renderPreviews();
        wrapper.append(input, preview);
      } 
      else if (f.type === 'coords') {
        input = document.createElement('div');
        input.className = 'space-y-2';
        input.dataset.field = f.name;

        const list = document.createElement('div');
        input.appendChild(list);

        const addBtn = document.createElement('button');
        addBtn.type = 'button';
        addBtn.textContent = 'Ajouter';
        addBtn.className = 'mt-2 px-2 py-1 bg-blue-600 text-white rounded';
        input.appendChild(addBtn);

        function addRow(pair) {
          const row = document.createElement('div');
          row.className = 'coord-row flex gap-2 items-center';
          const x = document.createElement('input');
          x.type = 'number';
          x.step = 'any';
          x.className = 'w-full border border-gray-300 p-2 rounded';
          const y = document.createElement('input');
          y.type = 'number';
          y.step = 'any';
          y.className = 'w-full border border-gray-300 p-2 rounded';
          if (Array.isArray(pair)) {
            x.value = pair[0];
            y.value = pair[1];
          }
          const rm = document.createElement('button');
          rm.type = 'button';
          rm.textContent = '×';
          rm.className = 'text-red-600';
          rm.addEventListener('click', () => row.remove());
          row.append(x, y, rm);
          list.appendChild(row);
        }

        addBtn.addEventListener('click', () => addRow());
        const existingPairs = item[f.name] || [];
        if (existingPairs.length) existingPairs.forEach(addRow);
        else addRow();
      }
      else if (f.type === 'textarea') {
        input = document.createElement('textarea');
        input.className = 'w-full border border-gray-300 p-2 rounded';
        if (item[f.name] != null) {
          if (f.name === 'lambert_coords') {
            input.value = item[f.name]
              .map(pair => Array.isArray(pair) ? pair.join(' ') : '')
              .join('\n');
          } else {
            input.value = item[f.name];
          }
        }
      }
      else {
        input = document.createElement('input');
        input.type = f.type || 'text';
        input.className = 'w-full border border-gray-300 p-2 rounded';
        if (item[f.name] != null) {
          input.value = item[f.name];
        }
      }

      if (f.type !== 'multiselect') {
        input.name = f.name;
      }
      if (f.type !== 'file') wrapper.appendChild(input);
      form.appendChild(wrapper);
    });
  }

  // Récupération et affichage des éléments
  async function fetchItems() {
    const resp = await fetch(`/api/${resource}/`, { credentials: 'same-origin' });
    allItems = await resp.json();
    renderTable();
  }

  function renderTable() {
    const container = document.getElementById('table-container');
    container.innerHTML = '';
    const table = document.createElement('table');
    table.className = 'min-w-full divide-y divide-gray-200';

    // En-tête
    const thead = document.createElement('thead');
    const headRow = document.createElement('tr');
    cfg.display.forEach(col => {
      const th = document.createElement('th');
      th.textContent = labelMap[col] || col.replace(/_/g, ' ');
      th.className = 'px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase';
      headRow.appendChild(th);
    });
    headRow.appendChild(document.createElement('th')).textContent = 'Actions';
    thead.append(headRow);
    table.append(thead);

    // Corps
    const tbody = document.createElement('tbody');
    const filtered = allItems.filter(i => {
      const data = normalizeText(JSON.stringify(i));
      return data.includes(searchQuery);
    });
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    filtered.slice(start, start + ITEMS_PER_PAGE).forEach(item => {
      const tr = document.createElement('tr');
      cfg.display.forEach(col => {
        const td = document.createElement('td');
        let val = item[col];
        if (selectMaps[col]) val = selectMaps[col][val] ?? val;
        td.textContent = val;
        td.className = 'px-3 py-2 text-sm text-gray-700';
        tr.appendChild(td);
      });

      // Actions
      const tdAct = document.createElement('td');
      const editBtn = document.createElement('button');
      editBtn.textContent = 'Éditer';
      editBtn.className = 'text-blue-600 mr-2';
      editBtn.addEventListener('click', () => openForm(item));

      const delBtn = document.createElement('button');
      delBtn.textContent = 'Supprimer';
      delBtn.className = 'text-red-600';
      delBtn.addEventListener('click', () => deleteItem(item.id));

      tdAct.append(editBtn, delBtn);
      tr.appendChild(tdAct);
      tbody.appendChild(tr);
    });
    table.append(tbody);
    container.append(table);

    // Pagination
    const totalPages = Math.ceil(filtered.length / ITEMS_PER_PAGE);
    const pag = document.createElement('div');
    pag.className = 'mt-4 flex space-x-2';
    for (let i = 1; i <= totalPages; i++) {
      const btn = document.createElement('button');
      btn.textContent = i;
      btn.className = `px-3 py-1 border rounded ${i === currentPage ? 'bg-gray-300' : ''}`;
      btn.addEventListener('click', () => { currentPage = i; renderTable(); });
      pag.appendChild(btn);
    }
    container.append(pag);
  }

  async function openForm(item = {}) {
    currentId = item.id || null;
    formTitle.textContent = currentId ? 'Modifier' : 'Créer';
    renderForm(item);
    if (deleteBtn) {
      if (currentId) deleteBtn.classList.remove('hidden');
      else deleteBtn.classList.add('hidden');
    }

    // Affichage des noms de pays et région lors de l'édition d'une zone
    if (resource === 'zones') {
      const countrySelect = form.querySelector('[name="country_id"]');
      const regionSelect = form.querySelector('[name="region_id"]');
      const infoId = 'zone-edit-info';
      let info = document.getElementById(infoId);
      if (!info) {
        info = document.createElement('div');
        info.id = infoId;
        info.className = 'mb-2 text-sm text-gray-600';
        form.prepend(info);
      }

      async function updateInfo(regionId) {
        if (!regionId) { info.textContent = ''; return; }
        const reg = await fetch(`/api/regions/${regionId}`, { credentials: 'same-origin' }).then(r => r.json());
        const country = await fetch(`/api/countries/${reg.country_id}`, { credentials: 'same-origin' }).then(r => r.json());
        info.innerHTML = `Pays : ${country.name} — Région : ${reg.name}`;
      }

      if (item?.region_id) {
        const region = await fetch(`/api/regions/${item.region_id}`, { credentials: 'same-origin' }).then(r => r.json());
        await loadOptions(cfg.fields.find(f => f.name === 'country_id'), countrySelect, region.country_id);
        countrySelect.dispatchEvent(new Event('change'));
        updateInfo(item.region_id);
      }

      regionSelect.addEventListener('change', () => updateInfo(regionSelect.value));
    }

    modal.classList.remove('hidden');
  }

  async function saveItem() {
    const data = {};
    const filesToUpload = [];
    const linkUpdates = [];

    cfg.fields.forEach(f => {
      if (f.transient) return;
      const el = f.type === 'multiselect'
        ? form.querySelector(`[data-field="${f.name}"]`)
        : form.querySelector(`[name="${f.name}"]`);
      if (!el) return;

      if (f.type === 'checkbox') data[f.name] = el.checked;
      else if (f.type === 'file') {
        const existing = JSON.parse(el.dataset.existing || '[]');
        data[f.name] = f.multiple ? existing : existing[0] || null;
        if (el.files.length) filesToUpload.push({ field: f, input: el });
      }
      else if (f.type === 'multiselect') {
        const selected = Array.from(el.querySelectorAll('input[type="checkbox"]:checked')).map(c => parseInt(c.value));
        const original = JSON.parse(el.dataset.original || '[]');
        linkUpdates.push({ field: f, selected, original });
      }
      else if (f.type === 'coords') {
        const rows = el.querySelectorAll('.coord-row');
        const coords = [];
        rows.forEach(r => {
          const inputs = r.querySelectorAll('input[type="number"]');
          if (inputs.length === 2) {
            const x = parseFloat(inputs[0].value);
            const y = parseFloat(inputs[1].value);
            if (!isNaN(x) && !isNaN(y)) coords.push([x, y]);
          }
        });
        data[f.name] = coords;
      }
      else if (f.type === 'textarea' && f.name === 'lambert_coords') {
        const coords = el.value.trim()
          .split(/\n|;/)
          .map(s => s.trim())
          .filter(Boolean)
          .map(pair => pair.split(/[,\s]+/).map(Number))
          .filter(arr => arr.length === 2 && arr.every(n => !isNaN(n)));
        data[f.name] = coords;
      }
      else data[f.name] = el.value;
    });

    const url = `/api/${resource}/${currentId || ''}`;
    const method = currentId ? 'PUT' : 'POST';
    const resp = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'same-origin'
    });

    if (!resp.ok) {
      const msg = await resp.text();
      return alert('Erreur lors de la sauvegarde: ' + msg);
    }

    const saved = await resp.json();
    const itemId = saved.id || currentId;

    for (const { field, input } of filesToUpload) {
      const fd = new FormData();
      Array.from(input.files).forEach(f => fd.append('file', f));
      const uploadUrl = field.uploadEndpoint.replace('$id', itemId);
      await fetch(uploadUrl, { method: 'POST', body: fd, credentials: 'same-origin' });
    }

    for (const { field, selected, original } of linkUpdates) {
      const toAdd = selected.filter(id => !original.includes(id));
      const toRemove = original.filter(id => !selected.includes(id));
      for (const id of toAdd) {
        const body = { [field.parentKey]: itemId, [field.childKey]: id };
        await fetch(field.linkEndpoint + '/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
          credentials: 'same-origin'
        });
      }
      for (const id of toRemove) {
        const urlDel = `${field.linkEndpoint}/${itemId}/${id}`;
        await fetch(urlDel, { method: 'DELETE', credentials: 'same-origin' });
      }
    }

    closeModal();
    fetchItems();
  }

  async function deleteItem(id) {
    if (!confirm('Supprimer cet élément ?')) return;
    if (cfg.cascadeMessage && !confirm(cfg.cascadeMessage)) return;
    await fetch(`/api/${resource}/${id}`, { method: 'DELETE', credentials: 'same-origin' });
    fetchItems();
  }

  document.getElementById('add-btn').addEventListener('click', () => openForm());
  saveBtn.addEventListener('click', e => { e.preventDefault(); saveItem(); });

  await loadSelectMaps();
  fetchItems();

  if (searchBox) {
    searchBox.addEventListener('input', () => {
      searchQuery = normalizeText(searchBox.value.trim());
      currentPage = 1;
      renderTable();
    });
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initCrud);
} else {
  initCrud();
}
