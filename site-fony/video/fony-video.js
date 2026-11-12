/* 90-video.js — Vidéos produit : lues seulement quand elles sont à l'écran, en boucle et sans son.
   Rien ne se lance pour qui préfère moins d'animations ou a activé l'économie de données :
   l'image d'aperçu reste affichée avec un bouton « Lire ». Sans script : vidéo avec ses contrôles. */
(function () {
  var videos = document.querySelectorAll('video[data-fony-video]'); if (!videos.length) return;
  var calme = false;
  try { calme = matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  if (navigator.connection && navigator.connection.saveData) calme = true;

  Array.prototype.forEach.call(videos, function (v) {
    v.muted = true; v.removeAttribute('controls');
    var cadre = v.closest('.video-produit');
    if (calme || !('IntersectionObserver' in window)) {
      if (cadre) cadre.classList.add('video-produit--a-lire');
      var bouton = cadre && cadre.querySelector('.video-produit-lire');
      if (bouton) bouton.addEventListener('click', function () {
        cadre.classList.remove('video-produit--a-lire'); v.setAttribute('controls', ''); v.play();
      });
      return;
    }
    var o = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { if (v.preload === 'none') v.preload = 'auto'; var p = v.play(); if (p && p.catch) p.catch(function () {}); }
        else v.pause();
      });
    }, { threshold: 0.35 });
    o.observe(v);
  });
})();
