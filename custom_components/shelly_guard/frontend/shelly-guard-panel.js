class ShellyGuardPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._narrow = false;
    this._config = {};
    this._data = { devices: [], status: {}, updated_at: null };
    this._lastStateTs = null;
    this._loading = false;
    this._search = "";
    this._filter = "all";
    this._busy = {};
    this._toast = null;
    this._toastTimer = null;
    this._rendered = false;
  }

  setConfig(config) {
    this._config = config || {};
  }

  getCardSize() {
    return 12;
  }

  set narrow(val) {
    this._narrow = Boolean(val);
    const menuBtn = this.shadowRoot?.getElementById("sg-menu-btn");
    if (menuBtn) {
      menuBtn.narrow = this._narrow;
      menuBtn.style.display = this._narrow ? "inline-flex" : "none";
    }
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    const menuBtn = this.shadowRoot?.getElementById("sg-menu-btn");
    if (menuBtn) menuBtn.hass = hass;

    const sg = hass?.states?.["sensor.shelly_guard"];
    const ts = sg?.attributes?.state_ts || sg?.last_updated || null;
    if (first || (ts && ts !== this._lastStateTs)) {
      this._lastStateTs = ts;
      this._fetchState();
    } else if (this._rendered) {
      this._renderBody();
    }
  }

  async _fetchState() {
    if (!this._hass) return;
    this._loading = true;
    if (!this._rendered) this._renderShell();
    try {
      const data = await this._hass.callApi("GET", "shelly_guard/state");
      if (data && Array.isArray(data.devices)) {
        this._data = data;
      }
    } catch (e) {
      console.warn("shelly-guard-panel fetch failed:", e);
    } finally {
      this._loading = false;
      this._renderBody();
    }
  }

  _esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  _fmtShortDate(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return String(iso).slice(0, 16).replace("T", " ");
    const pad = (n) => String(n).padStart(2, "0");
    return `${pad(d.getDate())}/${pad(d.getMonth() + 1)} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  _showToast(msg, kind = "info") {
    this._toast = { msg, kind };
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => {
      this._toast = null;
      this._renderToast();
    }, 4500);
    this._renderToast();
  }

  _renderToast() {
    const el = this.shadowRoot?.getElementById("sg-toast");
    if (!el) return;
    if (!this._toast) {
      el.className = "toast hidden";
      el.textContent = "";
      return;
    }
    el.className = `toast ${this._toast.kind}`;
    el.textContent = this._toast.msg;
  }

  async _call(key, domain, service, data = {}, okMsg = "Ação executada") {
    if (!this._hass || this._busy[key]) return;
    this._busy[key] = true;
    this._renderBody();
    try {
      await this._hass.callService(domain, service, data);
      this._showToast(okMsg, "ok");
      setTimeout(() => this._fetchState(), 2500);
    } catch (e) {
      this._showToast(`Erro: ${e?.message || e}`, "err");
    } finally {
      setTimeout(() => {
        delete this._busy[key];
        this._renderBody();
      }, 1200);
    }
  }

  _getEnrichedDevices() {
    const states = this._hass?.states || {};
    const list = Array.isArray(this._data?.devices) ? this._data.devices : [];
    return list.map((d) => {
      const upd = d.update_entity ? states[d.update_entity] : null;
      const installed = upd?.attributes?.installed_version || d.fw || "—";
      const latest = upd?.attributes?.latest_version || "";
      const hasUpgrade = upd?.state === "on";
      const inProgress = Boolean(upd?.attributes?.in_progress);
      const progress = typeof upd?.attributes?.in_progress === "number" ? upd.attributes.in_progress : null;
      const isRE = Number(d.port || 80) !== 80;
      return {
        ...d,
        installed,
        latest,
        hasUpgrade,
        inProgress,
        progress,
        isRE,
      };
    });
  }

  _renderShell() {
    this._rendered = true;
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          min-height: 100%;
          background: var(--primary-background-color, #111);
          font-family: var(--paper-font-body1_-_font-family, Roboto, system-ui, -apple-system, sans-serif);
          color: var(--primary-text-color, #e1e1e1);
          box-sizing: border-box;
        }
        * { box-sizing: border-box; }
        .wrap {
          max-width: 1440px;
          margin: 0 auto;
          padding: 16px;
        }
        .header {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          background: var(--card-background-color, #1c1c1c);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.08));
          border-radius: 14px;
          padding: 16px 20px;
          margin-bottom: 14px;
        }
        .title-block {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .logo {
          width: 42px;
          height: 42px;
          border-radius: 12px;
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 18%, transparent);
          color: var(--primary-color, #03a9f4);
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .title {
          font-size: 1.25rem;
          font-weight: 600;
          margin: 0;
          line-height: 1.2;
        }
        .subtitle {
          font-size: 0.82rem;
          color: var(--secondary-text-color, #9e9e9e);
          margin-top: 3px;
        }
        .header-actions {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
        button.btn {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          border: 1px solid var(--divider-color, rgba(255,255,255,0.14));
          background: var(--secondary-background-color, rgba(255,255,255,0.06));
          color: var(--primary-text-color, #fff);
          border-radius: 10px;
          padding: 8px 13px;
          font-size: 0.85rem;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.15s, border-color 0.15s, opacity 0.15s;
        }
        button.btn:hover:not(:disabled) {
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 16%, var(--secondary-background-color, #2a2a2a));
          border-color: var(--primary-color, #03a9f4);
        }
        button.btn.primary {
          background: var(--primary-color, #03a9f4);
          border-color: var(--primary-color, #03a9f4);
          color: #fff;
        }
        button.btn.primary:hover:not(:disabled) { filter: brightness(1.08); }
        button.btn.upgrade-active {
          background: var(--warning-color, #ff9800);
          border-color: var(--warning-color, #ff9800);
          color: #111;
          font-weight: 600;
        }
        button.btn.upgrade-active:hover:not(:disabled) { filter: brightness(1.08); }
        button.btn.sm {
          padding: 5px 10px;
          font-size: 0.78rem;
          border-radius: 8px;
        }
        button.btn:disabled {
          opacity: 0.35;
          cursor: not-allowed;
        }
        .kpis {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
          gap: 10px;
          margin-bottom: 14px;
        }
        .kpi {
          background: var(--card-background-color, #1c1c1c);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.08));
          border-radius: 12px;
          padding: 12px 14px;
          cursor: pointer;
          transition: border-color 0.15s;
        }
        .kpi:hover { border-color: var(--primary-color, #03a9f4); }
        .kpi.active { border-color: var(--primary-color, #03a9f4); box-shadow: 0 0 0 1px var(--primary-color, #03a9f4); }
        .kpi-label {
          font-size: 0.75rem;
          color: var(--secondary-text-color, #9e9e9e);
          text-transform: uppercase;
          letter-spacing: 0.04em;
        }
        .kpi-val {
          font-size: 1.45rem;
          font-weight: 700;
          margin-top: 4px;
        }
        .kpi-val.ok { color: var(--success-color, #4caf50); }
        .kpi-val.err { color: var(--error-color, #f44336); }
        .kpi-val.warn { color: var(--warning-color, #ff9800); }
        .kpi-val.info { color: var(--primary-color, #03a9f4); }

        .toolbar {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          justify-content: space-between;
          gap: 10px;
          margin-bottom: 12px;
        }
        .search {
          flex: 1 1 240px;
          max-width: 380px;
          background: var(--card-background-color, #1c1c1c);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.14));
          color: var(--primary-text-color, #fff);
          border-radius: 10px;
          padding: 9px 12px;
          font-size: 0.88rem;
          outline: none;
        }
        .search:focus { border-color: var(--primary-color, #03a9f4); }
        .chips {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }
        .chip {
          border: 1px solid var(--divider-color, rgba(255,255,255,0.14));
          background: var(--card-background-color, #1c1c1c);
          color: var(--secondary-text-color, #aaa);
          border-radius: 999px;
          padding: 6px 12px;
          font-size: 0.8rem;
          cursor: pointer;
        }
        .chip.active {
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 20%, transparent);
          border-color: var(--primary-color, #03a9f4);
          color: var(--primary-text-color, #fff);
          font-weight: 600;
        }

        .table-card {
          background: var(--card-background-color, #1c1c1c);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.08));
          border-radius: 14px;
          overflow: hidden;
        }
        .table-scroll { overflow-x: auto; }
        table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.86rem;
        }
        th {
          text-align: left;
          font-size: 0.74rem;
          text-transform: uppercase;
          letter-spacing: 0.04em;
          color: var(--secondary-text-color, #9e9e9e);
          padding: 12px 14px;
          border-bottom: 1px solid var(--divider-color, rgba(255,255,255,0.1));
          white-space: nowrap;
        }
        td {
          padding: 11px 14px;
          border-bottom: 1px solid var(--divider-color, rgba(255,255,255,0.06));
          vertical-align: middle;
        }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: rgba(255,255,255,0.025); }
        tr.offline-row td { background: color-mix(in srgb, var(--error-color, #f44336) 7%, transparent); }

        .dev-name {
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .dot {
          width: 9px;
          height: 9px;
          border-radius: 50%;
          flex-shrink: 0;
        }
        .dot.on { background: var(--success-color, #4caf50); }
        .dot.off { background: var(--error-color, #f44336); }
        .dot.rst { background: var(--warning-color, #ff9800); }
        .dev-meta {
          font-size: 0.76rem;
          color: var(--secondary-text-color, #9e9e9e);
          margin-top: 2px;
        }
        .dev-meta a {
          color: var(--primary-color, #03a9f4);
          text-decoration: none;
        }
        .dev-meta a:hover { text-decoration: underline; }
        .badge {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 3px 8px;
          border-radius: 999px;
          font-size: 0.75rem;
          font-weight: 500;
          white-space: nowrap;
        }
        .badge.ok {
          background: color-mix(in srgb, var(--success-color, #4caf50) 16%, transparent);
          color: var(--success-color, #4caf50);
        }
        .badge.miss {
          background: color-mix(in srgb, var(--error-color, #f44336) 16%, transparent);
          color: var(--error-color, #f44336);
        }
        .badge.cfg {
          background: var(--secondary-background-color, rgba(255,255,255,0.07));
          color: var(--primary-text-color, #ddd);
        }
        .badge.re {
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 18%, transparent);
          color: var(--primary-color, #03a9f4);
        }
        .fw-cell {
          font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          font-size: 0.8rem;
          white-space: nowrap;
        }
        .fw-new {
          color: var(--warning-color, #ff9800);
          font-weight: 600;
          margin-left: 4px;
        }
        .actions-cell {
          display: flex;
          gap: 6px;
          justify-content: flex-end;
          white-space: nowrap;
        }
        .empty {
          padding: 32px;
          text-align: center;
          color: var(--secondary-text-color, #9e9e9e);
        }
        .toast {
          position: fixed;
          bottom: 20px;
          right: 20px;
          z-index: 999;
          padding: 10px 16px;
          border-radius: 10px;
          font-size: 0.86rem;
          font-weight: 500;
          box-shadow: 0 6px 20px rgba(0,0,0,0.35);
          background: var(--card-background-color, #222);
          border: 1px solid var(--primary-color, #03a9f4);
          color: var(--primary-text-color, #fff);
        }
        .toast.ok { border-color: var(--success-color, #4caf50); }
        .toast.err { border-color: var(--error-color, #f44336); }
        .toast.hidden { display: none; }
        .spin {
          display: inline-block;
          animation: sg-spin 1s linear infinite;
        }
        @keyframes sg-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      </style>
      <div class="wrap">
        <div class="header">
          <div class="title-block">
            <ha-menu-button id="sg-menu-btn" style="display:${this._narrow ? "inline-flex" : "none"}"></ha-menu-button>
            <div class="logo"><ha-icon icon="mdi:shield-sync"></ha-icon></div>
            <div>
              <h1 class="title">Shelly Guard</h1>
              <div class="subtitle" id="sg-sub">A carregar estado...</div>
            </div>
          </div>
          <div class="header-actions">
            <button class="btn" id="btn-reload" title="Recarregar integração Shelly Guard">
              <ha-icon icon="mdi:reload"></ha-icon> Reload
            </button>
            <button class="btn" id="btn-backup" title="Backup de todos os Shellys">
              <ha-icon icon="mdi:content-save-all"></ha-icon> Backup All
            </button>
            <button class="btn primary" id="btn-check" title="Executar verificação completa">
              <ha-icon icon="mdi:shield-refresh"></ha-icon> Check Completo
            </button>
          </div>
        </div>

        <div class="kpis" id="sg-kpis"></div>

        <div class="toolbar">
          <input class="search" id="sg-search" type="search" placeholder="Filtrar por nome, área, IP, MAC, modelo ou firmware..." />
          <div class="chips" id="sg-chips"></div>
        </div>

        <div class="table-card">
          <div class="table-scroll" id="sg-table"></div>
        </div>
      </div>
      <div class="toast hidden" id="sg-toast"></div>
    `;

    const menuBtn = this.shadowRoot.getElementById("sg-menu-btn");
    if (menuBtn) {
      menuBtn.hass = this._hass;
      menuBtn.narrow = this._narrow;
    }

    this.shadowRoot.getElementById("btn-reload").addEventListener("click", () =>
      this._call("reload", "shelly_guard", "reload", {}, "Shelly Guard recarregado")
    );
    this.shadowRoot.getElementById("btn-backup").addEventListener("click", () =>
      this._call("backup", "shelly_guard", "backup_all", {}, "Backup completo iniciado")
    );
    this.shadowRoot.getElementById("btn-check").addEventListener("click", () =>
      this._call("check", "shelly_guard", "check", {}, "Check completo iniciado")
    );
    this.shadowRoot.getElementById("sg-search").addEventListener("input", (e) => {
      this._search = (e.target.value || "").trim().toLowerCase();
      this._renderBody();
    });
  }

  _renderBody() {
    if (!this._rendered) this._renderShell();
    const devs = this._getEnrichedDevices();
    const sg = this._hass?.states?.["sensor.shelly_guard"];
    const lastCheck = sg?.attributes?.last_check || this._data?.status?.last_check || this._data?.updated_at;
    const lastDev = sg?.attributes?.last_device_check || this._data?.status?.last_device_check;

    const sub = this.shadowRoot.getElementById("sg-sub");
    if (sub) {
      const parts = [];
      if (lastCheck) parts.push(`Último check: ${this._fmtShortDate(lastCheck)}`);
      if (lastDev) parts.push(`Último dispositivo: ${lastDev}`);
      sub.textContent = parts.length ? parts.join(" · ") : "Sem verificação registada ainda";
    }

    const btnReload = this.shadowRoot.getElementById("btn-reload");
    const btnBackup = this.shadowRoot.getElementById("btn-backup");
    const btnCheck = this.shadowRoot.getElementById("btn-check");
    if (btnReload) btnReload.disabled = Boolean(this._busy.reload);
    if (btnBackup) btnBackup.disabled = Boolean(this._busy.backup);
    if (btnCheck) btnCheck.disabled = Boolean(this._busy.check);

    const total = devs.length;
    const online = devs.filter((d) => d.online).length;
    const offline = total - online;
    const withBk = devs.filter((d) => d.has_backup).length;
    const noBk = total - withBk;
    const upgrades = devs.filter((d) => d.hasUpgrade).length;
    const reCount = devs.filter((d) => d.isRE).length;

    const kpisEl = this.shadowRoot.getElementById("sg-kpis");
    if (kpisEl) {
      const cards = [
        { id: "all", label: "Dispositivos", val: total, cls: "info" },
        { id: "online", label: "Online", val: online, cls: "ok" },
        { id: "offline", label: "Offline", val: offline, cls: offline ? "err" : "ok" },
        { id: "nobackup", label: "Backups", val: `${withBk}/${total}`, cls: noBk ? "warn" : "ok" },
        { id: "upgrade", label: "Upgrades", val: upgrades, cls: upgrades ? "warn" : "ok" },
        { id: "re", label: "Range Extender", val: reCount, cls: "info" },
      ];
      kpisEl.innerHTML = cards
        .map(
          (c) => `
          <div class="kpi ${this._filter === c.id ? "active" : ""}" data-filter="${c.id}">
            <div class="kpi-label">${c.label}</div>
            <div class="kpi-val ${c.cls}">${c.val}</div>
          </div>`
        )
        .join("");
      kpisEl.querySelectorAll(".kpi").forEach((el) => {
        el.addEventListener("click", () => {
          this._filter = el.dataset.filter;
          this._renderBody();
        });
      });
    }

    const chipsEl = this.shadowRoot.getElementById("sg-chips");
    if (chipsEl) {
      const filters = [
        ["all", `Todos (${total})`],
        ["offline", `Offline (${offline})`],
        ["upgrade", `Com Upgrade (${upgrades})`],
        ["re", `Range Extender (${reCount})`],
        ["nobackup", `Sem Backup (${noBk})`],
      ];
      chipsEl.innerHTML = filters
        .map(
          ([id, lbl]) =>
            `<button class="chip ${this._filter === id ? "active" : ""}" data-filter="${id}">${lbl}</button>`
        )
        .join("");
      chipsEl.querySelectorAll(".chip").forEach((el) => {
        el.addEventListener("click", () => {
          this._filter = el.dataset.filter;
          this._renderBody();
        });
      });
    }

    const filtered = devs.filter((d) => {
      if (this._filter === "online" && !d.online) return false;
      if (this._filter === "offline" && d.online) return false;
      if (this._filter === "upgrade" && !d.hasUpgrade) return false;
      if (this._filter === "re" && !d.isRE) return false;
      if (this._filter === "nobackup" && d.has_backup) return false;
      if (this._search) {
        const hay = `${d.name} ${d.area} ${d.host} ${d.port} ${d.mac} ${d.model} ${d.config_type} ${d.installed}`.toLowerCase();
        if (!hay.includes(this._search)) return false;
      }
      return true;
    });

    const tableEl = this.shadowRoot.getElementById("sg-table");
    if (!tableEl) return;

    if (!filtered.length) {
      tableEl.innerHTML = `<div class="empty">${
        this._loading
          ? "A carregar dispositivos..."
          : "Nenhum dispositivo corresponde ao filtro atual."
      }</div>`;
      return;
    }

    const rowsHtml = filtered
      .map((d) => {
        const addr = Number(d.port || 80) !== 80 ? `${d.host}:${d.port}` : d.host;
        const dotCls = d.reset ? "rst" : d.online ? "on" : "off";
        const bkHtml = d.has_backup
          ? `<span class="badge ok" title="${this._esc(d.backup_at)}">Sim · ${this._esc(this._fmtShortDate(d.backup_at))}</span>`
          : `<span class="badge miss">Sem backup</span>`;
        const cfgCls = d.isRE ? "re" : "cfg";
        const hardTitle =
          d.hardened === true
            ? "Reset por interruptor desativado"
            : d.hardened === false
            ? "Atenção: reset por interruptor ainda ativo"
            : "";
        const hardIcon =
          d.hardened === true
            ? ` <ha-icon icon="mdi:shield-check" style="--mdc-icon-size:15px;color:var(--success-color,#4caf50)" title="${hardTitle}"></ha-icon>`
            : d.hardened === false
            ? ` <ha-icon icon="mdi:shield-alert" style="--mdc-icon-size:15px;color:var(--warning-color,#ff9800)" title="${hardTitle}"></ha-icon>`
            : "";

        let fwHtml = `<span>${this._esc(d.installed)}</span>`;
        if (d.inProgress) {
          fwHtml += `<span class="fw-new">A atualizar${d.progress != null ? ` (${d.progress}%)` : "..."}</span>`;
        } else if (d.hasUpgrade && d.latest) {
          fwHtml += `<span class="fw-new">→ ${this._esc(d.latest)}</span>`;
        }

        const upgKey = `upg_${d.mac}`;
        const chkKey = `chk_${d.mac}`;
        const upgDisabled = !d.hasUpgrade || d.inProgress || Boolean(this._busy[upgKey]);
        const upgCls = d.hasUpgrade && !d.inProgress ? "btn sm upgrade-active" : "btn sm";
        const upgLabel = d.inProgress ? "A instalar..." : d.hasUpgrade ? "Upgrade" : "Atualizado";
        const chkBusy = Boolean(this._busy[chkKey]);

        return `
          <tr class="${d.online ? "" : "offline-row"}">
            <td>
              <div class="dev-name">
                <span class="dot ${dotCls}" title="${d.online ? "Online" : "Offline"}"></span>
                <span>${this._esc(d.name)}</span>
              </div>
              <div class="dev-meta">
                ${d.area ? `${this._esc(d.area)} · ` : ""}
                <a href="http://${this._esc(addr)}" target="_blank" rel="noopener">${this._esc(addr)}</a>
                ${d.model ? ` · ${this._esc(d.model)}` : ""}
                ${d.error ? `<div style="color:var(--error-color,#f44336)">${this._esc(d.error)}</div>` : ""}
              </div>
            </td>
            <td>${bkHtml}</td>
            <td>
              <span class="badge ${cfgCls}">${this._esc(d.config_type || `Gen${d.gen}`)}</span>${hardIcon}
            </td>
            <td class="fw-cell">${fwHtml}</td>
            <td>
              <div class="actions-cell">
                <button class="${upgCls}" data-act="upgrade" data-mac="${this._esc(d.mac)}" data-entity="${this._esc(d.update_entity)}" data-name="${this._esc(d.name)}" ${upgDisabled ? "disabled" : ""}>
                  <ha-icon icon="mdi:package-up" style="--mdc-icon-size:15px"></ha-icon> ${upgLabel}
                </button>
                <button class="btn sm" data-act="check" data-mac="${this._esc(d.mac)}" data-name="${this._esc(d.name)}" ${chkBusy ? "disabled" : ""} title="Reexecutar check deste dispositivo">
                  <ha-icon icon="mdi:refresh" class="${chkBusy ? "spin" : ""}" style="--mdc-icon-size:15px"></ha-icon> Check
                </button>
              </div>
            </td>
          </tr>
        `;
      })
      .join("");

    tableEl.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Dispositivo</th>
            <th>Backup</th>
            <th>Configuração</th>
            <th>Firmware</th>
            <th style="text-align:right">Ações</th>
          </tr>
        </thead>
        <tbody>${rowsHtml}</tbody>
      </table>
    `;

    tableEl.querySelectorAll("button[data-act='upgrade']").forEach((btn) => {
      btn.addEventListener("click", () => {
        const entity = btn.dataset.entity;
        const name = btn.dataset.name;
        const mac = btn.dataset.mac;
        if (!entity) return;
        if (!confirm(`Instalar atualização de firmware em ${name}?`)) return;
        this._call(`upg_${mac}`, "update", "install", { entity_id: entity }, `Upgrade iniciado em ${name}`);
      });
    });

    tableEl.querySelectorAll("button[data-act='check']").forEach((btn) => {
      btn.addEventListener("click", () => {
        const mac = btn.dataset.mac;
        const name = btn.dataset.name;
        this._call(`chk_${mac}`, "shelly_guard", "check_device", { mac }, `Check executado em ${name}`);
      });
    });
  }
}

class ShellyGuardCard extends ShellyGuardPanel {}

if (!customElements.get("shelly-guard-panel")) {
  customElements.define("shelly-guard-panel", ShellyGuardPanel);
}
if (!customElements.get("shelly-guard-card")) {
  customElements.define("shelly-guard-card", ShellyGuardCard);
}
