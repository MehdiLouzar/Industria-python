function getLabel(obj) {
  return obj.name || obj.label || obj.status_name || obj.code || obj.activities_key || obj.amenities_key || obj.id;
}

document.addEventListener('DOMContentLoaded', async () => {
  const container = document.getElementById('crud-app');
  if (!container) return;
  const resource = container.dataset.resource;
  const cfg = CRUD_CONFIG[resource];
  if (!cfg) {
    container.innerHTML = '<p>Configuration manquante pour ' + resource + '</p>';
    return;
  }

  const modal = document.getElementById('form-modal');
  const form = document.getElementById('item-form');
  const formTitle = document.getElementById('form-title');
  const cancelBtn = document.getElementById('cancel-btn');
  const closeBtn = document.getElementById('close-btn');
  const saveBtn = document.getElementById('save-btn');
  let allItems = [];
  let currentId = null;
  const ITEMS_PER_PAGE = 10;
  let currentPage = 1;
  const selectMaps = {};
  const labelMap = {};
  cfg.fields.forEach(f => { labelMap[f.name] = f.label || f.name; });

  async function loadSelectMaps() {
    const selects = cfg.fields.filter(f => f.type === 'select');
    await Promise.all(selects.map(async f => {
      let url = f.mapEndpoint || f.optionsEndpoint;
      if (!url) return;
      // Remove placeholder if present
      if (url.includes('$')) {
        url = url.replace(/\$[^/]+/, '').replace(/\/\//g, '/');
      }
      const resp = await fetch(url, {credentials: 'same-origin'});
      if (!resp.ok) return;
      
      const data = await resp.json();
      const map = {};
      data.forEach(opt => { map[opt.id] = getLabel(opt); });
      selectMaps[f.name] = map;
    }));
  }

  function closeModal() {
    modal.classList.add('hidden');
  }
  cancelBtn.addEventListener('click', (e) => {
    e.preventDefault();
    closeModal();
  });
  if (closeBtn) {
    closeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      closeModal();
    });
  }

  async function loadOptions(field, selectEl, selectedValue) {
    if (!field.optionsEndpoint) return;
    let url = field.optionsEndpoint;
    if (field.dependsOn) {
      const depVal = form.querySelector(`[name="${field.dependsOn}"]`).value;
      if (!depVal) {
        selectEl.innerHTML = '';
        return;
      }
      url = url.replace(`$${field.dependsOn}`, depVal);
    }
    const resp = await fetch(url, {credentials: 'same-origin'});
    const data = await resp.json();
    selectEl.innerHTML = '';
    const empty = document.createElement('option');
    empty.value = '';
    empty.textContent = '';
    selectEl.appendChild(empty);
    data.forEach(opt => {
      const option = document.createElement('option');
      option.value = opt.id;
      option.textContent = getLabel(opt);
      selectEl.appendChild(option);
    });
    if (selectedValue !== undefined && selectedValue !== null) {
      selectEl.value = selectedValue;
    }
  }

  function renderForm(item) {
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
          const update = async () => {
            await loadOptions(f, input, item ? item[f.name] : null);
            input.disabled = false;
          };
          depEl.addEventListener('change', update);
          if (depEl && depEl.value) update();
        } else {
          loadOptions(f, input, item ? item[f.name] : null);
        }
      } else if (f.type === 'checkbox') {
        input = document.createElement('input');
        input.type = 'checkbox';
        input.className = 'ml-2';
      } else if (f.type === 'file') {
        input = document.createElement('input');
        input.type = 'file';
        if (f.multiple) input.multiple = true;
        input.className = 'w-full';
        const preview = document.createElement('div');
        preview.className = 'flex flex-wrap gap-2 mt-2';
        const existing = [];
        if (item && item[f.name]) {
          if (Array.isArray(item[f.name])) existing.push(...item[f.name]);
          else existing.push(item[f.name]);
        }
        input.dataset.existing = JSON.stringify(existing);
        function renderPreviews() {
          preview.innerHTML = '';
          if (!f.multiple && input.files.length) {
            existing.splice(0);
            input.dataset.existing = JSON.stringify(existing);
          }
          existing.forEach((path, idx) => {
            const holder = document.createElement('div');
            holder.className = 'relative inline-block';
            const img = document.createElement('img');
            img.className = 'h-20 w-20 object-cover rounded';
            img.src = '/static/' + path;
            const rm = document.createElement('button');
            rm.type = 'button';
            rm.innerHTML = '&times;';
            rm.className = 'absolute -top-1 -right-1 bg-white rounded-full text-red-600 text-xs';
            rm.addEventListener('click', () => {
              existing.splice(idx, 1);
              input.dataset.existing = JSON.stringify(existing);
              renderPreviews();
            });
            holder.appendChild(img);
            holder.appendChild(rm);
            preview.appendChild(holder);
          });
          Array.from(input.files).forEach((file, idx) => {
            const holder = document.createElement('div');
            holder.className = 'relative inline-block';
            const img = document.createElement('img');
            img.className = 'h-20 w-20 object-cover rounded';
            img.src = URL.createObjectURL(file);
            const rm = document.createElement('button');
            rm.type = 'button';
            rm.innerHTML = '&times;';
            rm.className = 'absolute -top-1 -right-1 bg-white rounded-full text-red-600 text-xs';
            rm.addEventListener('click', () => {
              const dt = new DataTransfer();
              Array.from(input.files).forEach((f, i) => {
                if (i !== idx) dt.items.add(f);
              });
              input.files = dt.files;
              renderPreviews();
            });
            holder.appendChild(img);
            holder.appendChild(rm);
            preview.appendChild(holder);
          });
        }
        input.addEventListener('change', renderPreviews);
        renderPreviews();
        wrapper.appendChild(input);
        wrapper.appendChild(preview);
      } else {
        input = document.createElement('input');
        input.type = f.type || 'text';
        input.className = 'w-full border border-gray-300 p-2 rounded';
      }
      if (f.type !== 'file') {
        wrapper.appendChild(input);
      }
      input.name = f.name;
      if (item && item[f.name] !== undefined) {
        if (f.type === 'checkbox') {
          input.checked = !!item[f.name];
        } else if (f.type !== 'file') {
          input.value = item[f.name];
        }
      }
      form.appendChild(wrapper);
    });
  }

  async function fetchItems() {
    const resp = await fetch('/api/' + resource + '/', {credentials: 'same-origin'});
    allItems = await resp.json();
    renderTable();
  }

  function renderTable() {
    const container = document.getElementById('table-container');
    container.innerHTML = '';
    const table = document.createElement('table');
    table.className = 'min-w-full divide-y divide-gray-200';
    const thead = document.createElement('thead');
    const headRow = document.createElement('tr');
    cfg.display.forEach(col => {
      const th = document.createElement('th');
      th.textContent = labelMap[col] || col.replace(/_/g, ' ');
      th.className = 'px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase';
      headRow.appendChild(th);
    });
    const thActions = document.createElement('th');
    thActions.textContent = 'Actions';
    headRow.appendChild(thActions);
    thead.appendChild(headRow);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    const pageItems = allItems.slice(start, start + ITEMS_PER_PAGE);
    pageItems.forEach(item => {
      const tr = document.createElement('tr');
      cfg.display.forEach(col => {
        const td = document.createElement('td');
        let value = item[col];
        if (selectMaps[col]) {
          value = selectMaps[col][value] ?? value;
        }
        td.textContent = value;
        td.className = 'px-3 py-2 text-sm text-gray-700';
        tr.appendChild(td);
      });
      const tdAct = document.createElement('td');
      const editBtn = document.createElement('button');
      editBtn.textContent = 'Éditer';
      editBtn.className = 'text-blue-600 mr-2';
      editBtn.addEventListener('click', () => openForm(item));
      const delBtn = document.createElement('button');
      delBtn.textContent = 'Supprimer';
      delBtn.className = 'text-red-600';
      delBtn.addEventListener('click', () => deleteItem(item.id));
      tdAct.appendChild(editBtn);
      tdAct.appendChild(delBtn);
      tr.appendChild(tdAct);
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    container.appendChild(table);

    const totalPages = Math.ceil(allItems.length / ITEMS_PER_PAGE);
    const pag = document.createElement('div');
    pag.className = 'mt-4 flex space-x-2';
    for (let i = 1; i <= totalPages; i++) {
      const btn = document.createElement('button');
      btn.textContent = i;
      btn.className = 'px-3 py-1 border rounded ' + (i === currentPage ? 'bg-gray-300' : '');
      btn.addEventListener('click', () => { currentPage = i; renderTable(); });
      pag.appendChild(btn);
    }
    container.appendChild(pag);
  }

  function openForm(item) {
    currentId = item ? item.id : null;
    formTitle.textContent = item ? 'Modifier' : 'Créer';
    renderForm(item);
    modal.classList.remove('hidden');
    if (resource === 'zones' && item && item.region_id) {
      const countrySelect = form.querySelector('[name="country_id"]');
      const regionSelect = form.querySelector('[name="region_id"]');
      fetch('/api/regions/' + item.region_id, {credentials: 'same-origin'})
        .then(r => r.json())
        .then(region => {
          countrySelect.value = region.country_id;
          countrySelect.dispatchEvent(new Event('change'));
        });
    }
  }

  async function saveItem() {
    const data = {};
    const filesToUpload = [];
    cfg.fields.forEach(f => {
      const el = form.querySelector(`[name="${f.name}"]`);
      if (!el) return;
      if (f.transient) return;
      if (f.type === 'checkbox') {
        data[f.name] = el.checked;
      } else if (f.type === 'file') {
        const existing = JSON.parse(el.dataset.existing || '[]');
        if (f.multiple) {
          data[f.name] = existing;
        } else {
          data[f.name] = existing[0] || null;
        }
        if (el.files.length) {
          filesToUpload.push({field: f, input: el});
        }
      } else {
        data[f.name] = el.value;
      }
    });
    const url = '/api/' + resource + '/' + (currentId ? currentId : '');
    const method = currentId ? 'PUT' : 'POST';
    const resp = await fetch(url, {
      method: method,
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data),
      credentials: 'same-origin'
    });
    if (resp.ok) {
      const saved = await resp.json();
      const itemId = saved.id || currentId;
      for (const item of filesToUpload) {
        const fd = new FormData();
        Array.from(item.input.files).forEach(f => fd.append('file', f));
        const urlUpload = item.field.uploadEndpoint.replace('$id', itemId);
        await fetch(urlUpload, {method: 'POST', body: fd, credentials: 'same-origin'});
      }
      closeModal();
      fetchItems();
    } else {
      const msg = await resp.text();
      alert('Erreur lors de la sauvegarde: ' + msg);
    }
  }

  async function deleteItem(id) {
    if (!confirm('Supprimer cet élément ?')) return;
    await fetch('/api/' + resource + '/' + id, { method: 'DELETE', credentials: 'same-origin' });
    fetchItems();
  }

  document.getElementById('add-btn').addEventListener('click', () => openForm(null));
  saveBtn.addEventListener('click', (e) => { e.preventDefault(); saveItem(); });

  await loadSelectMaps();
  fetchItems();
});
