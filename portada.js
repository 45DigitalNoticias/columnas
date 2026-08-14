/* Portada de 45 Digital Noticias. Los datos (COLUMNAS, PORTADAS) los
   inyecta _generar_portada.py justo antes de este archivo. */
(() => {
  const RUTA = '';
  const DWELL = 7000;
  // COLUMNAS y PORTADAS los inyecta _generar_portada.py

  /* ---------- el panel ---------- */
  const mgrid = document.getElementById('mgrid');
  /* Se construye a la medida del hero: columnas fijas y las filas que
     hagan falta para cubrir el alto exacto. Con las dos en 1fr no queda
     hueco ni sobra, que es lo que lo vuelve panel y no mosaico.
     Paso 17 al recorrer las 45: 17 y 45 son coprimos, así que pasa por
     todas sin repetir. Probé los 24 pasos posibles contando cuántas
     piezas vecinas comparten familia de color: el orden seguido da 20
     choques, el paso 7 da 7, y el 17 da 5. Ese es el que va. */
  const THUMB = f => 'thumbs/' + f;

  function armarPanel() {
    const caja = document.querySelector('.portada').getBoundingClientRect();
    // 18 columnas a 1440 => pieza de ~80px. En pantallas menores se
    // conserva ese tamaño de pieza, no el número de columnas: así el
    // grano del panel se ve igual de fino en cualquier ancho.
    const cols = Math.max(4, Math.round(caja.width / 80));
    const rows = Math.max(3, Math.round(caja.height / ((caja.width / cols) * 0.78)));
    mgrid.style.setProperty('--cols', cols);
    mgrid.style.setProperty('--rows', rows);

    const total = cols * rows;
    if (mgrid.childElementCount === total) return;   // nada que rehacer
    mgrid.textContent = '';
    for (let i = 0; i < total; i++) {
      const img = document.createElement('img');
      img.src = THUMB(PORTADAS[(i * 17) % PORTADAS.length]);
      img.alt = ''; img.decoding = 'async';
      mgrid.appendChild(img);
    }
  }
  armarPanel();
  let reloj2; addEventListener('resize', () => {
    clearTimeout(reloj2); reloj2 = setTimeout(armarPanel, 200);
  });

  /* ---------- destacada + tira ---------- */
  const destacada = document.getElementById('destacada');
  const activa    = document.getElementById('activa');
  const tabs      = document.getElementById('tabs');
  const rotador   = document.getElementById('rotador');
  rotador.style.setProperty('--dwell', DWELL + 'ms');

  COLUMNAS.forEach((c, i) => {
    const s = document.createElement('article');
    s.className = 'slide' + (i === 0 ? ' on' : '');
    s.innerHTML = `
      <div class="eyebrow">
        <span class="tick"></span>
        ${c.nueva ? '<span class="nueva">Nueva</span>' : '<span class="label">Columna destacada</span>'}
        <span class="meta" style="color:rgba(242,239,233,.5)">${c.tema}</span>
      </div>
      <h1>${c.t}</h1>
      <p class="standfirst">${c.d}</p>
      <div class="byline">
        <span class="firma">SRVO</span><span class="sep"></span>
        <span class="meta">${c.fecha}</span><span class="sep"></span>
        <span class="meta">${c.min}</span>
      </div>
      <a class="chev" href="${RUTA + c.href}">Leer la columna <i>›</i></a>`;
    destacada.appendChild(s);

    const img = document.createElement('img');
    img.src = RUTA + c.img; img.alt = ''; img.className = i === 0 ? 'on' : '';
    activa.appendChild(img);

    const tab = document.createElement('button');
    tab.className = 'tab'; tab.type = 'button'; tab.setAttribute('role','tab');
    tab.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
    tab.innerHTML = `<span class="n">${String(i+1).padStart(2,'0')}</span><span class="t">${c.t}</span><span class="barra"></span>`;
    tab.addEventListener('click', () => ir(i, true));
    tabs.appendChild(tab);
  });

  const slides = [...destacada.children], imgs = [...activa.children], botones = [...tabs.children];
  let actual = 0, reloj = null;
  const quieto = matchMedia('(prefers-reduced-motion: reduce)').matches;

  function ir(i, manual) {
    if (i === actual) return;
    slides[actual].classList.remove('on'); imgs[actual].classList.remove('on');
    botones[actual].setAttribute('aria-selected','false');
    const b = botones[actual].querySelector('.barra');
    b.style.transition = 'none'; b.style.width = '0';
    requestAnimationFrame(() => { b.style.transition = ''; b.style.width = ''; });
    actual = i;
    slides[i].classList.add('on'); imgs[i].classList.add('on');
    botones[i].setAttribute('aria-selected','true');
    if (manual) arranca();
  }
  const siguiente = () => ir((actual + 1) % COLUMNAS.length);
  function arranca(){ clearInterval(reloj); if (!quieto) reloj = setInterval(siguiente, DWELL); }
  function detiene(){ clearInterval(reloj); rotador.classList.add('pausa'); }
  function reanuda(){ rotador.classList.remove('pausa'); arranca(); }

  rotador.addEventListener('mouseenter', detiene);
  rotador.addEventListener('mouseleave', reanuda);
  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight') ir((actual + 1) % COLUMNAS.length, true);
    if (e.key === 'ArrowLeft')  ir((actual - 1 + COLUMNAS.length) % COLUMNAS.length, true);
  });
  document.addEventListener('visibilitychange', () => document.hidden ? clearInterval(reloj) : arranca());
  arranca();

  /* ============================================================
     ARCHIVO · escuchar sin salir de la página
     87 de las 93 columnas ya tienen su mp3 en el servidor.
     Un solo elemento <audio> reutilizado: nunca suenan dos a la vez.
     ============================================================ */
  const audio = new Audio();
  let sonando = null;

  function apaga(){
    if (!sonando) return;
    sonando.classList.remove('suena');
    sonando.querySelector('.pista').style.width = '0';
    sonando = null;
  }

  document.querySelectorAll('.fila').forEach(fila => {
    // la fila entera navega, salvo cuando el clic cae en el botón de audio
    fila.addEventListener('click', e => {
      if (e.target.closest('.oir')) return;
      location.href = RUTA + fila.dataset.href;
    });

    fila.querySelector('.oir').addEventListener('click', () => {
      const mismo = sonando === fila;
      apaga();
      if (mismo) { audio.pause(); return; }
      audio.src = RUTA + fila.dataset.audio;
      audio.play().catch(() => {});   // si el archivo no está, no rompe la página
      sonando = fila;
      fila.classList.add('suena');
    });
  });

  audio.addEventListener('timeupdate', () => {
    if (!sonando || !audio.duration) return;
    sonando.querySelector('.pista').style.width = (audio.currentTime / audio.duration * 100) + '%';
  });
  audio.addEventListener('ended', apaga);

  /* ============================================================
     ARCHIVO · filtros por tema y búsqueda
     ============================================================ */
  const filas  = [...document.querySelectorAll('.fila')];
  const busca  = document.querySelector('.busca');
  let tema = 'all';

  function filtra(){
    const q = busca.value.trim().toLowerCase();
    filas.forEach(f => {
      const okTema = tema === 'all' || f.dataset.t === tema;
      const okTexto = !q || f.textContent.toLowerCase().includes(q);
      f.hidden = !(okTema && okTexto);
    });
  }

  document.querySelectorAll('.f').forEach(b => b.addEventListener('click', () => {
    document.querySelectorAll('.f').forEach(x => x.classList.remove('on'));
    b.classList.add('on'); tema = b.dataset.t; filtra();
  }));
  busca.addEventListener('input', filtra);

  /* ============================================================
     COMPARTIR — las URL se arman al vuelo con la dirección real
     de la página, así que funciona igual en local y publicado.
     ============================================================ */
  const URL_SITIO = 'https://45digitalnoticias.github.io/columnas/';
  const u = encodeURIComponent(URL_SITIO);
  const t = encodeURIComponent('45 Digital Noticias · Columnas. Lecturas que conjuntan lo que en apariencia no tiene relación.');
  const DESTINOS = {
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${u}`,
    whatsapp: `https://api.whatsapp.com/send?text=${t}%20${u}`,
    x:        `https://twitter.com/intent/tweet?text=${t}&url=${u}`
  };

  document.querySelectorAll('.btn-red').forEach(b => {
    const red = b.dataset.red;
    if (DESTINOS[red]) {
      b.href = DESTINOS[red]; b.target = '_blank'; b.rel = 'noopener';
      return;
    }
    b.addEventListener('click', async () => {
      const tip = b.querySelector('.tip');
      try { await navigator.clipboard.writeText(URL_SITIO); }
      catch { return; }                      // sin permiso de portapapeles: no finge que copió
      const antes = tip.textContent;
      tip.textContent = 'Copiado'; b.classList.add('copiado');
      setTimeout(() => { tip.textContent = antes; b.classList.remove('copiado'); }, 1800);
    });
  });
})();
