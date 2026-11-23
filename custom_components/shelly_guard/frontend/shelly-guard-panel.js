class ShellyGuardPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._narrow = false;
    this._config = {};
    this._data = { devices: [], status: {}, updated_at: null, pending_new_devices: [] };
    this._lastStateTs = null;
    this._loading = false;
    this._search = "";
    this._filter = "all";
    this._busy = {};
    this._toast = null;
    this._toastTimer = null;
    this._rendered = false;
    this._modal = null; // { type: 'meta', mac } | { type: 'replace', newDev }
    this._seenPending = new Set();
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
        const pending = data.pending_new_devices || [];
        if (pending.length && !this._modal) {
          const unseen = pending.find((p) => !this._seenPending.has(p.mac));
          if (unseen) {
            this._seenPending.add(unseen.mac);
            this._modal = { type: "replace", newDev: unseen };
          }
        }
      }
    } catch (e) {
      console.warn("shelly-guard-panel fetch failed:", e);
    } finally {
      this._loading = false;
      this._renderBody();
      this._renderModal();
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

  _fmtMonthYear(isoDate) {
    if (!isoDate || isoDate.length < 7) return "";
    const [y, m] = isoDate.split("-");
    return `${m}/${y}`;
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

  async _call(key, domain, service, data = {}, okMsg = "Ação executada", refreshMs = 1500) {
    if (!this._hass || this._busy[key]) return false;
    this._busy[key] = true;
    this._renderBody();
    try {
      await this._hass.callService(domain, service, data);
      this._showToast(okMsg, "ok");
      setTimeout(() => this._fetchState(), refreshMs);
      return true;
    } catch (e) {
      this._showToast(`Erro: ${e?.message || e}`, "err");
      return false;
    } finally {
      setTimeout(() => {
        delete this._busy[key];
        this._renderBody();
      }, 900);
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
        lifecycle: d.lifecycle || "active",
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
          max-width: 1500px;
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
        .title { font-size: 1.25rem; font-weight: 600; margin: 0; line-height: 1.2; }
        .subtitle { font-size: 0.82rem; color: var(--secondary-text-color, #9e9e9e); margin-top: 3px; }
        .header-actions { display: flex; flex-wrap: wrap; gap: 8px; }
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
        button.btn.primary { background: var(--primary-color, #03a9f4); border-color: var(--primary-color, #03a9f4); color: #fff; }
        button.btn.primary:hover:not(:disabled) { filter: brightness(1.08); }
        button.btn.danger { background: color-mix(in srgb, var(--error-color, #f44336) 20%, transparent); border-color: var(--error-color, #f44336); color: var(--error-color, #f44336); }
        button.btn.danger:hover:not(:disabled) { background: var(--error-color, #f44336); color: #fff; }
        button.btn.upgrade-active { background: var(--warning-color, #ff9800); border-color: var(--warning-color, #ff9800); color: #111; font-weight: 600; }
        button.btn.upgrade-active:hover:not(:disabled) { filter: brightness(1.08); }
        button.btn.sm { padding: 5px 9px; font-size: 0.78rem; border-radius: 8px; }
        button.btn:disabled { opacity: 0.35; cursor: not-allowed; }

        .pending-banner {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          background: color-mix(in srgb, var(--warning-color, #ff9800) 14%, var(--card-background-color, #1c1c1c));
          border: 1px solid var(--warning-color, #ff9800);
          border-radius: 12px;
          padding: 12px 16px;
          margin-bottom: 14px;
        }
        .pending-banner.hidden { display: none; }

        .kpis {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
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
        .kpi-label { font-size: 0.74rem; color: var(--secondary-text-color, #9e9e9e); text-transform: uppercase; letter-spacing: 0.04em; }
        .kpi-val { font-size: 1.4rem; font-weight: 700; margin-top: 4px; }
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
        .chips { display: flex; flex-wrap: wrap; gap: 6px; }
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
        table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
        th {
          text-align: left;
          font-size: 0.73rem;
          text-transform: uppercase;
          letter-spacing: 0.04em;
          color: var(--secondary-text-color, #9e9e9e);
          padding: 12px 13px;
          border-bottom: 1px solid var(--divider-color, rgba(255,255,255,0.1));
          white-space: nowrap;
        }
        td {
          padding: 10px 13px;
          border-bottom: 1px solid var(--divider-color, rgba(255,255,255,0.06));
          vertical-align: middle;
        }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: rgba(255,255,255,0.025); }
        tr.offline-row td { background: color-mix(in srgb, var(--error-color, #f44336) 7%, transparent); }
        tr.faulty-row td { background: color-mix(in srgb, var(--warning-color, #ff9800) 9%, transparent); }

        .dev-name { font-weight: 600; display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }
        .dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
        .dot.on { background: var(--success-color, #4caf50); }
        .dot.off { background: var(--error-color, #f44336); }
        .dot.rst { background: var(--warning-color, #ff9800); }
        .dev-meta { font-size: 0.75rem; color: var(--secondary-text-color, #9e9e9e); margin-top: 2px; }
        .dev-meta a { color: var(--primary-color, #03a9f4); text-decoration: none; }
        .dev-meta a:hover { text-decoration: underline; }
        .rma-line { font-size: 0.75rem; color: var(--warning-color, #ff9800); margin-top: 3px; font-weight: 500; }

        .badge {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 3px 8px;
          border-radius: 999px;
          font-size: 0.74rem;
          font-weight: 500;
          white-space: nowrap;
        }
        .badge.ok { background: color-mix(in srgb, var(--success-color, #4caf50) 16%, transparent); color: var(--success-color, #4caf50); }
        .badge.miss { background: color-mix(in srgb, var(--error-color, #f44336) 16%, transparent); color: var(--error-color, #f44336); }
        .badge.warn { background: color-mix(in srgb, var(--warning-color, #ff9800) 18%, transparent); color: var(--warning-color, #ff9800); }
        .badge.muted { background: var(--secondary-background-color, rgba(255,255,255,0.06)); color: var(--secondary-text-color, #9e9e9e); }
        .badge.cfg { background: var(--secondary-background-color, rgba(255,255,255,0.07)); color: var(--primary-text-color, #ddd); }
        .badge.re { background: color-mix(in srgb, var(--primary-color, #03a9f4) 18%, transparent); color: var(--primary-color, #03a9f4); }
        .badge.clickable { cursor: pointer; }
        .badge.clickable:hover { filter: brightness(1.15); }

        .fw-cell { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.79rem; white-space: nowrap; }
        .fw-new { color: var(--warning-color, #ff9800); font-weight: 600; margin-left: 4px; }
        .actions-cell { display: flex; gap: 6px; justify-content: flex-end; white-space: nowrap; }
        .empty { padding: 32px; text-align: center; color: var(--secondary-text-color, #9e9e9e); }

        .modal-backdrop {
          position: fixed;
          inset: 0;
          background: rgba(0, 0, 0, 0.65);
          z-index: 1000;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 16px;
        }
        .modal-backdrop.hidden { display: none; }
        .modal {
          width: 100%;
          max-width: 520px;
          background: var(--card-background-color, #1e1e1e);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.14));
          border-radius: 16px;
          padding: 20px;
          box-shadow: 0 18px 48px rgba(0,0,0,0.5);
          max-height: 90vh;
          overflow-y: auto;
        }
        .modal h2 { margin: 0 0 6px; font-size: 1.12rem; }
        .modal-sub { font-size: 0.82rem; color: var(--secondary-text-color, #9e9e9e); margin-bottom: 16px; }
        .field { margin-bottom: 12px; }
        .field label { display: block; font-size: 0.78rem; color: var(--secondary-text-color, #aaa); margin-bottom: 4px; }
        .field input, .field select, .field textarea {
          width: 100%;
          background: var(--primary-background-color, #121212);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.16));
          color: var(--primary-text-color, #fff);
          border-radius: 8px;
          padding: 8px 10px;
          font-size: 0.88rem;
          font-family: inherit;
        }
        .field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .modal-section {
          border-top: 1px solid var(--divider-color, rgba(255,255,255,0.1));
          margin-top: 16px;
          padding-top: 14px;
        }
        .modal-actions {
          display: flex;
          justify-content: flex-end;
          gap: 8px;
          margin-top: 16px;
          flex-wrap: wrap;
        }

        .toast {
          position: fixed;
          bottom: 20px;
          right: 20px;
          z-index: 1100;
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
        .spin { display: inline-block; animation: sg-spin 1s linear infinite; }
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

        <div class="pending-banner hidden" id="sg-pending"></div>
        <div class="kpis" id="sg-kpis"></div>

        <div class="toolbar">
          <input class="search" id="sg-search" type="search" placeholder="Filtrar por nome, área, IP, MAC, vendedor, fatura ou firmware..." />
          <div class="chips" id="sg-chips"></div>
        </div>

        <div class="table-card">
          <div class="table-scroll" id="sg-table"></div>
        </div>
      </div>
      <div class="modal-backdrop hidden" id="sg-modal-bg"></div>
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
    this.shadowRoot.getElementById("sg-modal-bg").addEventListener("click", (e) => {
      if (e.target.id === "sg-modal-bg") {
        this._modal = null;
        this._renderModal();
      }
    });
  }

  _warrantyBadgeHtml(d) {
    const st = d.warranty_status || "unknown";
    if (st === "valid") {
      return `<span class="badge ok clickable" data-act="meta" data-mac="${this._esc(d.mac)}" title="${this._esc(d.vendor || "Garantia")} · até ${this._esc(d.warranty_until)}">Até ${this._esc(this._fmtMonthYear(d.warranty_until))}</span>`;
    }
    if (st === "expiring") {
      return `<span class="badge warn clickable" data-act="meta" data-mac="${this._esc(d.mac)}" title="Expira em ${d.warranty_days_left} dias (${this._esc(d.warranty_until)})">Expira ${d.warranty_days_left}d</span>`;
    }
    if (st === "expired") {
      return `<span class="badge muted clickable" data-act="meta" data-mac="${this._esc(d.mac)}" title="Expirou em ${this._esc(d.warranty_until)}">Expirada</span>`;
    }
    return `<span class="badge muted clickable" data-act="meta" data-mac="${this._esc(d.mac)}" title="Adicionar data de compra, vendedor e fatura">+ Registar</span>`;
  }

  _renderBody() {
    if (!this._rendered) this._renderShell();
    const devs = this._getEnrichedDevices();
    const pending = this._data?.pending_new_devices || [];
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

    const pendingEl = this.shadowRoot.getElementById("sg-pending");
    if (pendingEl) {
      if (pending.length) {
        const first = pending[0];
        pendingEl.className = "pending-banner";
        pendingEl.innerHTML = `
          <div>
            <strong>Novo Shelly detetado:</strong> ${this._esc(first.name)}
            ${first.model ? `(${this._esc(first.model)})` : ""} · <code>${this._esc(first.mac)}</code>
            ${pending.length > 1 ? ` (+${pending.length - 1} outro)` : ""}
            <div style="font-size:0.8rem;color:var(--secondary-text-color,#ccc);margin-top:2px">
              Escolhe se é um dispositivo novo ou se vem substituir um dos dispositivos avariados/offline.
            </div>
          </div>
          <button class="btn primary sm" id="btn-open-replace">
            <ha-icon icon="mdi:swap-horizontal" style="--mdc-icon-size:16px"></ha-icon> Configurar / Substituir
          </button>
        `;
        pendingEl.querySelector("#btn-open-replace").addEventListener("click", () => {
          this._modal = { type: "replace", newDev: first };
          this._renderModal();
        });
      } else {
        pendingEl.className = "pending-banner hidden";
        pendingEl.innerHTML = "";
      }
    }

    const btnReload = this.shadowRoot.getElementById("btn-reload");
    const btnBackup = this.shadowRoot.getElementById("btn-backup");
    const btnCheck = this.shadowRoot.getElementById("btn-check");
    if (btnReload) btnReload.disabled = Boolean(this._busy.reload);
    if (btnBackup) btnBackup.disabled = Boolean(this._busy.backup);
    if (btnCheck) btnCheck.disabled = Boolean(this._busy.check);

    const activeDevs = devs.filter((d) => d.lifecycle !== "replaced");
    const total = activeDevs.length;
    const online = activeDevs.filter((d) => d.online && d.lifecycle === "active").length;
    const offline = activeDevs.filter((d) => !d.online && d.lifecycle === "active").length;
    const faulty = devs.filter((d) => d.lifecycle === "faulty").length;
    const replaced = devs.filter((d) => d.lifecycle === "replaced").length;
    const withBk = activeDevs.filter((d) => d.has_backup).length;
    const noBk = total - withBk;
    const upgrades = activeDevs.filter((d) => d.hasUpgrade).length;
    const reCount = activeDevs.filter((d) => d.isRE).length;

    const kpisEl = this.shadowRoot.getElementById("sg-kpis");
    if (kpisEl) {
      const cards = [
        { id: "all", label: "Dispositivos", val: total, cls: "info" },
        { id: "online", label: "Online", val: online, cls: "ok" },
        { id: "offline", label: "Offline", val: offline, cls: offline ? "err" : "ok" },
        { id: "faulty", label: "Avariados", val: faulty, cls: faulty ? "warn" : "ok" },
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
        ["faulty", `Avariados (${faulty})`],
        ["upgrade", `Com Upgrade (${upgrades})`],
        ["re", `Range Extender (${reCount})`],
        ["nobackup", `Sem Backup (${noBk})`],
      ];
      if (replaced > 0) filters.push(["replaced", `Substituídos (${replaced})`]);
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
      if (this._filter === "replaced") {
        if (d.lifecycle !== "replaced") return false;
      } else {
        if (d.lifecycle === "replaced") return false;
        if (this._filter === "online" && !(d.online && d.lifecycle === "active")) return false;
        if (this._filter === "offline" && !(!d.online && d.lifecycle === "active")) return false;
        if (this._filter === "faulty" && d.lifecycle !== "faulty") return false;
        if (this._filter === "upgrade" && !d.hasUpgrade) return false;
        if (this._filter === "re" && !d.isRE) return false;
        if (this._filter === "nobackup" && d.has_backup) return false;
      }
      if (this._search) {
        const hay = `${d.name} ${d.area} ${d.host} ${d.port} ${d.mac} ${d.model} ${d.config_type} ${d.installed} ${d.vendor} ${d.invoice_number} ${d.faulty_reason}`.toLowerCase();
        if (!hay.includes(this._search)) return false;
      }
      return true;
    });

    const tableEl = this.shadowRoot.getElementById("sg-table");
    if (!tableEl) return;

    if (!filtered.length) {
      tableEl.innerHTML = `<div class="empty">${
        this._loading ? "A carregar dispositivos..." : "Nenhum dispositivo corresponde ao filtro atual."
      }</div>`;
      return;
    }

    const rowsHtml = filtered
      .map((d) => {
        const addr = Number(d.port || 80) !== 80 ? `${d.host}:${d.port}` : d.host;
        const dotCls = d.lifecycle === "faulty" || d.reset ? "rst" : d.online ? "on" : "off";
        const rowCls = d.lifecycle === "faulty" ? "faulty-row" : d.online ? "" : "offline-row";
        const lcBadge =
          d.lifecycle === "faulty"
            ? `<span class="badge warn">Avariado</span>`
            : d.lifecycle === "replaced"
            ? `<span class="badge muted">Substituído</span>`
            : "";

        const bkHtml = d.has_backup
          ? `<span class="badge ok" title="${this._esc(d.backup_at)}">Sim · ${this._esc(this._fmtShortDate(d.backup_at))}</span>`
          : `<span class="badge miss">Sem backup</span>`;
        const cfgCls = d.isRE ? "re" : "cfg";
        const hardIcon =
          d.hardened === true
            ? ` <ha-icon icon="mdi:shield-check" style="--mdc-icon-size:15px;color:var(--success-color,#4caf50)" title="Reset por interruptor desativado"></ha-icon>`
            : d.hardened === false
            ? ` <ha-icon icon="mdi:shield-alert" style="--mdc-icon-size:15px;color:var(--warning-color,#ff9800)" title="Reset por interruptor ainda ativo"></ha-icon>`
            : "";

        let fwHtml = `<span>${this._esc(d.installed)}</span>`;
        if (d.inProgress) {
          fwHtml += `<span class="fw-new">A atualizar${d.progress != null ? ` (${d.progress}%)` : "..."}</span>`;
        } else if (d.hasUpgrade && d.latest) {
          fwHtml += `<span class="fw-new">→ ${this._esc(d.latest)}</span>`;
        }

        const rmaInfo =
          (d.lifecycle === "faulty" || d.lifecycle === "replaced") && (d.vendor || d.invoice_number || d.faulty_reason)
            ? `<div class="rma-line">
                ${d.vendor ? `Loja: ${this._esc(d.vendor)}` : ""}
                ${d.invoice_number ? ` · Fatura: ${this._esc(d.invoice_number)}` : ""}
                ${d.faulty_reason ? ` · ${this._esc(d.faulty_reason)}` : ""}
                ${d.replaced_by ? ` · Substituído por ${this._esc(d.replaced_by)}` : ""}
              </div>`
            : "";

        const upgKey = `upg_${d.mac}`;
        const chkKey = `chk_${d.mac}`;
        const upgDisabled = !d.hasUpgrade || d.inProgress || Boolean(this._busy[upgKey]);
        const upgCls = d.hasUpgrade && !d.inProgress ? "btn sm upgrade-active" : "btn sm";
        const upgLabel = d.inProgress ? "A instalar..." : d.hasUpgrade ? "Upgrade" : "Atualizado";
        const chkBusy = Boolean(this._busy[chkKey]);

        return `
          <tr class="${rowCls}">
            <td>
              <div class="dev-name">
                <span class="dot ${dotCls}"></span>
                <span>${this._esc(d.name)}</span>
                ${lcBadge}
              </div>
              <div class="dev-meta">
                ${d.area ? `${this._esc(d.area)} · ` : ""}
                ${addr ? `<a href="http://${this._esc(addr)}" target="_blank" rel="noopener">${this._esc(addr)}</a>` : ""}
                ${d.model ? ` · ${this._esc(d.model)}` : ""}
                ${d.error && d.lifecycle === "active" ? `<div style="color:var(--error-color,#f44336)">${this._esc(d.error)}</div>` : ""}
              </div>
              ${rmaInfo}
            </td>
            <td>${bkHtml}</td>
            <td><span class="badge ${cfgCls}">${this._esc(d.config_type || `Gen${d.gen}`)}</span>${hardIcon}</td>
            <td>
              ${this._warrantyBadgeHtml(d)}
              ${d.vendor ? `<div class="dev-meta">${this._esc(d.vendor)}</div>` : ""}
            </td>
            <td class="fw-cell">${fwHtml}</td>
            <td>
              <div class="actions-cell">
                <button class="btn sm" data-act="meta" data-mac="${this._esc(d.mac)}" title="Garantia, fatura e estado (avariado)">
                  <ha-icon icon="mdi:receipt-text-outline" style="--mdc-icon-size:15px"></ha-icon>
                </button>
                <button class="${upgCls}" data-act="upgrade" data-mac="${this._esc(d.mac)}" data-entity="${this._esc(d.update_entity)}" data-name="${this._esc(d.name)}" ${upgDisabled ? "disabled" : ""}>
                  <ha-icon icon="mdi:package-up" style="--mdc-icon-size:15px"></ha-icon> ${upgLabel}
                </button>
                <button class="btn sm" data-act="check" data-mac="${this._esc(d.mac)}" data-name="${this._esc(d.name)}" ${chkBusy || d.lifecycle === "replaced" ? "disabled" : ""} title="Reexecutar check deste dispositivo">
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
            <th>Garantia</th>
            <th>Firmware</th>
            <th style="text-align:right">Ações</th>
          </tr>
        </thead>
        <tbody>${rowsHtml}</tbody>
      </table>
    `;

    tableEl.querySelectorAll("[data-act='meta']").forEach((el) => {
      el.addEventListener("click", () => {
        this._modal = { type: "meta", mac: el.dataset.mac };
        this._renderModal();
      });
    });

    tableEl.querySelectorAll("button[data-act='upgrade']").forEach((btn) => {
      btn.addEventListener("click", () => {
        const entity = btn.dataset.entity;
        const name = btn.dataset.name;
        const mac = btn.dataset.mac;
        if (!entity) return;
        if (!confirm(`Instalar atualização de firmware em ${name}?`)) return;
        this._call(`upg_${mac}`, "update", "install", { entity_id: entity }, `Upgrade iniciado em ${name}`, 3000);
      });
    });

    tableEl.querySelectorAll("button[data-act='check']").forEach((btn) => {
      btn.addEventListener("click", () => {
        const mac = btn.dataset.mac;
        const name = btn.dataset.name;
        this._call(`chk_${mac}`, "shelly_guard", "check_device", { mac }, `Check executado em ${name}`, 2500);
      });
    });
  }

  _renderModal() {
    const bg = this.shadowRoot?.getElementById("sg-modal-bg");
    if (!bg) return;
    if (!this._modal) {
      bg.className = "modal-backdrop hidden";
      bg.innerHTML = "";
      return;
    }

    const devs = this._getEnrichedDevices();
    bg.className = "modal-backdrop";

    if (this._modal.type === "meta") {
      const d = devs.find((x) => x.mac === this._modal.mac);
      if (!d) {
        this._modal = null;
        this._renderModal();
        return;
      }
      const wLine = d.warranty_until
        ? `Válida até <strong>${this._esc(d.warranty_until)}</strong> (${
            d.warranty_days_left >= 0 ? `faltam ${d.warranty_days_left} dias` : `expirou há ${Math.abs(d.warranty_days_left)} dias`
          })`
        : "Preenche a data de compra para calcular a validade da garantia.";

      bg.innerHTML = `
        <div class="modal">
          <h2>${this._esc(d.name)}</h2>
          <div class="modal-sub">${this._esc(d.model || "Shelly")} · MAC <code>${this._esc(d.mac)}</code></div>

          <div class="field-row">
            <div class="field">
              <label>Data de compra</label>
              <input type="date" id="m-pdate" value="${this._esc(d.purchase_date || "")}" />
            </div>
            <div class="field">
              <label>Garantia (meses)</label>
              <input type="number" id="m-wmonths" min="0" max="120" value="${this._esc(d.warranty_months ?? 36)}" />
            </div>
          </div>
          <div class="modal-sub" style="margin-top:-4px;margin-bottom:12px">${wLine}</div>

          <div class="field-row">
            <div class="field">
              <label>Vendedor / Loja</label>
              <input type="text" id="m-vendor" placeholder="ex.: Shelly Store, Amazon ES..." value="${this._esc(d.vendor || "")}" />
            </div>
            <div class="field">
              <label>Nº de Fatura / Encomenda</label>
              <input type="text" id="m-invoice" placeholder="ex.: FT 2025/1234" value="${this._esc(d.invoice_number || "")}" />
            </div>
          </div>

          <div class="field">
            <label>Notas</label>
            <textarea id="m-notes" rows="2" placeholder="Observações, local exato, link da fatura...">${this._esc(d.notes || "")}</textarea>
          </div>

          <div class="modal-actions">
            <button class="btn" id="m-close">Cancelar</button>
            <button class="btn primary" id="m-save">Guardar Dados</button>
          </div>

          <div class="modal-section">
            <h2 style="font-size:0.98rem;margin-bottom:8px">Estado de Funcionamento / Avaria</h2>
            ${
              d.lifecycle === "faulty"
                ? `<div class="modal-sub">Marcado como <strong>Avariado</strong>${d.faulty_at ? ` em ${this._esc(d.faulty_at)}` : ""}${
                    d.faulty_reason ? ` — ${this._esc(d.faulty_reason)}` : ""
                  }. O backup está preservado para substituição.</div>
                  <div class="modal-actions" style="justify-content:flex-start">
                    <button class="btn" id="m-reactivate">Reativar dispositivo</button>
                  </div>`
                : d.lifecycle === "replaced"
                ? `<div class="modal-sub">Arquivado como <strong>Substituído</strong>${d.replaced_at ? ` em ${this._esc(d.replaced_at)}` : ""}${
                    d.replaced_by ? ` pelo MAC <code>${this._esc(d.replaced_by)}</code>` : ""
                  }.</div>
                  <div class="modal-actions" style="justify-content:flex-start">
                    <button class="btn" id="m-reactivate">Voltar a marcar como Ativo</button>
                  </div>`
                : `<div class="field">
                    <label>Motivo da avaria (opcional)</label>
                    <input type="text" id="m-reason" placeholder="ex.: Não liga, relé colado, sem Wi-Fi..." />
                  </div>
                  <div class="modal-actions" style="justify-content:flex-start">
                    <button class="btn danger" id="m-faulty">
                      <ha-icon icon="mdi:alert-circle-outline" style="--mdc-icon-size:16px"></ha-icon> Marcar como Avariado
                    </button>
                  </div>`
            }
          </div>
        </div>
      `;

      bg.querySelector("#m-close").addEventListener("click", () => {
        this._modal = null;
        this._renderModal();
      });
      bg.querySelector("#m-save").addEventListener("click", async () => {
        const ok = await this._call(
          `meta_${d.mac}`,
          "shelly_guard",
          "set_metadata",
          {
            mac: d.mac,
            purchase_date: bg.querySelector("#m-pdate").value,
            warranty_months: Number(bg.querySelector("#m-wmonths").value || 36),
            vendor: bg.querySelector("#m-vendor").value,
            invoice_number: bg.querySelector("#m-invoice").value,
            notes: bg.querySelector("#m-notes").value,
          },
          `Dados de garantia guardados para ${d.name}`,
          800
        );
        if (ok) {
          this._modal = null;
          this._renderModal();
        }
      });
      const faultyBtn = bg.querySelector("#m-faulty");
      if (faultyBtn) {
        faultyBtn.addEventListener("click", async () => {
          const reason = bg.querySelector("#m-reason")?.value || "";
          const ok = await this._call(
            `lc_${d.mac}`,
            "shelly_guard",
            "set_lifecycle",
            { mac: d.mac, lifecycle: "faulty", reason },
            `${d.name} movido para a lista de avariados`,
            800
          );
          if (ok) {
            this._modal = null;
            this._renderModal();
          }
        });
      }
      const reactBtn = bg.querySelector("#m-reactivate");
      if (reactBtn) {
        reactBtn.addEventListener("click", async () => {
          const ok = await this._call(
            `lc_${d.mac}`,
            "shelly_guard",
            "set_lifecycle",
            { mac: d.mac, lifecycle: "active", reason: "" },
            `${d.name} reativado`,
            800
          );
          if (ok) {
            this._modal = null;
            this._renderModal();
          }
        });
      }
      return;
    }

    if (this._modal.type === "replace") {
      const nd = this._modal.newDev;
      const candidates = devs
        .filter((x) => x.mac !== nd.mac && (x.lifecycle === "faulty" || (!x.online && x.lifecycle === "active")))
        .sort((a, b) => {
          const aFault = a.lifecycle === "faulty" ? 0 : 1;
          const bFault = b.lifecycle === "faulty" ? 0 : 1;
          if (aFault !== bFault) return aFault - bFault;
          const aSame = nd.model && a.model === nd.model ? 0 : 1;
          const bSame = nd.model && b.model === nd.model ? 0 : 1;
          return aSame - bSame;
        });

      const opts = candidates
        .map((c) => {
          const tag = c.lifecycle === "faulty" ? "[AVARIADO]" : "[OFFLINE]";
          const match = nd.model && c.model === nd.model ? " ★ Mesmo modelo" : "";
          const bk = c.has_backup ? "" : " (sem backup)";
          return `<option value="${this._esc(c.mac)}">${tag} ${this._esc(c.name)} (${this._esc(c.model || "?")})${match}${bk}</option>`;
        })
        .join("");

      bg.innerHTML = `
        <div class="modal">
          <h2>Novo Shelly detetado na rede</h2>
          <div class="modal-sub">
            <strong>${this._esc(nd.name)}</strong> ${nd.model ? `(${this._esc(nd.model)})` : ""} ·
            MAC <code>${this._esc(nd.mac)}</code> · ${this._esc(nd.host)}
          </div>

          <div class="field">
            <label>Substituir um dispositivo avariado ou offline (restaura automaticamente o backup)</label>
            <select id="r-old-mac">
              ${opts || `<option value="">Nenhum dispositivo avariado/offline disponível</option>`}
            </select>
          </div>

          <div class="modal-actions" style="justify-content:space-between">
            <button class="btn" id="r-new">
              <ha-icon icon="mdi:plus-circle-outline" style="--mdc-icon-size:16px"></ha-icon> É um dispositivo novo
            </button>
            <div style="display:flex;gap:8px">
              <button class="btn" id="r-later">Depois</button>
              <button class="btn primary" id="r-replace" ${candidates.length ? "" : "disabled"}>
                <ha-icon icon="mdi:swap-horizontal" style="--mdc-icon-size:16px"></ha-icon> Restaurar &amp; Substituir
              </button>
            </div>
          </div>
        </div>
      `;

      bg.querySelector("#r-later").addEventListener("click", () => {
        this._modal = null;
        this._renderModal();
      });
      bg.querySelector("#r-new").addEventListener("click", async () => {
        const ok = await this._call(
          `confirm_${nd.mac}`,
          "shelly_guard",
          "confirm_new_device",
          { mac: nd.mac },
          `${nd.name} registado como dispositivo novo`,
          2000
        );
        if (ok) {
          this._modal = null;
          this._renderModal();
        }
      });
      bg.querySelector("#r-replace").addEventListener("click", async () => {
        const oldMac = bg.querySelector("#r-old-mac").value;
        if (!oldMac) return;
        const oldDev = candidates.find((c) => c.mac === oldMac);
        if (!confirm(`Restaurar o backup de "${oldDev?.name || oldMac}" para o novo Shelly "${nd.name}"?`)) return;
        const ok = await this._call(
          `repl_${nd.mac}`,
          "shelly_guard",
          "replace_device",
          { old_mac: oldMac, new_mac: nd.mac },
          `Substituição iniciada: ${oldDev?.name || oldMac} → ${nd.name}`,
          4000
        );
        if (ok) {
          this._modal = null;
          this._renderModal();
        }
      });
    }
  }
}

class ShellyGuardCard extends ShellyGuardPanel {}

if (!customElements.get("shelly-guard-panel")) {
  customElements.define("shelly-guard-panel", ShellyGuardPanel);
}
if (!customElements.get("shelly-guard-card")) {
  customElements.define("shelly-guard-card", ShellyGuardCard);
}
