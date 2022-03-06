async function notif(s, t) {
  new Noty({
    type: t,
    theme: 'relax',
    layout: 'topCenter',
    text: s,
    timeout: 4500
  }).show();
  return
}

window.addEventListener('DOMContentLoaded', () => {
  up.link.config.followSelectors.push('a[href]')
});
