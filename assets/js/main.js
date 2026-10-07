/* ============================================================
   NOVA AI — interaction layer
   Vanilla JS. Premium easing, rAF-driven scroll motion.
   ============================================================ */
(function () {
  "use strict";

  const doc = document;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const finePointer = window.matchMedia("(pointer: fine)").matches;

  const lerp = (a, b, t) => a + (b - a) * t;
  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
  const viewH = () => window.innerHeight || doc.documentElement.clientHeight;

  /* ---------- Preloader: film intro — counter, timecode, wipe reveal ---------- */
  const preloader = doc.getElementById("preloader");
  if (preloader) {
    const countEl = doc.getElementById("pl-count");
    const tcEl = doc.getElementById("pl-tc");
    const heroV = doc.querySelector(".hero-media video, .p-hero-media video");
    const start = performance.now();
    const DUR = 1800;      // counter run time
    const FPS = 30;
    const TOTAL_FRAMES = 45 * FPS; // a 45s reel timeline ticks during load
    let revealed = false;

    const fmtTC = (f) => {
      const ff = f % FPS;
      const s = Math.floor(f / FPS) % 60;
      const m = Math.floor(f / (FPS * 60)) % 60;
      const h = Math.floor(f / (FPS * 3600));
      return [h, m, s, ff].map((n) => String(n).padStart(2, "0")).join(":");
    };

    const reveal = () => {
      if (revealed) return;
      revealed = true;
      if (countEl) countEl.textContent = "100%";
      preloader.classList.add("reveal");
      doc.body.classList.add("loaded");
      window.dispatchEvent(new CustomEvent("nova:loaded"));
      // camera settle — quick zoom of the hero film as the wipe lands
      if (heroV && !reduceMotion) {
        const from = 1.15, dur = 950, t0 = performance.now();
        const step = (now) => {
          const p = Math.min(1, (now - t0) / dur);
          const e = 1 - Math.pow(1 - p, 3);
          heroV.style.transform = "scale(" + (from - (from - 1) * e) + ")";
          if (p < 1) requestAnimationFrame(step);
          else heroV.style.transform = "";
        };
        requestAnimationFrame(step);
      }
      setTimeout(() => preloader.classList.add("done"), 1400);
    };

    if (reduceMotion) {
      if (countEl) countEl.textContent = "100%";
      if (tcEl) tcEl.textContent = fmtTC(TOTAL_FRAMES);
      window.addEventListener("load", () => setTimeout(reveal, 0));
      setTimeout(reveal, 3200); // safety: never trap the user
    } else {
      let lastFrame = -1;
      const tick = (now) => {
        const p = Math.min(1, (now - start) / DUR);
        const e = 1 - Math.pow(1 - p, 3);
        if (countEl) countEl.textContent = Math.round(e * 100) + "%";
        const f = Math.round(e * TOTAL_FRAMES);
        if (f !== lastFrame) {
          lastFrame = f;
          if (tcEl) tcEl.textContent = fmtTC(f);
        }
        if (p < 1) requestAnimationFrame(tick);
        else setTimeout(reveal, 140);
      };
      requestAnimationFrame(tick);
      window.addEventListener("load", () => {
        const past = performance.now() - start;
        setTimeout(reveal, Math.max(0, DUR - past));
      });
      setTimeout(reveal, 3600); // safety: never trap the user
    }
  }

  /* ---------- Scroll progress ---------- */
  const bar = doc.querySelector(".scrollbar span");
  if (bar) {
    const updateBar = () => {
      const h = doc.documentElement.scrollHeight - viewH();
      const p = h > 0 ? window.scrollY / h : 0;
      bar.style.transform = `scaleX(${p})`;
    };
    window.addEventListener("scroll", updateBar, { passive: true });
    updateBar();
  }

  /* ---------- Nav state ---------- */
  const nav = doc.getElementById("nav");
  const onNavScroll = () => nav.classList.toggle("scrolled", window.scrollY > 30);
  window.addEventListener("scroll", onNavScroll, { passive: true });
  onNavScroll();

  /* ---------- Fullscreen menu ---------- */
  const burger = doc.getElementById("burger");
  const menu = doc.getElementById("menu");
  const lockBody = (on) => {
    doc.body.style.overflow = on ? "hidden" : "";
    doc.body.style.height = on ? "100svh" : "";
  };
  const setMenu = (open) => {
    if (!menu || !burger) return;
    menu.classList.toggle("open", open);
    menu.setAttribute("aria-hidden", String(!open));
    burger.classList.toggle("open", open);
    burger.setAttribute("aria-expanded", String(open));
    burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    lockBody(open);
  };
  if (burger) {
    burger.addEventListener("click", () => setMenu(!menu.classList.contains("open")));
    doc.addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });
    menu.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setMenu(false)));
  }

  /* ---------- Reveal on scroll ---------- */
  const revealEls = Array.from(doc.querySelectorAll("[data-reveal], .mask")).filter(
    (el) => !el.closest(".hero")
  );
  if ("IntersectionObserver" in window && !reduceMotion) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((en) => {
          if (en.isIntersecting) {
            en.target.classList.add("in");
            io.unobserve(en.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -7% 0px" }
    );
    revealEls.forEach((el) => io.observe(el));

    // gentle stagger inside multi-line headline masks
    const groups = new Map();
    doc.querySelectorAll(".mask").forEach((m) => {
      if (m.closest(".hero")) return;
      const parent = m.parentElement;
      if (!groups.has(parent)) groups.set(parent, []);
      groups.get(parent).push(m);
    });
    groups.forEach((ms) => {
      if (ms.length < 2) return;
      ms.forEach((m, i) => {
        if (m.firstElementChild) m.firstElementChild.style.transitionDelay = `${Math.min(i * 0.09, 0.45)}s`;
      });
    });
  } else {
    revealEls.forEach((el) => el.classList.add("in"));
  }

  /* ---------- Autoplay videos when visible ---------- */
  const autoVideos = doc.querySelectorAll("video[data-autoplay]");
  if ("IntersectionObserver" in window) {
    const vio = new IntersectionObserver(
      (entries) => {
        entries.forEach((en) => {
          const v = en.target;
          if (en.isIntersecting) {
            v.muted = true;
            const p = v.play();
            if (p && p.catch) p.catch(() => {});
          } else if (!v.matches(".no-pause")) {
            v.pause();
          }
        });
      },
      { threshold: 0.25 }
    );
    autoVideos.forEach((v) => vio.observe(v));
  }

  /* ---------- Work reel: hover to play ---------- */
  const reelItems = doc.querySelectorAll(".reel-item");
  reelItems.forEach((item) => {
    const video = item.querySelector("video");
    if (!video) return;
    const play = () => {
      if (reduceMotion) return;
      video.muted = true;
      video.load();
      const p = video.play();
      if (p && p.catch) p.catch(() => {});
    };
    const stop = () => { video.pause(); };
    if (finePointer) {
      item.addEventListener("mouseenter", play);
      item.addEventListener("mouseleave", stop);
    } else {
      // mobile: play a peek on tap via focus (navigation happens as well)
      item.querySelector("a").addEventListener("touchstart", play, { passive: true });
    }
  });

  /* ---------- Hero scroll drift ---------- */
  const hero = doc.querySelector(".hero");
  if (hero) {
    const heroTitle = hero.querySelector(".hero-title");
    const heroMedia = hero.querySelector(".hero-media");
    const onHeroScroll = () => {
      const y = window.scrollY;
      if (y > viewH() * 1.2) return;
      const p = clamp(y / viewH(), 0, 1);
      if (heroTitle) heroTitle.style.transform = `translateY(${p * 120}px)`;
      if (heroTitle) heroTitle.style.opacity = String(1 - p * 0.9);
      if (heroMedia) heroMedia.style.transform = `scale(${1 + p * 0.09})`;
    };
    window.addEventListener("scroll", onHeroScroll, { passive: true });
    onHeroScroll();
  }

  /* ---------- Parallax helpers ---------- */
  const parEls = doc.querySelectorAll("[data-parallax]");
  const parallax = () => {
    if (reduceMotion) return;
    parEls.forEach((el) => {
      const r = el.getBoundingClientRect();
      const speed = parseFloat(el.getAttribute("data-parallax")) || 0.15;
      const offset = (r.top + r.height / 2 - viewH() / 2) * -speed;
      el.style.transform = `translate3d(0, ${Math.round(offset * 10) / 10}px, 0)`;
    });
  };
  window.addEventListener("scroll", parallax, { passive: true });
  parallax();

  /* ---------- Showcase scroll choreography ---------- */
  const showcase = doc.querySelector(".showcase");
  if (showcase) {
    const sticky = showcase.querySelector(".showcase-sticky");
    const media = showcase.querySelector(".showcase-media video, .showcase-media img");
    const words = Array.from(showcase.querySelectorAll(".sw"));
    const onScroll = () => {
      const r = showcase.getBoundingClientRect();
      const total = showcase.clientHeight - viewH();
      const p = clamp(-r.top / total, 0, 1);
      if (media) media.style.transform = `scale(${1.18 - p * 0.14}) rotate(${(p - 0.5) * 1.2}deg)`;
      words.forEach((w, i) => {
        const t = clamp((p - i * 0.18) / 0.26, 0, 1);
        const e = 1 - Math.pow(1 - t, 3);
        w.style.opacity = String(e);
        w.style.transform = `translateY(${(1 - e) * 46}px) scale(${0.94 + e * 0.06})`;
        w.style.filter = `blur(${(1 - e) * 8}px)`;
      });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Featured media slow scale on view ---------- */
  const featMedia = doc.querySelectorAll(".p-hero-media");
  featMedia.forEach((el) => {
    const img = el.querySelector("video, img");
    if (!img) return;
    const upd = () => {
      const r = el.getBoundingClientRect();
      const p = clamp((viewH() - r.top) / (viewH() + r.height), 0, 1);
      img.style.transform = `scale(${1.05 + p * 0.05}) translate3d(0,${(1 - p) * -16}px,0)`;
    };
    window.addEventListener("scroll", upd, { passive: true });
    upd();
  });

  /* ---------- Accordions (services + faq) ---------- */
  doc.querySelectorAll("[data-accordion]").forEach((group) => {
    const items = group.querySelectorAll("[data-item]");
    items.forEach((item) => {
      const btn = item.querySelector("button");
      btn.addEventListener("click", () => {
        const isOpen = item.classList.contains("open");
        if (group.getAttribute("data-multi") !== "true") items.forEach((i) => i.classList.remove("open"));
        item.classList.toggle("open", !isOpen);
      });
    });
  });

  /* ---------- Magnetic buttons ---------- */
  const magnetic = doc.querySelectorAll(".magnetic");
  if (finePointer && !reduceMotion) {
    magnetic.forEach((el) => {
      const power = 0.22;
      el.addEventListener("mousemove", (e) => {
        const r = el.getBoundingClientRect();
        const dx = e.clientX - (r.left + r.width / 2);
        const dy = e.clientY - (r.top + r.height / 2);
        el.style.transform = `translate(${dx * power}px, ${dy * power}px)`;
      });
      el.addEventListener("mouseleave", () => {
        el.style.transform = "";
      });
    });
  }

  /* ---------- Hero headline entrance ---------- */
  const heroMasks = Array.from(doc.querySelectorAll(".hero-title .mask"));
  const heroLate = ["hero-eyebrow", "hero-sub", "hero-ctas"];
  const playHero = () => {
    if (!hero) return;
    if (reduceMotion) {
      heroMasks.forEach((m) => m.classList.add("in"));
      heroLate.forEach((c) => {
        const el = hero.querySelector("." + c);
        if (el) el.classList.add("in");
      });
      return;
    }
    heroMasks.forEach((m, i) => {
      if (m.firstElementChild) m.firstElementChild.style.transitionDelay = `${0.15 + i * 0.12}s`;
      m.classList.add("in");
    });
    heroLate.forEach((c, i) => {
      const el = hero.querySelector("." + c);
      if (el) {
        el.style.transitionDelay = `${0.55 + i * 0.14}s`;
        el.classList.add("in");
      }
    });
  };
  window.addEventListener("nova:loaded", playHero, { once: true });
  setTimeout(playHero, 1500); // safety fallback

  /* ---------- Contact form → WhatsApp ---------- */
  const cform = doc.getElementById("contact-form");
  if (cform) {
    const note = cform.querySelector(".form-note");
    const fields = Array.from(cform.querySelectorAll("input, textarea"));
    fields.forEach((f) => f.addEventListener("input", () => f.classList.remove("err")));
    cform.addEventListener("submit", (e) => {
      e.preventDefault();
      const values = {};
      fields.forEach((f) => { values[f.name] = f.value.trim(); });
      if (fields.some((f) => !f.value.trim())) {
        fields.forEach((f) => f.classList.toggle("err", !f.value.trim()));
        return;
      }
      const text =
        "New inquiry — NOVA AI website\n" +
        "Phone: " + values.phone + "\n" +
        "Email: " + values.email + "\n" +
        "Message: " + values.message;
      const link = doc.createElement("a");
      link.href = "https://wa.me/201282256742?text=" + encodeURIComponent(text);
      link.target = "_blank";
      link.rel = "noopener";
      doc.body.appendChild(link);
      link.click();
      link.remove();
      if (note) {
        note.textContent = "Opening WhatsApp…";
        note.classList.add("show");
        setTimeout(() => note.classList.remove("show"), 4000);
      }
    });
  }

  /* ---------- Footer year ---------- */
  const yr = doc.querySelectorAll("[data-year]");
  yr.forEach((el) => { el.textContent = new Date().getFullYear(); });
})();