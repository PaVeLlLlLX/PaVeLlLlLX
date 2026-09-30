(() => {
  document.documentElement.classList.add('js');

  const canvas = document.getElementById('particle-field');
  const context = canvas.getContext('2d', { alpha: true });
  const progress = document.querySelector('.scroll-progress');
  const art = document.querySelector('.hero-art');
  const year = document.getElementById('year');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const palette = ['121,240,210', '125,201,255', '189,173,255', '255,189,152'];
  const pointer = { x: -1000, y: -1000 };
  let points = [];
  let width = 0;
  let height = 0;
  let lastScroll = window.scrollY;
  let scrollImpulse = 0;
  let lastFrame = performance.now();

  year.textContent = new Date().getFullYear();

  const random = (low, high) => low + Math.random() * (high - low);
  const clamp = (value, low, high) => Math.max(low, Math.min(high, value));

  function makePoint() {
    return {
      x: random(0, width),
      y: random(0, height),
      vx: random(-0.16, 0.16),
      vy: random(-0.2, 0.2),
      radius: random(1, 2.7),
      depth: random(.35, 1.4),
      color: palette[Math.floor(random(0, palette.length))]
    };
  }

  function resize() {
    const density = Math.min(window.devicePixelRatio || 1, 2);
    width = document.documentElement.clientWidth;
    height = window.innerHeight;
    canvas.width = Math.round(width * density);
    canvas.height = Math.round(height * density);
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    context.setTransform(density, 0, 0, density, 0, 0);
    const count = reducedMotion.matches ? 32 : clamp(Math.round(width * height / 13000), 36, 95);
    points = Array.from({ length: count }, makePoint);
    draw();
  }

  function draw() {
    context.clearRect(0, 0, width, height);
    const reach = width < 680 ? 105 : 145;
    const reachSquared = reach * reach;
    const energy = Math.min(1, Math.abs(scrollImpulse) / 17);

    for (let i = 0; i < points.length; i += 1) {
      const a = points[i];
      for (let j = i + 1; j < points.length; j += 1) {
        const b = points[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const distance = dx * dx + dy * dy;
        if (distance < reachSquared) {
          const opacity = (1 - distance / reachSquared) * (.12 + energy * .13);
          context.strokeStyle = 'rgba(121, 240, 210, ' + opacity.toFixed(3) + ')';
          context.lineWidth = .8;
          context.beginPath();
          context.moveTo(a.x, a.y);
          context.lineTo(b.x, b.y);
          context.stroke();
        }
      }
    }

    for (const point of points) {
      const glow = point.radius * (4 + energy * 1.8);
      const gradient = context.createRadialGradient(point.x, point.y, 0, point.x, point.y, glow);
      gradient.addColorStop(0, 'rgba(' + point.color + ', ' + (.42 + energy * .18).toFixed(3) + ')');
      gradient.addColorStop(1, 'rgba(' + point.color + ', 0)');
      context.fillStyle = gradient;
      context.beginPath();
      context.arc(point.x, point.y, glow, 0, Math.PI * 2);
      context.fill();
      context.fillStyle = 'rgba(' + point.color + ', .78)';
      context.beginPath();
      context.arc(point.x, point.y, point.radius, 0, Math.PI * 2);
      context.fill();
    }
  }

  function move(delta) {
    for (const point of points) {
      point.x += point.vx * delta;
      point.y += point.vy * delta + scrollImpulse * point.depth * .17;
      const dx = point.x - pointer.x;
      const dy = point.y - pointer.y;
      const distance = dx * dx + dy * dy;
      if (distance < 135 * 135 && distance > 1) {
        const force = (1 - Math.sqrt(distance) / 135) * .65 * delta;
        point.x += dx / Math.sqrt(distance) * force;
        point.y += dy / Math.sqrt(distance) * force;
      }
      if (point.x < -12) point.x = width + 12;
      if (point.x > width + 12) point.x = -12;
      if (point.y < -12) point.y = height + 12;
      if (point.y > height + 12) point.y = -12;
    }
    scrollImpulse *= .9;
  }

  function frame(now) {
    if (document.visibilityState === 'visible' && !reducedMotion.matches) {
      const delta = clamp((now - lastFrame) / 16.67, .3, 2.5);
      move(delta);
      draw();
    }
    lastFrame = now;
    window.requestAnimationFrame(frame);
  }

  function onScroll() {
    const current = window.scrollY;
    const change = clamp(current - lastScroll, -100, 100);
    lastScroll = current;
    scrollImpulse = clamp(scrollImpulse + change * .22, -24, 24);
    const maximum = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    progress.style.transform = 'scaleX(' + clamp(current / maximum, 0, 1) + ')';
    if (!reducedMotion.matches) {
      art.style.transform = 'translate3d(0, ' + Math.min(95, current * .12) + 'px, 0)';
    }
  }

  const revealItems = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reducedMotion.matches) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      }
    }, { threshold: .09, rootMargin: '0px 0px -40px 0px' });
    revealItems.forEach(item => observer.observe(item));
  } else {
    revealItems.forEach(item => item.classList.add('is-visible'));
  }

  window.addEventListener('resize', resize, { passive: true });
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('pointermove', event => {
    pointer.x = event.clientX;
    pointer.y = event.clientY;
  }, { passive: true });
  window.addEventListener('pointerleave', () => {
    pointer.x = -1000;
    pointer.y = -1000;
  });
  reducedMotion.addEventListener('change', () => {
    resize();
    revealItems.forEach(item => item.classList.add('is-visible'));
    if (reducedMotion.matches) art.style.transform = '';
  });

  resize();
  onScroll();
  window.requestAnimationFrame(frame);
})();
