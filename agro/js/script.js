/*AGRI-TOGO.FR - script.js*/
document.documentElement.classList.add('js');

(function () {
    'use strict';

    var bouton = document.getElementById('bouton-burger');
    if (!bouton) {
        return; // page sans menu hamburger
    }

    var enTete = bouton.closest('.en-tete');
    var navigation = document.getElementById('navigation-principale');
    var ouvert = false;

    /* Garde-fou : le bouton doit être dans un en-tête */
    if (!enTete) {
        return;
    }

    /* Ouvre (force = true) ou ferme (force = false) le menu, ou inverse
       l'état courant si force n'est pas fourni. */
    function basculer(force) {
        ouvert = (typeof force === 'boolean') ? force : !ouvert;

        bouton.setAttribute('aria-expanded', ouvert ? 'true' : 'false');
        bouton.setAttribute('aria-label', ouvert ? 'Fermer le menu' : 'Ouvrir le menu');

        if (ouvert) {
            enTete.classList.add('menu-ouvert');
        } else {
            enTete.classList.remove('menu-ouvert');
        }
    }

    /* Ouverture/fermeture au clic sur le bouton hamburger */
    bouton.addEventListener('click', function () {
        basculer();
    });

    /* Ferme le menu après un clic sur un lien de navigation */
    if (navigation) {
        var liens = navigation.querySelectorAll('a');
        var i;
        for (i = 0; i < liens.length; i++) {
            liens[i].addEventListener('click', function () {
                basculer(false);
            });
        }
    }

    /* Ferme le menu avec la touche Échap (accessibilité clavier) */
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' || e.key === 'Esc') {
            basculer(false);
        }
    });

    /* Replie le menu automatiquement en repassant en largeur desktop.
       Le point de rupture est défini dans le CSS (media query 640px) ; on
       le reflète ici via matchMedia pour rester synchronisé. */
    var requeteDesktop = window.matchMedia('(min-width: 641px)');
    window.addEventListener('resize', function () {
        if (ouvert && requeteDesktop.matches) {
            basculer(false);
        }
    });
})();


/* ==========================================================================
   Carrousel produits (page produit.html uniquement)
   --------------------------------------------------------------------------
   Galerie d'images animée en JavaScript natif : navigation précédent/
   suivant, points cliquables, défilement automatique (pause au survol et
   à la mise au point), navigation au clavier (flèches gauche/droite).
   ========================================================================== */
