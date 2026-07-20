/* global frappe */
(function () {
	const STORAGE_LANG = "nursery_site_lang";

	const DEFAULT_CATALOG = {
		programs: [
			{ key: "infant", name_ar: "حضانة الأطفال", name_en: "Infant Care", icon: "👶", age: "0-2 years" },
			{ key: "toddler", name_ar: "الروضة", name_en: "Toddler Program", icon: "🧸", age: "2-4 years" },
			{ key: "preschool", name_ar: "ما قبل المدرسة", name_en: "Preschool", icon: "🎨", age: "4-6 years" },
			{ key: "after_school", name_ar: "برنامج بعد المدرسة", name_en: "After School", icon: "📚", age: "6-12 years" },
		],
		features: [
			{ icon: "👩‍🏫", ar: "معلمون مؤهلون", en: "Qualified Teachers" },
			{ icon: "🍎", ar: "وجبات صحية", en: "Healthy Meals" },
			{ icon: "🔒", ar: "أمان وحماية", en: "Safe Environment" },
			{ icon: "🎮", ar: "أنشطة تعليمية", en: "Learning Activities" },
			{ icon: "📱", ar: "تطبيق أولياء الأمور", en: "Parent App" },
			{ icon: "🏥", ar: "رعاية صحية", en: "Healthcare Support" },
		],
	};

	window.NurserySite = {
		config: null,
		lang: localStorage.getItem(STORAGE_LANG) || "ar",
		page: "home",

		init(page) {
			this.page = page || "home";
			this.config = this.defaultConfig();
			this.applyTheme();
			this.renderChrome();
			this.loadConfig()
				.then(() => {
					this.applyTheme();
					this.renderChrome();
					const fn = this[`init_${this.page}`];
					if (typeof fn === "function") fn.call(this);
					this.setupReveal();
				})
				.catch(() => {
					this.config = this.config || this.defaultConfig();
					this.renderChrome();
					const fn = this[`init_${this.page}`];
					if (typeof fn === "function") fn.call(this);
					this.setupReveal();
				});
		},

		defaultConfig() {
			return {
				brand_name_ar: "Omnexa Nursery",
				brand_name_en: "Omnexa Nursery",
				tagline_ar: "رعاية تعليمية آمنة ومحبة لأطفالكم",
				tagline_en: "Safe, loving educational care for your children",
				hero_text_ar: "من الرعاية المبكرة إلى ما قبل المدرسة — بيئة آمنة ومحبة لنمو طفلك",
				hero_text_en: "From infant care to preschool — a safe, loving environment for your child's growth",
				hero_image: "https://images.unsplash.com/photo-1587654780291-39c9404d746b?auto=format&fit=crop&w=1920&q=85",
				logo: "/assets/omnexa_nursery/logo.png",
				primary_color: "#e91e63",
				secondary_color: "#9c27b0",
				accent_color: "#00bcd4",
				gold_color: "#ffc107",
				programs: DEFAULT_CATALOG.programs,
				features: DEFAULT_CATALOG.features,
				stats: { children: 500, teachers: 50, families: 300, years: 10 },
			};
		},

		t(key) {
			const map = {
				home: { ar: "الرئيسية", en: "Home" },
				programs: { ar: "البرامج", en: "Programs" },
				features: { ar: "المميزات", en: "Features" },
				contact: { ar: "تواصل", en: "Contact" },
				login: { ar: "دخول", en: "Login" },
				enroll: { ar: "سجل الآن", en: "Enroll Now" },
				learn_more: { ar: "اعرف المزيد", en: "Learn More" },
				children: { ar: "طفل", en: "Children" },
				teachers: { ar: "معلم", en: "Teachers" },
				families: { ar: "عائلة", en: "Families" },
				years: { ar: "سنة", en: "Years" },
				loading: { ar: "جاري التحميل...", en: "Loading..." },
			};
			return (map[key] && map[key][this.lang]) || key;
		},

		esc(v) {
			if (typeof frappe !== "undefined" && frappe.utils && frappe.utils.escape_html) {
				return frappe.utils.escape_html(v == null ? "" : String(v));
			}
			const d = document.createElement("div");
			d.textContent = v == null ? "" : String(v);
			return d.innerHTML;
		},

		nameField() {
			return this.lang === "ar" ? "brand_name_ar" : "brand_name_en";
		},

		textField(base) {
			return this.lang === "ar" ? `${base}_ar` : `${base}_en`;
		},

		async loadConfig() {
			try {
				if (typeof frappe !== "undefined" && frappe.call) {
					const r = await frappe.call({
						method: "omnexa_nursery.api.public_nursery_site.get_site_config",
					});
					this.config = Object.assign(this.defaultConfig(), r.message || {});
				} else {
					const res = await fetch("/api/method/omnexa_nursery.api.public_nursery_site.get_site_config");
					const data = await res.json();
					this.config = Object.assign(this.defaultConfig(), data.message || {});
				}
			} catch (e) {
				this.config = this.config || this.defaultConfig();
			}
			if (this.config.primary_color) {
				document.documentElement.style.setProperty("--nursery-primary", this.config.primary_color);
			}
			if (this.config.secondary_color) {
				document.documentElement.style.setProperty("--nursery-secondary", this.config.secondary_color);
			}
			if (this.config.accent_color) {
				document.documentElement.style.setProperty("--nursery-teal", this.config.accent_color);
			}
			if (this.config.gold_color) {
				document.documentElement.style.setProperty("--nursery-gold", this.config.gold_color);
			}
		},

		applyTheme() {
			const root = document.querySelector(".nursery-site");
			if (!root) return;
			root.dir = this.lang === "ar" ? "rtl" : "ltr";
			root.lang = this.lang;
		},

		toggleLang() {
			this.lang = this.lang === "ar" ? "en" : "ar";
			localStorage.setItem(STORAGE_LANG, this.lang);
			this.applyTheme();
			this.renderChrome();
			const fn = this[`init_${this.page}`];
			if (typeof fn === "function") fn.call(this);
		},

		setupReveal() {
			const els = document.querySelectorAll(".nursery-reveal");
			if (!els.length || !("IntersectionObserver" in window)) {
				els.forEach((el) => el.classList.add("nursery-visible"));
				return;
			}
			const obs = new IntersectionObserver(
				(entries) => {
					entries.forEach((e) => {
						if (e.isIntersecting) {
							e.target.classList.add("nursery-visible");
							obs.unobserve(e.target);
						}
					});
				},
				{ threshold: 0.12 }
			);
			els.forEach((el) => obs.observe(el));
		},

		renderChrome() {
			const cfg = this.config || this.defaultConfig();
			const name = cfg[this.nameField()] || "Nursery";
			const logo = cfg.logo
				? `<img src="${this.esc(cfg.logo)}" alt="" onerror="this.style.display='none'">`
				: "👶";
			const nav = [
				{ href: "/nursery", key: "home", page: "home" },
				{ href: "/nursery#nursery-programs-section", key: "programs", page: "home" },
				{ href: "/nursery#nursery-features-section", key: "features", page: "home" },
				{ href: "/nursery#nursery-stats", key: "stats", page: "home" },
			];

			const header = document.getElementById("nursery-header");
			if (header) {
				header.innerHTML = `
					<div class="nursery-topbar"><div class="nursery-wrap nursery-topbar-inner">
						<span>📞 +966 11 000 0000</span>
						<span>✉ admissions@omnexa.nursery</span>
						<span class="nursery-topbar-links">
							<a href="/app/nursery-workcenter">${this.lang === "ar" ? "مركز العمل" : "Workcenter"}</a>
							<a href="/app/nursery-parent-portal">${this.lang === "ar" ? "بوابة أولياء الأمور" : "Parent Portal"}</a>
						</span>
					</div></div>
					<div class="nursery-wrap nursery-header-inner">
						<a class="nursery-brand nursery-brand-stack" href="/nursery">
							<span class="nursery-brand-logo">${logo}</span>
							<span class="nursery-brand-name">${this.esc(name)}</span>
						</a>
						<button type="button" class="nursery-mobile-toggle" id="nursery-menu-toggle" aria-label="Menu">☰</button>
						<nav class="nursery-nav nursery-nav-single" id="nursery-nav">
							<div class="nursery-nav-links">
							${nav
								.map((n) => {
									const label = this.t(n.key);
									const active = n.page && this.page === n.page ? "active" : "";
									return `<a href="${n.href}" class="${active}">${label}</a>`;
								})
								.join("")}
							</div>
						</nav>
						<div class="nursery-actions">
							<button type="button" class="nursery-lang" id="nursery-lang-toggle">${this.lang === "ar" ? "EN" : "AR"}</button>
							<a class="nursery-btn nursery-btn-outline" href="/login">${this.t("login")}</a>
							<a class="nursery-btn nursery-btn-primary" href="/app/nursery-workcenter">${this.t("enroll")}</a>
						</div>
					</div>`;
				document.getElementById("nursery-lang-toggle")?.addEventListener("click", () => this.toggleLang());
				document.getElementById("nursery-menu-toggle")?.addEventListener("click", () => {
					document.getElementById("nursery-nav")?.classList.toggle("open");
				});
			}

			const footer = document.getElementById("nursery-footer");
			if (footer) {
				footer.innerHTML = `
					<div class="nursery-wrap nursery-footer-grid">
						<div>
							<h3>${this.esc(name)}</h3>
							<p>${this.esc(cfg[this.textField("hero_text")] || "")}</p>
							<p class="nursery-footer-contact">📞 +966 11 000 0000 · ✉ admissions@omnexa.nursery</p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "البرامج" : "Programs"}</h4>
							<p><a href="/nursery#nursery-programs-section">${this.lang === "ar" ? "حضانة الأطفال" : "Infant Care"}</a></p>
							<p><a href="/nursery#nursery-programs-section">${this.lang === "ar" ? "الروضة" : "Toddler"}</a></p>
							<p><a href="/nursery#nursery-programs-section">${this.lang === "ar" ? "ما قبل المدرسة" : "Preschool"}</a></p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "المميزات" : "Features"}</h4>
							<p><a href="/nursery#nursery-features-section">${this.lang === "ar" ? "معلمون مؤهلون" : "Qualified Teachers"}</a></p>
							<p><a href="/nursery#nursery-features-section">${this.lang === "ar" ? "أمان وحماية" : "Safe Environment"}</a></p>
							<p><a href="/nursery#nursery-features-section">${this.lang === "ar" ? "تطبيق أولياء الأمور" : "Parent App"}</a></p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "البوابات" : "Portals"}</h4>
							<p><a href="/app/nursery-workcenter">${this.lang === "ar" ? "مركز العمل" : "Workcenter"}</a></p>
							<p><a href="/app/nursery-parent-portal">${this.lang === "ar" ? "بوابة أولياء الأمور" : "Parent Portal"}</a></p>
						</div>
					</div>
					<div class="nursery-wrap nursery-footer-bottom">© ${new Date().getFullYear()} ${this.esc(name)} · Omnexa · ErpGenEx</div>`;
			}
		},

		init_home() {
			const cfg = this.config || {};
			const heroImg = cfg.hero_image || "";
			const hero = document.getElementById("nursery-hero");
			if (hero) {
				hero.innerHTML = `
					<div class="nursery-hero-bg" style="background-image:url('${this.esc(heroImg)}')"></div>
					<div class="nursery-hero-overlay"></div>
					<div class="nursery-wrap nursery-hero-premium-inner">
						<span class="nursery-eyebrow nursery-eyebrow-light">Omnexa Nursery · Premium Childcare</span>
						<h1>${this.esc(cfg[this.textField("tagline")] || "")}</h1>
						<p class="nursery-hero-lead">${this.esc(cfg[this.textField("hero_text")] || "")}</p>
						<div class="nursery-hero-cta">
							<a class="nursery-btn nursery-btn-accent" href="/app/nursery-workcenter">${this.lang === "ar" ? "سجل الآن" : "Enroll Now"}</a>
							<a class="nursery-btn nursery-btn-ghost-light" href="/nursery#nursery-programs-section">${this.lang === "ar" ? "استكشف البرامج" : "Explore Programs"}</a>
						</div>
					</div>`;
			}

			const trust = document.getElementById("nursery-trust-strip");
			if (trust) {
				const values = (cfg.features || DEFAULT_CATALOG.features).slice(0, 5);
				trust.innerHTML = `<div class="nursery-wrap nursery-value-inner">${values
					.map((v) => `<div class="nursery-value-item"><span>${v.icon}</span><strong>${this.lang === "ar" ? v.ar : v.en}</strong></div>`)
					.join("")}</div>`;
			}

			const programs = document.getElementById("nursery-programs-section");
			if (programs) {
				const progs = cfg.programs || DEFAULT_CATALOG.programs;
				programs.innerHTML = `
					<div class="nursery-wrap">
						<div class="nursery-section-title">
							<span class="nursery-eyebrow">Our Programs</span>
							<h2>${this.lang === "ar" ? "برامجنا التعليمية" : "Our Educational Programs"}</h2>
							<p>${this.lang === "ar" ? "برامج مصممة لكل مرحلة عمرية لضمان نمو طفلك بشكل صحي" : "Programs designed for every age group to ensure healthy child development"}</p>
						</div>
						<div class="nursery-grid-4">${progs
							.map((p) => `<div class="nursery-card">
								<div style="font-size:48px;margin-bottom:16px;">${p.icon}</div>
								<h3>${this.esc(this.lang === "ar" ? p.name_ar : p.name_en)}</h3>
								<p>${this.esc(p.age || "")}</p>
							</div>`
							)
							.join("")}</div>
					</div>`;
			}

			const features = document.getElementById("nursery-features-section");
			if (features) {
				const feats = cfg.features || DEFAULT_CATALOG.features;
				features.innerHTML = `
					<div class="nursery-wrap">
						<div class="nursery-section-title">
							<span class="nursery-eyebrow">Why Choose Us</span>
							<h2>${this.lang === "ar" ? "لماذا تختارنا؟" : "Why Choose Us?"}</h2>
							<p>${this.lang === "ar" ? "نقدم أفضل رعاية تعليمية لأطفالكم في بيئة آمنة ومحبة" : "We provide the best educational care for your children in a safe, loving environment"}</p>
						</div>
						<div class="nursery-grid-4">${feats
							.map((f) => `<div class="nursery-card">
								<div style="font-size:32px;margin-bottom:12px;">${f.icon}</div>
								<h3>${this.esc(this.lang === "ar" ? f.ar : f.en)}</h3>
							</div>`
							)
							.join("")}</div>
					</div>`;
			}

			const stats = document.getElementById("nursery-stats");
			if (stats && cfg.stats) {
				const s = cfg.stats;
				stats.innerHTML = `
					<div class="nursery-wrap nursery-stats-grid">
						<div><div class="nursery-stat-num">${s.children || 0}</div><div class="nursery-stat-label">${this.t("children")}</div></div>
						<div><div class="nursery-stat-num">${s.teachers || 0}</div><div class="nursery-stat-label">${this.t("teachers")}</div></div>
						<div><div class="nursery-stat-num">${s.families || 0}</div><div class="nursery-stat-label">${this.t("families")}</div></div>
						<div><div class="nursery-stat-num">${s.years || 0}</div><div class="nursery-stat-label">${this.t("years")}</div></div>
					</div>`;
			}

			const cta = document.getElementById("nursery-cta-band");
			if (cta) {
				cta.innerHTML = `
					<div class="nursery-wrap">
						<h2>${this.lang === "ar" ? "جاهز لتسجيل طفلك؟" : "Ready to enroll your child?"}</h2>
						<p>${this.lang === "ar" ? "انضم إلى مئات العائلات التي تثق في رعايتنا لأطفالها" : "Join hundreds of families who trust us with their children's care"}</p>
						<div class="nursery-hero-cta">
							<a class="nursery-btn nursery-btn-accent" href="/app/nursery-workcenter">${this.lang === "ar" ? "سجل الآن" : "Enroll Now"}</a>
							<a class="nursery-btn nursery-btn-ghost-light" href="/nursery#nursery-features-section">${this.t("learn_more")}</a>
						</div>
					</div>`;
			}
		},
	};
})();
