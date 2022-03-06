window.addEventListener('DOMContentLoaded', () => {
  // unpoly config adjustments
  // up.link.config.followSelectors.push('a[href]');
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
