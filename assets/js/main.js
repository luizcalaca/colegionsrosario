/* Colégio Nossa Senhora do Rosário — comportamentos de interface */
(function () {
  'use strict';

  var header = document.querySelector('.site-header');
  var nav = document.querySelector('.nav');
  var toggle = document.querySelector('.nav-toggle');
  var items = Array.prototype.slice.call(document.querySelectorAll('.nav-item'));
  var mq = window.matchMedia('(max-width: 1000px)');

  /* Sombra no cabeçalho ao rolar */
  if (header) {
    var onScroll = function () {
      header.classList.toggle('is-stuck', window.scrollY > 8);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* Menu mobile */
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.classList.toggle('is-active', open);
      toggle.setAttribute('aria-expanded', String(open));
      document.body.style.overflow = open ? 'hidden' : '';
    });
  }

  var closeAll = function (except) {
    items.forEach(function (item) {
      if (item === except) return;
      item.classList.remove('is-open');
      var btn = item.querySelector('.nav-link');
      if (btn && btn.tagName === 'BUTTON') btn.setAttribute('aria-expanded', 'false');
    });
  };

  /* Submenus: hover no desktop, clique no mobile — sempre acessíveis por teclado */
  items.forEach(function (item) {
    var btn = item.querySelector('.nav-link');
    if (!item.querySelector('.submenu') || !btn) return;

    /* No desktop o hover já abre o submenu; o clique imediatamente seguinte
       não deve fechá-lo — apenas confirma a abertura. */
    var openedByHover = false;

    btn.addEventListener('click', function (e) {
      e.preventDefault();
      if (openedByHover) { openedByHover = false; return; }
      var open = !item.classList.contains('is-open');
      closeAll(item);
      item.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', String(open));
    });

    item.addEventListener('mouseenter', function () {
      if (mq.matches) return;
      closeAll(item);
      openedByHover = !item.classList.contains('is-open');
      item.classList.add('is-open');
      btn.setAttribute('aria-expanded', 'true');
    });
    item.addEventListener('mouseleave', function () {
      if (mq.matches) return;
      openedByHover = false;
      item.classList.remove('is-open');
      btn.setAttribute('aria-expanded', 'false');
    });
    item.addEventListener('focusout', function (e) {
      if (mq.matches) return;
      if (!item.contains(e.relatedTarget)) {
        item.classList.remove('is-open');
        btn.setAttribute('aria-expanded', 'false');
      }
    });
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-item')) closeAll(null);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeAll(null);
  });

  /* Acordeões */
  document.querySelectorAll('.acc-head').forEach(function (head) {
    head.addEventListener('click', function () {
      var acc = head.parentElement;
      var open = acc.classList.toggle('is-open');
      head.setAttribute('aria-expanded', String(open));
    });
  });

  /* Revelar elementos ao entrar na viewport */
  var targets = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && targets.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: .12 });
    targets.forEach(function (t) { io.observe(t); });
  } else {
    targets.forEach(function (t) { t.classList.add('is-visible'); });
  }

  /* ------------------------------------------------------------------
     Materiais: player de áudio com botão de play, título e barra
     ------------------------------------------------------------------ */
  var players = [].slice.call(document.querySelectorAll('.audio-item'));

  var formatarTempo = function (segundos) {
    if (!isFinite(segundos) || segundos < 0) return '--:--';
    var m = Math.floor(segundos / 60);
    var s = Math.floor(segundos % 60);
    return m + ':' + (s < 10 ? '0' : '') + s;
  };

  players.forEach(function (item) {
    var audio = item.querySelector('.audio-fonte');
    var botao = item.querySelector('.audio-play');
    var barra = item.querySelector('.audio-barra');
    var progresso = item.querySelector('.audio-progresso');
    var atual = item.querySelector('.audio-atual');
    var total = item.querySelector('.audio-total');
    var titulo = item.querySelector('.audio-titulo');
    if (!audio || !botao) return;

    var nome = titulo ? titulo.textContent.trim() : 'áudio';

    var mostrarDuracao = function () {
      if (total) total.textContent = formatarTempo(audio.duration);
    };
    if (audio.readyState >= 1) mostrarDuracao();
    audio.addEventListener('loadedmetadata', mostrarDuracao);

    botao.addEventListener('click', function () {
      if (audio.paused) {
        /* Um áudio por vez: pausa os demais antes de tocar este. */
        players.forEach(function (outro) {
          if (outro === item) return;
          var a = outro.querySelector('.audio-fonte');
          if (a && !a.paused) a.pause();
        });
        audio.play().catch(function () {
          if (total) total.textContent = 'erro';
          botao.setAttribute('aria-label', 'Não foi possível tocar ' + nome);
        });
      } else {
        audio.pause();
      }
    });

    audio.addEventListener('play', function () {
      item.classList.add('is-tocando');
      botao.setAttribute('aria-label', 'Pausar ' + nome);
    });

    var aoParar = function () {
      item.classList.remove('is-tocando');
      botao.setAttribute('aria-label', 'Tocar ' + nome);
    };
    audio.addEventListener('pause', aoParar);
    audio.addEventListener('ended', function () {
      aoParar();
      audio.currentTime = 0;
    });

    audio.addEventListener('timeupdate', function () {
      var fracao = audio.duration ? audio.currentTime / audio.duration : 0;
      if (progresso) progresso.style.width = (fracao * 100) + '%';
      if (atual) atual.textContent = formatarTempo(audio.currentTime);
      if (barra) barra.setAttribute('aria-valuenow', Math.round(fracao * 100));
    });

    /* Clique na barra posiciona o áudio */
    var posicionar = function (clientX) {
      if (!audio.duration) return;
      var r = barra.getBoundingClientRect();
      var fracao = Math.min(Math.max((clientX - r.left) / r.width, 0), 1);
      audio.currentTime = fracao * audio.duration;
    };
    if (barra) {
      barra.addEventListener('click', function (e) { posicionar(e.clientX); });

      /* Mesma navegação pelo teclado, já que a barra é um slider */
      barra.addEventListener('keydown', function (e) {
        if (!audio.duration) return;
        var passo = 5;
        if (e.key === 'ArrowRight') audio.currentTime = Math.min(audio.currentTime + passo, audio.duration);
        else if (e.key === 'ArrowLeft') audio.currentTime = Math.max(audio.currentTime - passo, 0);
        else if (e.key === 'Home') audio.currentTime = 0;
        else if (e.key === 'End') audio.currentTime = audio.duration;
        else return;
        e.preventDefault();
      });
    }
  });

  /* Formulários: em vez de um back-end, montam uma mensagem organizada e abrem
     a conversa com o WhatsApp da Secretaria já preenchida. */
  document.querySelectorAll('form[data-form]').forEach(function (form) {
    var numero = form.getAttribute('data-whatsapp');

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;

      var val = function (name) {
        var el = form.elements[name];
        return el && el.value ? el.value.trim() : '';
      };

      var linhas = ['*Contato pelo site — Colégio N. Sra. do Rosário*', ''];
      [
        ['Nome', val('nome')],
        ['E-mail', val('email')],
        ['Telefone', val('telefone')],
        ['Assunto', val('assunto')]
      ].forEach(function (par) {
        if (par[1]) linhas.push('*' + par[0] + ':* ' + par[1]);
      });

      var mensagem = val('mensagem');
      if (mensagem) linhas.push('', '*Mensagem:*', mensagem);

      var feedback = form.querySelector('.form-feedback');
      if (!numero) {
        if (feedback) {
          feedback.textContent = 'Não foi possível abrir o WhatsApp. Ligue para a Secretaria.';
          feedback.style.color = '#B3261E';
        }
        return;
      }

      var url = 'https://wa.me/' + numero + '?text=' + encodeURIComponent(linhas.join('\n'));
      var aba = window.open(url, '_blank', 'noopener');

      if (feedback) {
        feedback.style.color = '#1B3468';
        feedback.textContent = aba
          ? 'Abrimos o WhatsApp da Secretaria com sua mensagem pronta. Confirme o envio por lá.'
          : 'Seu navegador bloqueou a janela do WhatsApp. Libere o pop-up e tente novamente.';
      }
      /* O formulário só é limpo quando a janela abriu — assim o texto não se
         perde se o pop-up for bloqueado. */
      if (aba) form.reset();
    });
  });
})();