(function () {
    'use strict';

    var carrousel = document.getElementById('carrousel-produits');
    if (!carrousel) {
        return; // page sans carrousel
    }

    var piste = document.getElementById('carrousel-piste');
    var diapos = piste.querySelectorAll('.diapositive');
    var boutonPrecedent = carrousel.querySelector('.carrousel-precedent');
    var boutonSuivant = carrousel.querySelector('.carrousel-suivant');
    var points = carrousel.querySelectorAll('.carrousel-point');
    var legende = document.getElementById('carrousel-legende');
    var total = diapos.length;
    var index = 0;
    var temporisateur = null;
    var enPause = false;
    var INTERVALLE = 4000; // défilement automatique : 4 s par diapositive

    /* Carrousel avec moins de 2 diapositives : rien à animer */
    if (total < 2) {
        return;
    }

    /* Affiche la diapositive n (boucle circulaire), met à jour les points
       actifs et la légende. */
    function afficher(n) {
        index = ((n % total) + total) % total;
        piste.style.transform = 'translateX(-' + (index * 100) + '%)';

        var i;
        for (i = 0; i < points.length; i++) {
            if (i === index) {
                points[i].classList.add('actif');
                points[i].setAttribute('aria-current', 'true');
            } else {
                points[i].classList.remove('actif');
                points[i].setAttribute('aria-current', 'false');
            }
        }

        if (legende && diapos[index]) {
            var titre = diapos[index].getAttribute('data-titre');
            if (titre) {
                legende.textContent = titre;
            }
        }

        /* Seule la diapositive courante doit être lue par les lecteurs
           d'écran : les autres sont masquées d'un point de vue ARIA */
        var d;
        for (d = 0; d < diapos.length; d++) {
            if (d === index) {
                diapos[d].setAttribute('aria-hidden', 'false');
            } else {
                diapos[d].setAttribute('aria-hidden', 'true');
            }
        }
    }

    /* Les interactions manuelles (boutons et points) redémarrent le
       décompte pour éviter un double défilement juste après un clic */
    function diapositiveSuivante() { afficher(index + 1); demarrerDefilement(); }
    function diapositivePrecedente() { afficher(index - 1); demarrerDefilement(); }

    function arreterDefilement() {
        if (temporisateur) {
            clearInterval(temporisateur);
            temporisateur = null;
        }
    }

    function demarrerDefilement() {
        arreterDefilement();
        temporisateur = setInterval(function () {
            if (!enPause) {
                afficher(index + 1);
            }
        }, INTERVALLE);
    }

    if (boutonSuivant) {
        boutonSuivant.addEventListener('click', diapositiveSuivante);
    }
    if (boutonPrecedent) {
        boutonPrecedent.addEventListener('click', diapositivePrecedente);
    }

    var j;
    for (j = 0; j < points.length; j++) {
        (function (k) {
            points[k].addEventListener('click', function () {
                afficher(k);
                demarrerDefilement(); // redémarre le décompte après un clic
            });
        })(j);
    }

    /* Pause du défilement automatique au survol ou à la mise au point */
    carrousel.addEventListener('mouseenter', function () { enPause = true; });
    carrousel.addEventListener('mouseleave', function () { enPause = false; });
    carrousel.addEventListener('focusin', function () { enPause = true; });
    carrousel.addEventListener('focusout', function () { enPause = false; });

    /* Navigation au clavier (flèches gauche/droite) quand le carrousel
       (ou l'un de ses boutons) a le focus */
    carrousel.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight') {
            e.preventDefault();
            diapositiveSuivante();
        } else if (e.key === 'ArrowLeft') {
            e.preventDefault();
            diapositivePrecedente();
        }
    });

    afficher(0);
    demarrerDefilement();
})();


/* ==========================================================================
   Animations au défilement (scroll reveal) — toutes les pages
    */
(function () {
    'use strict';

    var elements = document.querySelectorAll('.reveal');
    var i;

    /* Pas d'observateur disponible ou mouvement réduit : on affiche tout
       immédiatement, sans animation. */
    if (!('IntersectionObserver' in window) ||
        window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
        elements.length === 0) {
        for (i = 0; i < elements.length; i++) {
            elements[i].classList.add('reveal-visible');
        }
        return;
    }

    var observateur = new IntersectionObserver(function (entrees) {
        var j;
        for (j = 0; j < entrees.length; j++) {
            if (entrees[j].isIntersecting) {
                entrees[j].target.classList.add('reveal-visible');
                observateur.unobserve(entrees[j].target); // une seule fois
            }
        }
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

    for (i = 0; i < elements.length; i++) {
        observateur.observe(elements[i]);
    }
})();


/* ==========================================================================
   Mode sombre / clair — toutes les pages
   --------------------------------------------------------------------------
 */
(function () {
    'use strict';

    var bouton = document.getElementById('bouton-theme');
    var racine = document.documentElement;
    var CLE = 'agri-togo-theme';

    if (!bouton) {
        return; // page sans bouton de thème
    }

    function appliquer(theme) {
        if (theme === 'sombre') {
            racine.setAttribute('data-theme', 'sombre');
            bouton.setAttribute('aria-label', 'Activer le mode clair');
        } else {
            racine.removeAttribute('data-theme');
            bouton.setAttribute('aria-label', 'Activer le mode sombre');
        }
    }

    /* Thème mémorisé, sinon préférence système, sinon clair par défaut */
    var memorise = null;
    try {
        memorise = localStorage.getItem(CLE);
    } catch (e) {
        /* stockage indisponible (navigation privée, etc.) */
    }

    var themeInitial;
    if (memorise === 'sombre' || memorise === 'clair') {
        themeInitial = memorise;
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        themeInitial = 'sombre';
    } else {
        themeInitial = 'clair';
    }
    appliquer(themeInitial);

    bouton.addEventListener('click', function () {
        var nouveau = racine.getAttribute('data-theme') === 'sombre' ? 'clair' : 'sombre';
        appliquer(nouveau);
        try {
            localStorage.setItem(CLE, nouveau);
        } catch (e) {
            /* stockage indisponible */
        }
    });
})();
