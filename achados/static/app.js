// Preferências locais: nenhuma informação é enviada ao servidor.
const root = document.documentElement;
const preferenceKey = 'achados-accessibility';
const preferenceStatus = document.getElementById('accessibility-status');
const contrastToggle = document.getElementById('contrast-toggle');
const colorProfileSelect = document.getElementById('color-profile');
const colorProfiles = {
  default: null,
  acromatomia: 'Acromatomia',
  acromatopsia: 'Acromatopsia',
  deuteranomalia: 'Deuteranomalia',
  deuteranopia: 'Deuteranopia',
  protanomalia: 'Protonomalia',
  protanopia: 'Protanopia',
  tritanomalia: 'Tritanomalia',
  tritanopia: 'Tritanopia',
};
let colorProfile = 'default';
let fontSize = 100;
let highContrast = false;
try {
  const saved = JSON.parse(localStorage.getItem(preferenceKey) || '{}');
  if ([100, 125, 150].includes(saved.fontSize)) fontSize = saved.fontSize;
  highContrast = saved.highContrast === true;
  if (Object.hasOwn(colorProfiles, saved.colorProfile)) colorProfile = saved.colorProfile;
} catch { /* As preferências também funcionam quando o armazenamento está bloqueado. */ }
function applyPreferences(announce = false) {
  root.style.fontSize = `${fontSize}%`;
  root.dataset.contrast = highContrast ? 'high' : 'normal';
  if (colorProfileSelect) colorProfileSelect.value = colorProfile;
  const filterId = colorProfiles[colorProfile];
  root.style.setProperty('--color-filter', filterId ? `url("#${filterId}")` : 'none');
  contrastToggle?.setAttribute('aria-pressed', String(highContrast));
  document.querySelector('[data-font="decrease"]')?.setAttribute('aria-disabled', String(fontSize === 100));
  document.querySelector('[data-font="increase"]')?.setAttribute('aria-disabled', String(fontSize === 150));
  try { localStorage.setItem(preferenceKey, JSON.stringify({ fontSize, highContrast, colorProfile })); } catch { /* Opcional. */ }
  if (announce && preferenceStatus) {
    preferenceStatus.textContent = `Texto em ${fontSize}%. Alto contraste ${highContrast ? 'ativado' : 'desativado'}. Cores: ${colorProfileSelect?.selectedOptions[0]?.textContent || 'padrão'}.`;
  }
}
document.querySelectorAll('[data-font]').forEach((button) => {
  button.addEventListener('click', () => {
    fontSize = Math.max(100, Math.min(150, fontSize + (button.dataset.font === 'increase' ? 25 : -25)));
    applyPreferences(true);
  });
});
contrastToggle?.addEventListener('click', () => { highContrast = !highContrast; applyPreferences(true); });
colorProfileSelect?.addEventListener('change', () => {
  colorProfile = Object.hasOwn(colorProfiles, colorProfileSelect.value) ? colorProfileSelect.value : 'default';
  applyPreferences(true);
});
applyPreferences();
document.querySelectorAll('form[data-confirm]').forEach((form) => {
  form.addEventListener('submit', (event) => {
    if (!window.confirm(form.dataset.confirm)) event.preventDefault();
  });
});

const statusSelect = document.querySelector('.item-form #status');
const returnSection = document.getElementById('return-section');
function updateReturnFields() {
  if (!returnSection || !statusSelect) return;
  const returned = statusSelect.value === 'devolvido';
  returnSection.hidden = !returned;
  returnSection.querySelectorAll('input, textarea').forEach((field) => {
    field.disabled = !returned;
    field.required = returned;
  });
}
statusSelect?.addEventListener('change', updateReturnFields);
updateReturnFields();

const custody = document.querySelector('.item-form #local_guarda');
function updateCustody() {
  const selected = document.querySelector('input[name="tipo"]:checked');
  if (!custody || !selected) return;
  custody.required = selected.value === 'encontrado';
  const label = document.querySelector('label[for="local_guarda"]');
  let indicator = label.querySelector('span');
  if (!indicator) {
    indicator = document.createElement('span');
    indicator.setAttribute('aria-hidden', 'true');
    indicator.textContent = ' *';
    label.append(indicator);
  }
  indicator.hidden = !custody.required;
}
document.querySelectorAll('input[name="tipo"]').forEach((field) => field.addEventListener('change', updateCustody));
updateCustody();

// O resumo recebe foco após uma resposta de validação do servidor.
const errorSummary = document.getElementById('form-errors');
if (errorSummary) {
  errorSummary.focus();
  errorSummary.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (event) => {
      const target = document.getElementById(link.hash.slice(1));
      if (target) { event.preventDefault(); target.focus(); target.scrollIntoView({ block: 'center' }); }
    });
  });
}

const institutionLogo = document.querySelector('.institution-logo img');
function showLogoFallback() {
  institutionLogo.hidden = true;
  const fallback = document.querySelector('.logo-fallback');
  if (fallback) fallback.hidden = false;
}
if (institutionLogo) {
  institutionLogo.addEventListener('error', showLogoFallback);
  if (institutionLogo.complete && institutionLogo.naturalWidth === 0) showLogoFallback();
}

// Retorno ao cabeçalho também devolve o foco para a navegação.
const backToTop = document.querySelector('.back-to-top');
if (backToTop) {
  const updateBackToTop = () => { backToTop.hidden = window.scrollY < 250; };
  window.addEventListener('scroll', updateBackToTop, { passive: true });
  updateBackToTop();
  backToTop.addEventListener('click', (event) => {
    event.preventDefault();
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.scrollTo({ top: 0, behavior: reducedMotion ? 'instant' : 'smooth' });
    document.querySelector('.government-brand')?.focus({ preventScroll: true });
  });
}

// O tradutor externo é carregado somente após a ativação explícita.
const vlibrasLaunch = document.getElementById('vlibras-launch');
const vlibrasDialog = document.getElementById('vlibras-consent');
const vlibrasEnable = document.getElementById('vlibras-enable');
const vlibrasStatus = document.getElementById('vlibras-connection-status');
vlibrasLaunch?.addEventListener('click', () => vlibrasDialog.showModal());
document.getElementById('vlibras-cancel')?.addEventListener('click', () => vlibrasDialog.close());
vlibrasDialog?.addEventListener('close', () => {
  if (!vlibrasLaunch.hidden) vlibrasLaunch.focus();
});
vlibrasEnable?.addEventListener('click', () => {
  if (vlibrasEnable.disabled) return;
  vlibrasEnable.disabled = true;
  vlibrasStatus.textContent = 'Carregando o VLibras…';
  const script = document.createElement('script');
  script.src = 'https://vlibras.gov.br/app/vlibras-plugin.js';
  script.async = true;
  script.id = 'vlibras-loader';
  script.addEventListener('load', () => {
    if (!window.VLibras?.Widget) {
      loadingFailed();
      return;
    }
    new window.VLibras.Widget('https://vlibras.gov.br/app');
    vlibrasLaunch.hidden = true;
    vlibrasDialog.close();
    window.VLibrasWidget?.open?.();
  });
  function loadingFailed() {
    vlibrasStatus.textContent = 'Não foi possível carregar o tradutor. Tente novamente ou acesse o site do VLibras.';
    vlibrasEnable.disabled = false;
    script.remove();
  }
  script.addEventListener('error', loadingFailed);
  document.head.appendChild(script);
});
