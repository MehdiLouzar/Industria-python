document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form');
  const errorBox = document.getElementById('login-error');
  const toggleBtn = document.getElementById('togglePassword');
  const passwordInput = document.getElementById('password');
  const eyeOpenGroup = document.getElementById('eye-open');
  const eyeClosedGroup = document.getElementById('eye-closed');

  // Toggle password visibility
  if (toggleBtn && passwordInput) {
    toggleBtn.addEventListener('click', () => {
      const isHidden = passwordInput.type === 'password';
      passwordInput.type = isHidden ? 'text' : 'password';
      eyeOpenGroup.classList.toggle('hidden', isHidden);
      eyeClosedGroup.classList.toggle('hidden', !isHidden);
    });
  }

  // Handle form submission
  if (form && errorBox) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      errorBox.classList.add('hidden');
      errorBox.textContent = '';
      errorBox.classList.remove('animate-shake');

      const username = document.getElementById('username').value.trim();
      const password = passwordInput.value.trim();

      try {
        const resp = await fetch('/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });

        if (resp.ok) {
          window.location.href = '/';
        } else {
          const data = await resp.json();
          errorBox.textContent = data.error || 'Nom d’utilisateur ou mot de passe incorrect.';
          errorBox.classList.remove('hidden');
          void errorBox.offsetWidth;
          errorBox.classList.add('animate-shake');
        }
      } catch {
        errorBox.textContent = 'Erreur lors de la connexion. Veuillez réessayer.';
        errorBox.classList.remove('hidden');
        void errorBox.offsetWidth;
        errorBox.classList.add('animate-shake');
      }
    });
  }
});