window.addEventListener('DOMContentLoaded', () => {
  // unpoly config adjustments
  up.fragment.config.mainTargets.push('.container');
});

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
