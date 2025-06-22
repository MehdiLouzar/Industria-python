document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        try {
            const resp = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            if (resp.ok) {
                const data = await resp.json();
                console.log(data);
                alert('Connexion réussie');
            } else {
                alert('Utilisateur ou mot de passe incorrect');
            }
        } catch (err) {
            console.error(err);
            alert('Erreur lors de la connexion');
        }
    });

    if (window.lucide) {
        window.lucide.createIcons();
    }
});
