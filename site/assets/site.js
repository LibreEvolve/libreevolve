/* Progressive theme preference only. No telemetry, network or candidate execution. */
(() => {
  const root = document.documentElement;
  const button = document.querySelector('.theme');
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let preference = null;
  try { preference = localStorage.getItem('libreevolve-theme'); } catch (_) {}
  if (preference === 'light' || preference === 'dark') root.dataset.theme = preference;
  function current() { return root.dataset.theme || (system.matches ? 'dark' : 'light'); }
  function label() {
    const next = current() === 'dark' ? 'light' : 'dark';
    button.textContent = next === 'light' ? 'Light theme' : 'Dark theme';
    button.setAttribute('aria-label', `Switch to ${next} theme`);
  }
  button.hidden = false;
  label();
  system.addEventListener('change', label);
  button.addEventListener('click', () => {
    root.dataset.theme = current() === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('libreevolve-theme', root.dataset.theme); } catch (_) {}
    label();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      const menu = document.querySelector('details[open]');
      if (menu) { menu.open = false; menu.querySelector('summary').focus(); }
    }
  });
})();
