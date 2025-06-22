function getLabel(obj) {
  return obj.name || obj.label || obj.status_name || obj.code || obj.activities_key || obj.amenities_key || obj.id;
}

document.addEventListener('DOMContentLoaded', () => {
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
  const saveBtn = document.getElementById('save-btn');
  let allItems = [];
  let currentId = null;
  const ITEMS_PER_PAGE = 10;
  let currentPage = 1;

  function closeModal() {
    modal.classList.add('hidden');
  }
  cancelBtn.addEventListener('click', (e) => {
    e.preventDefault();
    closeModal();
  });

  async function loadOptions(field, selectEl) {
    if (!field.optionsEndpoint) return;
    const resp = await fetch(field.optionsEndpoint);
    const data = await resp.json();
    data.forEach(opt => {
      const option = document.createElement('option');
      option.value = opt.id;
      option.textContent = getLabel(opt);
      selectEl.appendChild(option);
    });
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
        loadOptions(f, input);
      } else if (f.type === 'checkbox') {
        input = document.createElement('input');
        input.type = 'checkbox';
        input.className = 'ml-2';
      } else if (f.type === 'file') {
        input = document.createElement('input');
        input.type = 'file';
        if (f.multiple) input.multiple = true;
        input.className = 'w-full';
      } else {
        input = document.createElement('input');
        input.type = f.type || 'text';
        input.className = 'w-full border border-gray-300 p-2 rounded';
      }
      input.name = f.name;
      if (item && item[f.name] !== undefined) {
        if (f.type === 'checkbox') {
          input.checked = !!item[f.name];
        } else if (f.type !== 'file') {
          input.value = item[f.name];
        }
      }
      wrapper.appendChild(input);
      form.appendChild(wrapper);
    });
  }

  async function fetchItems() {
    const resp = await fetch('/api/' + resource + '/');
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
      th.textContent = col;
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
        td.textContent = item[col];
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
  }

  async function saveItem() {
    const data = {};
    const filesToUpload = [];
    cfg.fields.forEach(f => {
      const el = form.querySelector(`[name="${f.name}"]`);
      if (!el) return;
      if (f.type === 'checkbox') {
        data[f.name] = el.checked;
      } else if (f.type === 'file') {
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
      body: JSON.stringify(data)
    });
    if (resp.ok) {
      const saved = await resp.json();
      const itemId = saved.id || currentId;
      for (const item of filesToUpload) {
        const fd = new FormData();
        Array.from(item.input.files).forEach(f => fd.append('file', f));
        const urlUpload = item.field.uploadEndpoint.replace('$id', itemId);
        await fetch(urlUpload, {method: 'POST', body: fd});
      }
      closeModal();
      fetchItems();
    } else {
      alert('Erreur lors de la sauvegarde');
    }
  }

  async function deleteItem(id) {
    if (!confirm('Supprimer cet élément ?')) return;
    await fetch('/api/' + resource + '/' + id, { method: 'DELETE' });
    fetchItems();
  }

  document.getElementById('add-btn').addEventListener('click', () => openForm(null));
  saveBtn.addEventListener('click', (e) => { e.preventDefault(); saveItem(); });

  fetchItems();
});
