const SG_TRANSLATIONS = {
  en: {
    loading: "Loading status...",
    loading_devices: "Loading devices...",
    no_check_yet: "No check recorded yet",
    last_check: "Last check: {ts}",
    last_device: "Last device: {dev}",
    last_dev_backup: "Last backup: {dev}",
    btn_reload: "Reload",
    btn_reload_title: "Reload Shelly Guard integration",
    btn_backup: "Backup All",
    btn_backup_title: "Back up all Shelly devices",
    btn_check_all: "Full Check",
    btn_check_all_title: "Run full check on all devices",
    toast_done: "Action completed",
    toast_error: "Error: {err}",
    toast_reloaded: "Shelly Guard reloaded",
    toast_backup_started: "Full backup started",
    toast_check_started: "Full check started",
    toast_upgrade_started: "Upgrade started on {name}",
    toast_device_checked: "Check completed on {name}",
    toast_backup_changed: "Backup saved for {name} (new snapshot #{digest})",
    toast_backup_unchanged: "Backup verified for {name} (matches #{digest})",
    toast_restore_dry: "Dry-run simulated for {name}: {ok} steps planned",
    toast_restore_done: "Restore completed on {name}: {ok} steps ok",
    toast_meta_saved: "Warranty details saved for {name}",
    toast_marked_faulty: "{name} moved to faulty list",
    toast_reactivated: "{name} reactivated",
    toast_confirmed_new: "{name} registered and backed up",
    toast_replace_done: "Replaced {old} → {new} ({ok} steps restored)",
    kpi_devices: "Devices",
    kpi_online: "Online",
    kpi_offline: "Offline",
    kpi_faulty: "Faulty",
    kpi_backups: "Backups",
    kpi_upgrades: "Upgrades",
    kpi_re: "Range Extender",
    search_placeholder: "Filter by name, area, IP, MAC, vendor, invoice or firmware...",
    chip_all: "All ({n})",
    chip_offline: "Offline ({n})",
    chip_faulty: "Faulty ({n})",
    chip_upgrade: "Upgrade ({n})",
    chip_re: "Range Extender ({n})",
    chip_nobackup: "No Backup ({n})",
    chip_replaced: "Replaced ({n})",
    empty_filtered: "No devices match the current filter.",
    th_device: "Device",
    th_backup: "Backup",
    th_config: "Configuration",
    th_warranty: "Warranty",
    th_firmware: "Firmware",
    th_actions: "Actions",
    badge_online: "Online",
    badge_offline: "Offline",
    badge_reset: "Factory Reset!",
    badge_faulty: "Faulty",
    badge_replaced: "Replaced",
    badge_backup_yes: "Yes · {ts}",
    badge_backup_ver: "{n}v",
    badge_backup_no: "No backup",
    backup_tip_open: "Click to view backup versions, run Backup Now or Restore",
    badge_warranty_until: "Until {date}",
    badge_warranty_expiring: "Expires {days}d",
    badge_warranty_expired: "Expired",
    badge_warranty_register: "+ Register",
    warranty_tip_register: "Add purchase date, vendor and invoice",
    warranty_tip_until: "{vendor} · valid until {date}",
    warranty_tip_expiring: "Expires in {days} days ({date})",
    warranty_tip_expired: "Expired on {date}",
    hardened_ok: "Factory reset from switch disabled",
    hardened_warn: "Warning: factory reset from switch still enabled",
    hardened_short_ok: "Protected",
    hardened_short_warn: "Switch reset active",
    fw_updating: "Updating{pct}",
    btn_upgrade: "Upgrade",
    btn_up_to_date: "Up to date",
    btn_installing: "Installing...",
    btn_check: "Check",
    btn_check_title: "Re-run check and backup on this device",
    btn_backup_now: "Backup Now",
    btn_backup_now_title: "Immediately fetch and save this Shelly's configuration",
    btn_restore: "Restore",
    btn_restore_title: "Restore configuration onto this Shelly from a saved backup",
    btn_web_ui: "Web UI",
    btn_meta_title: "Device menu: Check, Backup Now, Restore, Warranty & Fault status",
    confirm_upgrade: "Install firmware update on {name}?",
    confirm_restore: "Apply backup restore ({ver}) onto {name}? The device may reboot.",
    confirm_force_backup: "This Shelly appears factory-reset! Overwrite your saved backup anyway?",
    rma_store: "Store: {v}",
    rma_invoice: "Invoice: {v}",
    rma_replaced_by: "Replaced by {v}",
    rma_replaces: "Replaces {v}",
    pending_title: "New Shelly detected:",
    pending_more: "(+{n} more)",
    pending_desc: "Register warranty details or replace a faulty/offline device with automatic backup restore.",
    pending_btn: "Configure / Replace",
    sec_ops: "Device Actions, Backup & Restore",
    ops_last_backup: "Latest backup",
    ops_digest: "Snapshot hash",
    ops_snapshots: "Saved versions",
    ops_hardening: "Switch reset lock",
    ops_none: "None yet",
    ops_versions_n: "{n} snapshot(s)",
    msg_backup_changed: "Saved! Parameter changes detected — created new snapshot #{digest} at {ts}.",
    msg_backup_unchanged: "Backup verified at {ts} — all parameters match snapshot #{digest}.",
    msg_reset_protected: "Warning: device appears factory-reset! Existing backup ({ts}) was preserved.",
    btn_force_backup: "Force overwrite backup",
    msg_check_ok_changed: "Check & hardening done — new backup snapshot #{digest} saved.",
    msg_check_ok_same: "Check & hardening done — backup verified (#{digest}).",
    restore_panel_title: "Restore Configuration",
    lbl_restore_source: "Backup source device",
    opt_this_device: "This device ({name})",
    lbl_restore_version: "Backup snapshot version",
    opt_latest_snapshot: "Latest ({ts} · #{digest})",
    opt_hist_snapshot: "{ts} · #{digest}{fw}",
    opt_loading_versions: "Loading saved snapshots...",
    opt_no_versions: "No backup snapshots found",
    lbl_restore_host: "Host / IP override (optional)",
    ph_restore_host: "Leave empty to use {host}",
    btn_dry_run: "Simulate (Dry Run)",
    btn_apply_restore: "Restore Now",
    restore_dry_header: "Dry-run simulation ({n} planned steps):",
    restore_done_header: "Restore completed: {ok} steps applied{warn}.",
    restore_warn_suffix: ", {n} warning(s)",
    sec_warranty: "Warranty, Invoice & Notes",
    btn_today: "Today",
    modal_warranty_valid: "Valid until <strong>{date}</strong> ({detail})",
    modal_days_left: "{n} days left",
    modal_days_ago: "expired {n} days ago",
    modal_warranty_empty: "Enter a purchase date to calculate warranty expiration.",
    lbl_purchase_date: "Purchase date",
    lbl_warranty_months: "Warranty (months)",
    lbl_vendor: "Vendor / Store",
    ph_vendor: "e.g. Shelly Store, Amazon...",
    lbl_invoice: "Invoice / Order number",
    ph_invoice: "e.g. INV-2026-1234",
    lbl_notes: "Notes",
    ph_notes: "Notes, exact installation box, invoice URL...",
    btn_close: "Close",
    btn_cancel: "Cancel",
    btn_save: "Save Warranty & Notes",
    sec_lifecycle: "Device Status / Fault & Replacement",
    faulty_summary: "Marked as <strong>Faulty</strong>{at}{reason}. Its latest backup is preserved for replacement.",
    replaced_summary: "Archived as <strong>Replaced</strong>{at}{by}.",
    on_date: " on {d}",
    by_mac: " by MAC <code>{m}</code>",
    btn_reactivate: "Reactivate device",
    btn_mark_active: "Mark as Active again",
    lbl_fault_reason: "Fault reason (optional)",
    ph_fault_reason: "e.g. Dead relay, no power, Wi-Fi failure...",
    btn_mark_faulty: "Mark as Faulty",
    lbl_replace_with_active: "Replace this faulty unit with an active Shelly on network",
    opt_select_replacement: "— Select replacement Shelly —",
    replace_title: "New Shelly detected on network",
    mode_new_title: "Brand-new Shelly",
    mode_new_desc: "Keep as a new installation, apply hardening and save initial backup.",
    mode_replace_title: "Replace Faulty / Offline Shelly",
    mode_replace_desc: "Automatically restore the faulty unit's backup onto this Shelly and archive the old one.",
    replace_label: "Select faulty or offline device to replace",
    replace_none: "No faulty or offline devices currently in list",
    tag_faulty: "[FAULTY]",
    tag_offline: "[OFFLINE]",
    same_model: " ★ Same model",
    no_backup_paren: " (no backup)",
    sec_new_warranty: "Purchase & Warranty Details (optional, saved immediately)",
    btn_is_new_save: "Save & Register New Shelly",
    btn_later: "Later",
    btn_restore_replace: "Restore Backup & Replace",
    confirm_replace: 'Restore the backup of "{old}" onto "{new}" and archive "{old}" as replaced?',
    cfg_static: "Static",
  },
  pt: {
    loading: "A carregar estado...",
    loading_devices: "A carregar dispositivos...",
    no_check_yet: "Sem verificação registada ainda",
    last_check: "Último check: {ts}",
    last_device: "Último check ind.: {dev}",
    last_dev_backup: "Último backup ind.: {dev}",
    btn_reload: "Reload",
    btn_reload_title: "Recarregar integração Shelly Guard",
    btn_backup: "Backup All",
    btn_backup_title: "Backup de todos os Shellys",
    btn_check_all: "Check Completo",
    btn_check_all_title: "Executar verificação completa",
    toast_done: "Ação executada",
    toast_error: "Erro: {err}",
    toast_reloaded: "Shelly Guard recarregado",
    toast_backup_started: "Backup completo iniciado",
    toast_check_started: "Check completo iniciado",
    toast_upgrade_started: "Upgrade iniciado em {name}",
    toast_device_checked: "Check concluído em {name}",
    toast_backup_changed: "Backup gravado para {name} (nova versão #{digest})",
    toast_backup_unchanged: "Backup confirmado para {name} (igual a #{digest})",
    toast_restore_dry: "Simulação concluída para {name}: {ok} passos previstos",
    toast_restore_done: "Restauro concluído em {name}: {ok} passos ok",
    toast_meta_saved: "Dados de garantia guardados para {name}",
    toast_marked_faulty: "{name} movido para a lista de avariados",
    toast_reactivated: "{name} reativado",
    toast_confirmed_new: "{name} registado e guardado em backup",
    toast_replace_done: "Substituído {old} → {new} ({ok} passos restaurados)",
    kpi_devices: "Dispositivos",
    kpi_online: "Online",
    kpi_offline: "Offline",
    kpi_faulty: "Avariados",
    kpi_backups: "Backups",
    kpi_upgrades: "Upgrades",
    kpi_re: "Range Extender",
    search_placeholder: "Filtrar por nome, área, IP, MAC, vendedor, fatura ou firmware...",
    chip_all: "Todos ({n})",
    chip_offline: "Offline ({n})",
    chip_faulty: "Avariados ({n})",
    chip_upgrade: "Com Upgrade ({n})",
    chip_re: "Range Extender ({n})",
    chip_nobackup: "Sem Backup ({n})",
    chip_replaced: "Substituídos ({n})",
    empty_filtered: "Nenhum dispositivo corresponde ao filtro atual.",
    th_device: "Dispositivo",
    th_backup: "Backup",
    th_config: "Configuração",
    th_warranty: "Garantia",
    th_firmware: "Firmware",
    th_actions: "Ações",
    badge_online: "Online",
    badge_offline: "Offline",
    badge_reset: "Modo Fábrica!",
    badge_faulty: "Avariado",
    badge_replaced: "Substituído",
    badge_backup_yes: "Sim · {ts}",
    badge_backup_ver: "{n}v",
    badge_backup_no: "Sem backup",
    backup_tip_open: "Clica para ver versões de backup, fazer Backup Now ou Restore",
    badge_warranty_until: "Até {date}",
    badge_warranty_expiring: "Expira {days}d",
    badge_warranty_expired: "Expirada",
    badge_warranty_register: "+ Registar",
    warranty_tip_register: "Adicionar data de compra, vendedor e fatura",
    warranty_tip_until: "{vendor} · válida até {date}",
    warranty_tip_expiring: "Expira em {days} dias ({date})",
    warranty_tip_expired: "Expirou em {date}",
    hardened_ok: "Reset por interruptor desativado",
    hardened_warn: "Atenção: reset por interruptor ainda ativo",
    hardened_short_ok: "Protegido",
    hardened_short_warn: "Reset switch ativo",
    fw_updating: "A atualizar{pct}",
    btn_upgrade: "Upgrade",
    btn_up_to_date: "Atualizado",
    btn_installing: "A instalar...",
    btn_check: "Check",
    btn_check_title: "Executar check, hardening e backup deste dispositivo",
    btn_backup_now: "Backup Now",
    btn_backup_now_title: "Ler parâmetros atuais deste Shelly e gravar já no backup",
    btn_restore: "Restore",
    btn_restore_title: "Restaurar configuração deste Shelly a partir do backup",
    btn_web_ui: "Web UI",
    btn_meta_title: "Menu individual: Check, Backup Now, Restore, Garantia, Notas e Avaria",
    confirm_upgrade: "Instalar atualização de firmware em {name}?",
    confirm_restore: "Aplicar o restauro do backup ({ver}) no Shelly {name}? O dispositivo poderá reiniciar.",
    confirm_force_backup: "Este Shelly aparenta estar em modo de fábrica! Queres mesmo sobrescrever o backup existente?",
    rma_store: "Loja: {v}",
    rma_invoice: "Fatura: {v}",
    rma_replaced_by: "Substituído por {v}",
    rma_replaces: "Substituiu {v}",
    pending_title: "Novo Shelly detetado:",
    pending_more: "(+{n} outro)",
    pending_desc: "Preenche já os dados de garantia/fatura ou escolhe substituir um dispositivo da lista de Avariados/Offline.",
    pending_btn: "Configurar / Substituir",
    sec_ops: "Ações Individuais, Backup & Restore",
    ops_last_backup: "Último backup",
    ops_digest: "Hash (Digest)",
    ops_snapshots: "Versões gravadas",
    ops_hardening: "Bloqueio Reset Switch",
    ops_none: "Sem backup",
    ops_versions_n: "{n} versão(ões)",
    msg_backup_changed: "Gravado no backup! Alterações de parâmetros detetadas — criada nova versão #{digest} às {ts}.",
    msg_backup_unchanged: "Backup confirmado às {ts} — todos os parâmetros coincidem com a versão #{digest}.",
    msg_reset_protected: "Atenção: o Shelly aparenta estar em modo de fábrica! O backup anterior ({ts}) foi preservado.",
    btn_force_backup: "Forçar gravação por cima",
    msg_check_ok_changed: "Check e proteção concluídos — gravada nova versão de backup #{digest}.",
    msg_check_ok_same: "Check e proteção concluídos — backup verificado (#{digest}).",
    restore_panel_title: "Restaurar Configuração Individual",
    lbl_restore_source: "Origem do backup",
    opt_this_device: "Este dispositivo ({name})",
    lbl_restore_version: "Versão / Snapshot a restaurar",
    opt_latest_snapshot: "Mais recente ({ts} · #{digest})",
    opt_hist_snapshot: "{ts} · #{digest}{fw}",
    opt_loading_versions: "A carregar versões guardadas...",
    opt_no_versions: "Sem versões de backup disponíveis",
    lbl_restore_host: "IP / Host alternativo (opcional)",
    ph_restore_host: "Vazio para usar {host}",
    btn_dry_run: "Simular (Dry Run)",
    btn_apply_restore: "Restaurar Agora",
    restore_dry_header: "Simulação Dry-Run ({n} passos planeados):",
    restore_done_header: "Restauro concluído: {ok} passos aplicados{warn}.",
    restore_warn_suffix: ", {n} aviso(s)",
    sec_warranty: "Garantia, Fatura & Notas",
    btn_today: "Hoje",
    modal_warranty_valid: "Válida até <strong>{date}</strong> ({detail})",
    modal_days_left: "faltam {n} dias",
    modal_days_ago: "expirou há {n} dias",
    modal_warranty_empty: "Preenche a data de compra para calcular a validade da garantia.",
    lbl_purchase_date: "Data de compra",
    lbl_warranty_months: "Garantia (meses)",
    lbl_vendor: "Vendedor / Loja",
    ph_vendor: "ex.: Shelly Store, Amazon ES...",
    lbl_invoice: "Nº de Fatura / Encomenda",
    ph_invoice: "ex.: FT 2026/1234",
    lbl_notes: "Notas",
    ph_notes: "Observações, caixa de aparelhagem, link da fatura...",
    btn_close: "Fechar",
    btn_cancel: "Cancelar",
    btn_save: "Guardar Garantia & Notas",
    sec_lifecycle: "Estado de Funcionamento / Avaria & Substituição",
    faulty_summary: "Marcado como <strong>Avariado</strong>{at}{reason}. O último backup está preservado para substituição.",
    replaced_summary: "Arquivado como <strong>Substituído</strong>{at}{by}.",
    on_date: " em {d}",
    by_mac: " pelo MAC <code>{m}</code>",
    btn_reactivate: "Reativar dispositivo",
    btn_mark_active: "Voltar a marcar como Ativo",
    lbl_fault_reason: "Motivo da avaria (opcional)",
    ph_fault_reason: "ex.: Não liga, relé colado, sem Wi-Fi...",
    btn_mark_faulty: "Marcar como Avariado",
    lbl_replace_with_active: "Substituir este avariado por um Shelly ativo na rede",
    opt_select_replacement: "— Escolher Shelly substituto —",
    replace_title: "Novo Shelly detetado na rede",
    mode_new_title: "É um Shelly Novo",
    mode_new_desc: "Registar como nova instalação, aplicar proteção anti-reset e fazer já o primeiro backup.",
    mode_replace_title: "Substituir Shelly Avariado / Offline",
    mode_replace_desc: "Restaurar automaticamente o backup do avariado neste novo Shelly e arquivar o antigo.",
    replace_label: "Escolhe o dispositivo Avariado ou Offline a substituir",
    replace_none: "Nenhum dispositivo na lista de Avariados/Offline",
    tag_faulty: "[AVARIADO]",
    tag_offline: "[OFFLINE]",
    same_model: " ★ Mesmo modelo",
    no_backup_paren: " (sem backup)",
    sec_new_warranty: "Dados de Compra, Garantia & Notas (guardados de imediato)",
    btn_is_new_save: "Guardar & Registar Novo Shelly",
    btn_later: "Depois",
    btn_restore_replace: "Restaurar Backup & Substituir",
    confirm_replace: 'Restaurar o backup de "{old}" no novo Shelly "{new}" e arquivar "{old}" como substituído?',
    cfg_static: "Estático",
  },
};

class ShellyGuardPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._lang = "en";
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
    this._modal = null;
    this._backupsCache = {};
    this._seenPending = new Set();
  }

  setConfig(config) {
    this._config = config || {};
  }

  getCardSize() {
    return 12;
  }

  _detectLang(hass) {
    const raw = (hass?.locale?.language || hass?.language || navigator?.language || "en").toLowerCase();
    return raw.startsWith("pt") ? "pt" : "en";
  }

  _t(key, vars = {}) {
    const dict = SG_TRANSLATIONS[this._lang] || SG_TRANSLATIONS.en;
    let str = dict[key] ?? SG_TRANSLATIONS.en[key] ?? key;
    for (const [k, v] of Object.entries(vars)) {
      str = str.replaceAll(`{${k}}`, String(v ?? ""));
    }
    return str;
  }

  _localizeConfigType(ct) {
    if (!ct) return "";
    return String(ct).replace(/\b(Static|Estático)\b/g, this._t("cfg_static"));
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
    const newLang = this._detectLang(hass);
    const langChanged = this._rendered && newLang !== this._lang;
    this._lang = newLang;
    this._hass = hass;

    if (langChanged) {
      this._captureModalDraft();
      this._renderShell();
      this._renderBody();
      this._renderModal();
    }

    const menuBtn = this.shadowRoot?.getElementById("sg-menu-btn");
    if (menuBtn) menuBtn.hass = hass;

    const sg = hass?.states?.["sensor.shelly_guard"];
    const ts = sg?.attributes?.state_ts || sg?.last_updated || null;
    if (first || (ts && ts !== this._lastStateTs)) {
      this._lastStateTs = ts;
      this._fetchState();
    } else if (this._rendered && !langChanged) {
      this._renderBody();
    }
  }

  async _fetchState(forceRenderModal = false) {
    if (!this._hass) return;
    this._loading = true;
    if (!this._rendered) this._renderShell();
    let openedNewModal = false;
    try {
      const data = await this._hass.callApi("GET", "shelly_guard/state");
      if (data && Array.isArray(data.devices)) {
        this._data = data;
        const pending = data.pending_new_devices || [];
        if (pending.length && !this._modal) {
          const unseen = pending.find((p) => !this._seenPending.has(p.mac));
          if (unseen) {
            this._seenPending.add(unseen.mac);
            this._openReplaceModal(unseen);
            openedNewModal = true;
          }
        }
      }
    } catch (e) {
      console.warn("shelly-guard-panel fetch failed:", e);
    } finally {
      this._loading = false;
      this._renderBody();
      if (openedNewModal || forceRenderModal) {
        this._renderModal();
      }
    }
  }

  async _loadBackupsForMac(mac, force = false) {
    if (!this._hass || !mac) return [];
    if (!force && Array.isArray(this._backupsCache[mac])) {
      return this._backupsCache[mac];
    }
    try {
      const res = await this._hass.callApi("GET", `shelly_guard/backups/${encodeURIComponent(mac)}`);
      const list = Array.isArray(res?.backups) ? res.backups : [];
      this._backupsCache[mac] = list;
      if (this._modal && this._modal.type === "meta") {
        this._captureModalDraft();
        this._renderModal();
      }
      return list;
    } catch (e) {
      console.warn("shelly-guard-panel backups fetch failed:", e);
      return [];
    }
  }

  async _callAction(key, payload, okToast = null) {
    if (!this._hass || this._busy[key]) return null;
    this._busy[key] = true;
    this._captureModalDraft();
    this._renderBody();
    if (this._modal) this._renderModal();
    try {
      const res = await this._hass.callApi("POST", "shelly_guard/action", payload);
      if (res?.error && !res?.reset_detected) {
        this._showToast(this._t("toast_error", { err: res.error }), "err");
      } else if (okToast) {
        const msg = typeof okToast === "function" ? okToast(res) : okToast;
        if (msg) this._showToast(msg, res?.reset_detected ? "info" : "ok");
      }
      await this._fetchState(false);
      return res;
    } catch (e) {
      this._showToast(this._t("toast_error", { err: e?.message || e }), "err");
      return null;
    } finally {
      delete this._busy[key];
      this._renderBody();
      if (this._modal) this._renderModal();
    }
  }

  _esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  _todayIso() {
    const d = new Date();
    const pad = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  }

  _fmtShortDate(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return String(iso).slice(0, 16).replace("T", " ");
    const pad = (n) => String(n).padStart(2, "0");
    return `${pad(d.getDate())}/${pad(d.getMonth() + 1)} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  _fmtFullDate(iso) {
    if (!iso) return "";
    return String(iso).replace("T", " ").slice(0, 19);
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
    }, 4800);
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

  async _call(key, domain, service, data = {}, okMsg = null, refreshMs = 1500) {
    if (!this._hass || this._busy[key]) return false;
    this._busy[key] = true;
    this._captureModalDraft();
    this._renderBody();
    if (this._modal) this._renderModal();
    try {
      await this._hass.callService(domain, service, data);
      this._showToast(okMsg || this._t("toast_done"), "ok");
      setTimeout(() => this._fetchState(false), refreshMs);
      return true;
    } catch (e) {
      this._showToast(this._t("toast_error", { err: e?.message || e }), "err");
      return false;
    } finally {
      setTimeout(() => {
        delete this._busy[key];
        this._renderBody();
        if (this._modal) this._renderModal();
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

  _openMetaModal(mac, showRestore = false) {
    const devs = this._getEnrichedDevices();
    const d = devs.find((x) => x.mac === mac);
    this._modal = {
      type: "meta",
      mac,
      showRestore: Boolean(showRestore),
      restoreSourceMac: mac,
      restoreVersion: "latest.json",
      restoreHost: "",
      opsFeedback: null,
      restoreOutput: null,
      draft: d
        ? {
            pdate: d.purchase_date || "",
            wmonths: d.warranty_months ?? 36,
            vendor: d.vendor || "",
            invoice: d.invoice_number || "",
            notes: d.notes || "",
            reason: "",
          }
        : null,
    };
    this._renderModal();
    this._loadBackupsForMac(mac, true);
  }

  _openReplaceModal(newDev) {
    const devs = this._getEnrichedDevices();
    const existing = devs.find((x) => x.mac === newDev.mac);
    const hasFaulty = devs.some((x) => x.mac !== newDev.mac && x.lifecycle === "faulty");
    this._modal = {
      type: "replace",
      newDev,
      mode: hasFaulty ? "replace" : "new",
      oldMac: "",
      draft: {
        pdate: existing?.purchase_date || "",
        wmonths: existing?.warranty_months ?? 36,
        vendor: existing?.vendor || "",
        invoice: existing?.invoice_number || "",
        notes: existing?.notes || "",
      },
    };
  }

  _captureModalDraft() {
    if (!this._modal) return;
    const bg = this.shadowRoot?.getElementById("sg-modal-bg");
    if (!bg || bg.classList.contains("hidden")) return;
    if (this._modal.type === "meta") {
      const pdate = bg.querySelector("#m-pdate");
      if (pdate) {
        this._modal.draft = {
          pdate: pdate.value,
          wmonths: bg.querySelector("#m-wmonths")?.value ?? 36,
          vendor: bg.querySelector("#m-vendor")?.value ?? "",
          invoice: bg.querySelector("#m-invoice")?.value ?? "",
          notes: bg.querySelector("#m-notes")?.value ?? "",
          reason: bg.querySelector("#m-reason")?.value ?? "",
        };
      }
      const rSrc = bg.querySelector("#m-r-source");
      if (rSrc) this._modal.restoreSourceMac = rSrc.value;
      const rVer = bg.querySelector("#m-r-version");
      if (rVer) this._modal.restoreVersion = rVer.value;
      const rHost = bg.querySelector("#m-r-host");
      if (rHost) this._modal.restoreHost = rHost.value;
    } else if (this._modal.type === "replace") {
      const pdate = bg.querySelector("#r-pdate");
      if (pdate) {
        this._modal.draft = {
          pdate: pdate.value,
          wmonths: bg.querySelector("#r-wmonths")?.value ?? 36,
          vendor: bg.querySelector("#r-vendor")?.value ?? "",
          invoice: bg.querySelector("#r-invoice")?.value ?? "",
          notes: bg.querySelector("#r-notes")?.value ?? "",
        };
      }
      const oldSel = bg.querySelector("#r-old-mac");
      if (oldSel) this._modal.oldMac = oldSel.value;
    }
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
        .wrap { max-width: 1500px; margin: 0 auto; padding: 16px; }
        .header {
          display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px;
          background: var(--card-background-color, #1c1c1c);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.08));
          border-radius: 14px; padding: 16px 20px; margin-bottom: 14px;
        }
        .title-block { display: flex; align-items: center; gap: 12px; }
        .logo {
          width: 42px; height: 42px; border-radius: 12px;
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 18%, transparent);
          color: var(--primary-color, #03a9f4);
          display: flex; align-items: center; justify-content: center;
        }
        .title { font-size: 1.25rem; font-weight: 600; margin: 0; line-height: 1.2; }
        .subtitle { font-size: 0.82rem; color: var(--secondary-text-color, #9e9e9e); margin-top: 3px; }
        .header-actions { display: flex; flex-wrap: wrap; gap: 8px; }
        button.btn, a.btn {
          display: inline-flex; align-items: center; gap: 6px;
          border: 1px solid var(--divider-color, rgba(255,255,255,0.14));
          background: var(--secondary-background-color, rgba(255,255,255,0.06));
          color: var(--primary-text-color, #fff);
          border-radius: 10px; padding: 8px 13px; font-size: 0.85rem; font-weight: 500;
          cursor: pointer; text-decoration: none;
          transition: background 0.15s, border-color 0.15s, opacity 0.15s;
        }
        button.btn:hover:not(:disabled), a.btn:hover {
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 16%, var(--secondary-background-color, #2a2a2a));
          border-color: var(--primary-color, #03a9f4);
        }
        button.btn.primary { background: var(--primary-color, #03a9f4); border-color: var(--primary-color, #03a9f4); color: #fff; }
        button.btn.primary:hover:not(:disabled) { filter: brightness(1.08); }
        button.btn.ok-btn {
          background: color-mix(in srgb, var(--success-color, #4caf50) 20%, transparent);
          border-color: var(--success-color, #4caf50); color: var(--success-color, #4caf50);
        }
        button.btn.ok-btn:hover:not(:disabled) { background: var(--success-color, #4caf50); color: #fff; }
        button.btn.warn-btn {
          background: color-mix(in srgb, var(--warning-color, #ff9800) 18%, transparent);
          border-color: var(--warning-color, #ff9800); color: var(--warning-color, #ff9800);
        }
        button.btn.warn-btn:hover:not(:disabled) { background: var(--warning-color, #ff9800); color: #111; }
        button.btn.danger { background: color-mix(in srgb, var(--error-color, #f44336) 20%, transparent); border-color: var(--error-color, #f44336); color: var(--error-color, #f44336); }
        button.btn.danger:hover:not(:disabled) { background: var(--error-color, #f44336); color: #fff; }
        button.btn.upgrade-active { background: var(--warning-color, #ff9800); border-color: var(--warning-color, #ff9800); color: #111; font-weight: 600; }
        button.btn.upgrade-active:hover:not(:disabled) { filter: brightness(1.08); }
        button.btn.sm, a.btn.sm { padding: 5px 9px; font-size: 0.78rem; border-radius: 8px; }
        button.btn:disabled { opacity: 0.35; cursor: not-allowed; }
        .link-btn {
          background: none; border: none; color: var(--primary-color, #03a9f4);
          font-size: 0.75rem; cursor: pointer; padding: 0 4px; text-decoration: underline;
        }

        .pending-banner {
          display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px;
          background: color-mix(in srgb, var(--warning-color, #ff9800) 14%, var(--card-background-color, #1c1c1c));
          border: 1px solid var(--warning-color, #ff9800);
          border-radius: 12px; padding: 12px 16px; margin-bottom: 14px;
        }
        .pending-banner.hidden { display: none; }

        .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(135px, 1fr)); gap: 10px; margin-bottom: 14px; }
        .kpi {
          background: var(--card-background-color, #1c1c1c);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.08));
          border-radius: 12px; padding: 12px 14px; cursor: pointer; transition: border-color 0.15s;
        }
        .kpi:hover { border-color: var(--primary-color, #03a9f4); }
        .kpi.active { border-color: var(--primary-color, #03a9f4); box-shadow: 0 0 0 1px var(--primary-color, #03a9f4); }
        .kpi-label { font-size: 0.74rem; color: var(--secondary-text-color, #9e9e9e); text-transform: uppercase; letter-spacing: 0.04em; }
        .kpi-val { font-size: 1.4rem; font-weight: 700; margin-top: 4px; }
        .kpi-val.ok { color: var(--success-color, #4caf50); }
        .kpi-val.err { color: var(--error-color, #f44336); }
        .kpi-val.warn { color: var(--warning-color, #ff9800); }
        .kpi-val.info { color: var(--primary-color, #03a9f4); }

        .toolbar { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 12px; }
        .search {
          flex: 1 1 240px; max-width: 380px;
          background: var(--card-background-color, #1c1c1c);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.14));
          color: var(--primary-text-color, #fff);
          border-radius: 10px; padding: 9px 12px; font-size: 0.88rem; outline: none;
        }
        .search:focus { border-color: var(--primary-color, #03a9f4); }
        .chips { display: flex; flex-wrap: wrap; gap: 6px; }
        .chip {
          border: 1px solid var(--divider-color, rgba(255,255,255,0.14));
          background: var(--card-background-color, #1c1c1c);
          color: var(--secondary-text-color, #aaa);
          border-radius: 999px; padding: 6px 12px; font-size: 0.8rem; cursor: pointer;
        }
        .chip.active {
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 20%, transparent);
          border-color: var(--primary-color, #03a9f4);
          color: var(--primary-text-color, #fff); font-weight: 600;
        }

        .table-card {
          background: var(--card-background-color, #1c1c1c);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.08));
          border-radius: 14px; overflow: hidden;
        }
        .table-scroll { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
        th {
          text-align: left; font-size: 0.73rem; text-transform: uppercase; letter-spacing: 0.04em;
          color: var(--secondary-text-color, #9e9e9e); padding: 12px 13px;
          border-bottom: 1px solid var(--divider-color, rgba(255,255,255,0.1)); white-space: nowrap;
        }
        td { padding: 10px 13px; border-bottom: 1px solid var(--divider-color, rgba(255,255,255,0.06)); vertical-align: middle; }
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
          display: inline-flex; align-items: center; gap: 4px;
          padding: 3px 8px; border-radius: 999px; font-size: 0.74rem; font-weight: 500; white-space: nowrap;
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
          position: fixed; inset: 0; background: rgba(0, 0, 0, 0.68); z-index: 1000;
          display: flex; align-items: center; justify-content: center; padding: 14px;
        }
        .modal-backdrop.hidden { display: none; }
        .modal {
          width: 100%; max-width: 600px; background: var(--card-background-color, #1e1e1e);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.14)); border-radius: 16px;
          padding: 20px; box-shadow: 0 18px 48px rgba(0,0,0,0.55); max-height: 92vh; overflow-y: auto;
        }
        .modal-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
        .modal h2 { margin: 0 0 5px; font-size: 1.14rem; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
        .modal-sub { font-size: 0.81rem; color: var(--secondary-text-color, #9e9e9e); margin-bottom: 14px; }
        .modal-sub a { color: var(--primary-color, #03a9f4); text-decoration: none; }
        .modal-sub a:hover { text-decoration: underline; }
        .sec-title {
          font-size: 0.86rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;
          color: var(--secondary-text-color, #b0b0b0); margin: 0 0 10px;
        }
        .ops-grid {
          display: grid; grid-template-columns: repeat(auto-fit, minmax(125px, 1fr)); gap: 8px;
          background: var(--primary-background-color, #141414);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.08));
          border-radius: 10px; padding: 10px 12px; margin-bottom: 10px;
        }
        .ops-item-lbl { font-size: 0.7rem; color: var(--secondary-text-color, #9a9a9a); text-transform: uppercase; }
        .ops-item-val { font-size: 0.82rem; font-weight: 600; margin-top: 2px; word-break: break-all; }
        .ops-bar { display: flex; flex-wrap: wrap; gap: 7px; align-items: center; }
        .ops-alert {
          margin-top: 10px; padding: 9px 12px; border-radius: 9px; font-size: 0.81rem; line-height: 1.4;
          border: 1px solid var(--primary-color, #03a9f4);
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 12%, transparent);
        }
        .ops-alert.ok { border-color: var(--success-color, #4caf50); background: color-mix(in srgb, var(--success-color, #4caf50) 13%, transparent); }
        .ops-alert.warn { border-color: var(--warning-color, #ff9800); background: color-mix(in srgb, var(--warning-color, #ff9800) 14%, transparent); }
        .ops-alert.err { border-color: var(--error-color, #f44336); background: color-mix(in srgb, var(--error-color, #f44336) 14%, transparent); }
        .restore-box {
          margin-top: 12px; padding: 12px; border-radius: 11px;
          background: var(--primary-background-color, #131313);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.14));
        }
        .ops-log {
          margin: 8px 0 0; padding: 8px 10px; border-radius: 8px; max-height: 150px; overflow-y: auto;
          background: rgba(0,0,0,0.35); font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          font-size: 0.74rem; white-space: pre-wrap; color: var(--primary-text-color, #ddd);
        }

        .mode-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
        @media (max-width: 520px) { .mode-cards { grid-template-columns: 1fr; } }
        .mode-card {
          border: 1px solid var(--divider-color, rgba(255,255,255,0.16));
          background: var(--primary-background-color, #141414);
          border-radius: 11px; padding: 11px 13px; cursor: pointer; transition: border-color 0.15s, background 0.15s;
        }
        .mode-card.active {
          border-color: var(--primary-color, #03a9f4);
          background: color-mix(in srgb, var(--primary-color, #03a9f4) 14%, var(--primary-background-color, #141414));
        }
        .mode-card.disabled { opacity: 0.45; cursor: not-allowed; }
        .mode-card-title { font-weight: 600; font-size: 0.88rem; display: flex; align-items: center; gap: 6px; }
        .mode-card-desc { font-size: 0.76rem; color: var(--secondary-text-color, #aaa); margin-top: 4px; line-height: 1.35; }

        .field { margin-bottom: 11px; }
        .field label { display: flex; align-items: center; justify-content: space-between; font-size: 0.78rem; color: var(--secondary-text-color, #aaa); margin-bottom: 4px; }
        .field input, .field select, .field textarea {
          width: 100%; background: var(--primary-background-color, #121212);
          border: 1px solid var(--divider-color, rgba(255,255,255,0.16));
          color: var(--primary-text-color, #fff); border-radius: 8px; padding: 8px 10px;
          font-size: 0.86rem; font-family: inherit;
        }
        .field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        @media (max-width: 480px) { .field-row { grid-template-columns: 1fr; } }
        .modal-section { border-top: 1px solid var(--divider-color, rgba(255,255,255,0.1)); margin-top: 15px; padding-top: 14px; }
        .modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 14px; flex-wrap: wrap; }

        .toast {
          position: fixed; bottom: 20px; right: 20px; z-index: 1100;
          padding: 10px 16px; border-radius: 10px; font-size: 0.86rem; font-weight: 500;
          box-shadow: 0 6px 20px rgba(0,0,0,0.35); background: var(--card-background-color, #222);
          border: 1px solid var(--primary-color, #03a9f4); color: var(--primary-text-color, #fff);
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
              <div class="subtitle" id="sg-sub">${this._esc(this._t("loading"))}</div>
            </div>
          </div>
          <div class="header-actions">
            <button class="btn" id="btn-reload" title="${this._esc(this._t("btn_reload_title"))}">
              <ha-icon icon="mdi:reload"></ha-icon> ${this._esc(this._t("btn_reload"))}
            </button>
            <button class="btn" id="btn-backup" title="${this._esc(this._t("btn_backup_title"))}">
              <ha-icon icon="mdi:content-save-all"></ha-icon> ${this._esc(this._t("btn_backup"))}
            </button>
            <button class="btn primary" id="btn-check" title="${this._esc(this._t("btn_check_all_title"))}">
              <ha-icon icon="mdi:shield-refresh"></ha-icon> ${this._esc(this._t("btn_check_all"))}
            </button>
          </div>
        </div>

        <div class="pending-banner hidden" id="sg-pending"></div>
        <div class="kpis" id="sg-kpis"></div>

        <div class="toolbar">
          <input class="search" id="sg-search" type="search" value="${this._esc(this._search)}" placeholder="${this._esc(this._t("search_placeholder"))}" />
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
      this._call("reload", "shelly_guard", "reload", {}, this._t("toast_reloaded"))
    );
    this.shadowRoot.getElementById("btn-backup").addEventListener("click", () =>
      this._call("backup", "shelly_guard", "backup_all", {}, this._t("toast_backup_started"))
    );
    this.shadowRoot.getElementById("btn-check").addEventListener("click", () =>
      this._call("check", "shelly_guard", "check", {}, this._t("toast_check_started"))
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
      const tip = this._t("warranty_tip_until", { vendor: d.vendor || this._t("th_warranty"), date: d.warranty_until });
      return `<span class="badge ok clickable" data-act="meta" data-mac="${this._esc(d.mac)}" title="${this._esc(tip)}">${this._esc(this._t("badge_warranty_until", { date: this._fmtMonthYear(d.warranty_until) }))}</span>`;
    }
    if (st === "expiring") {
      const tip = this._t("warranty_tip_expiring", { days: d.warranty_days_left, date: d.warranty_until });
      return `<span class="badge warn clickable" data-act="meta" data-mac="${this._esc(d.mac)}" title="${this._esc(tip)}">${this._esc(this._t("badge_warranty_expiring", { days: d.warranty_days_left }))}</span>`;
    }
    if (st === "expired") {
      const tip = this._t("warranty_tip_expired", { date: d.warranty_until });
      return `<span class="badge muted clickable" data-act="meta" data-mac="${this._esc(d.mac)}" title="${this._esc(tip)}">${this._esc(this._t("badge_warranty_expired"))}</span>`;
    }
    return `<span class="badge muted clickable" data-act="meta" data-mac="${this._esc(d.mac)}" title="${this._esc(this._t("warranty_tip_register"))}">${this._esc(this._t("badge_warranty_register"))}</span>`;
  }

  _renderBody() {
    if (!this._rendered) this._renderShell();
    const devs = this._getEnrichedDevices();
    const pending = this._data?.pending_new_devices || [];
    const sg = this._hass?.states?.["sensor.shelly_guard"];
    const lastCheck = sg?.attributes?.last_check || this._data?.status?.last_check || this._data?.updated_at;
    const lastDev = sg?.attributes?.last_device_check || this._data?.status?.last_device_check;
    const lastDevBk = sg?.attributes?.last_device_backup || this._data?.status?.last_device_backup;

    const sub = this.shadowRoot.getElementById("sg-sub");
    if (sub) {
      const parts = [];
      if (lastCheck) parts.push(this._t("last_check", { ts: this._fmtShortDate(lastCheck) }));
      if (lastDev) parts.push(this._t("last_device", { dev: lastDev }));
      if (lastDevBk) parts.push(this._t("last_dev_backup", { dev: lastDevBk }));
      sub.textContent = parts.length ? parts.join(" · ") : this._t("no_check_yet");
    }

    const pendingEl = this.shadowRoot.getElementById("sg-pending");
    if (pendingEl) {
      if (pending.length) {
        const first = pending[0];
        pendingEl.className = "pending-banner";
        pendingEl.innerHTML = `
          <div>
            <strong>${this._esc(this._t("pending_title"))}</strong> ${this._esc(first.name)}
            ${first.model ? `(${this._esc(first.model)})` : ""} · <code>${this._esc(first.mac)}</code>
            ${pending.length > 1 ? ` ${this._esc(this._t("pending_more", { n: pending.length - 1 }))}` : ""}
            <div style="font-size:0.8rem;color:var(--secondary-text-color,#ccc);margin-top:2px">
              ${this._esc(this._t("pending_desc"))}
            </div>
          </div>
          <button class="btn primary sm" id="btn-open-replace">
            <ha-icon icon="mdi:plus-box-outline" style="--mdc-icon-size:16px"></ha-icon> ${this._esc(this._t("pending_btn"))}
          </button>
        `;
        pendingEl.querySelector("#btn-open-replace").addEventListener("click", () => {
          this._openReplaceModal(first);
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
        { id: "all", label: this._t("kpi_devices"), val: total, cls: "info" },
        { id: "online", label: this._t("kpi_online"), val: online, cls: "ok" },
        { id: "offline", label: this._t("kpi_offline"), val: offline, cls: offline ? "err" : "ok" },
        { id: "faulty", label: this._t("kpi_faulty"), val: faulty, cls: faulty ? "warn" : "ok" },
        { id: "nobackup", label: this._t("kpi_backups"), val: `${withBk}/${total}`, cls: noBk ? "warn" : "ok" },
        { id: "upgrade", label: this._t("kpi_upgrades"), val: upgrades, cls: upgrades ? "warn" : "ok" },
        { id: "re", label: this._t("kpi_re"), val: reCount, cls: "info" },
      ];
      kpisEl.innerHTML = cards
        .map(
          (c) => `
          <div class="kpi ${this._filter === c.id ? "active" : ""}" data-filter="${c.id}">
            <div class="kpi-label">${this._esc(c.label)}</div>
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
        ["all", this._t("chip_all", { n: total })],
        ["offline", this._t("chip_offline", { n: offline })],
        ["faulty", this._t("chip_faulty", { n: faulty })],
        ["upgrade", this._t("chip_upgrade", { n: upgrades })],
        ["re", this._t("chip_re", { n: reCount })],
        ["nobackup", this._t("chip_nobackup", { n: noBk })],
      ];
      if (replaced > 0) filters.push(["replaced", this._t("chip_replaced", { n: replaced })]);
      chipsEl.innerHTML = filters
        .map(
          ([id, lbl]) =>
            `<button class="chip ${this._filter === id ? "active" : ""}" data-filter="${id}">${this._esc(lbl)}</button>`
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
        const hay = `${d.name} ${d.area} ${d.host} ${d.port} ${d.mac} ${d.model} ${d.config_type} ${d.installed} ${d.vendor} ${d.invoice_number} ${d.faulty_reason} ${d.notes}`.toLowerCase();
        if (!hay.includes(this._search)) return false;
      }
      return true;
    });

    const tableEl = this.shadowRoot.getElementById("sg-table");
    if (!tableEl) return;

    if (!filtered.length) {
      tableEl.innerHTML = `<div class="empty">${this._esc(
        this._loading ? this._t("loading_devices") : this._t("empty_filtered")
      )}</div>`;
      return;
    }

    const rowsHtml = filtered
      .map((d) => {
        const addr = d.host ? (Number(d.port || 80) !== 80 ? `${d.host}:${d.port}` : d.host) : "";
        const dotCls = d.lifecycle === "faulty" || d.reset ? "rst" : d.online ? "on" : "off";
        const rowCls = d.lifecycle === "faulty" ? "faulty-row" : d.online ? "" : "offline-row";
        const lcBadge =
          d.reset
            ? `<span class="badge warn">${this._esc(this._t("badge_reset"))}</span>`
            : d.lifecycle === "faulty"
            ? `<span class="badge warn">${this._esc(this._t("badge_faulty"))}</span>`
            : d.lifecycle === "replaced"
            ? `<span class="badge muted">${this._esc(this._t("badge_replaced"))}</span>`
            : "";

        const digestInfo = d.backup_digest ? ` · #${d.backup_digest.slice(0, 8)}` : "";
        const verSuffix = d.backup_count > 1 ? ` (${this._t("badge_backup_ver", { n: d.backup_count })})` : "";
        const bkTip = `${d.backup_at || ""}${digestInfo} — ${this._t("backup_tip_open")}`;
        const bkHtml = d.has_backup
          ? `<span class="badge ok clickable" data-act="meta" data-mac="${this._esc(d.mac)}" title="${this._esc(bkTip)}">${this._esc(this._t("badge_backup_yes", { ts: this._fmtShortDate(d.backup_at) }) + verSuffix)}</span>`
          : `<span class="badge miss clickable" data-act="meta" data-mac="${this._esc(d.mac)}" title="${this._esc(this._t("backup_tip_open"))}">${this._esc(this._t("badge_backup_no"))}</span>`;

        const cfgCls = d.isRE ? "re" : "cfg";
        const cfgText = this._localizeConfigType(d.config_type || `Gen${d.gen}`);
        const hardIcon =
          d.hardened === true
            ? ` <ha-icon icon="mdi:shield-check" style="--mdc-icon-size:15px;color:var(--success-color,#4caf50)" title="${this._esc(this._t("hardened_ok"))}"></ha-icon>`
            : d.hardened === false
            ? ` <ha-icon icon="mdi:shield-alert" style="--mdc-icon-size:15px;color:var(--warning-color,#ff9800)" title="${this._esc(this._t("hardened_warn"))}"></ha-icon>`
            : "";

        let fwHtml = `<span>${this._esc(d.installed)}</span>`;
        if (d.inProgress) {
          const pct = d.progress != null ? ` (${d.progress}%)` : "...";
          fwHtml += `<span class="fw-new">${this._esc(this._t("fw_updating", { pct }))}</span>`;
        } else if (d.hasUpgrade && d.latest) {
          fwHtml += `<span class="fw-new">→ ${this._esc(d.latest)}</span>`;
        }

        const rmaParts = [];
        if (d.vendor) rmaParts.push(this._t("rma_store", { v: d.vendor }));
        if (d.invoice_number) rmaParts.push(this._t("rma_invoice", { v: d.invoice_number }));
        if (d.faulty_reason) rmaParts.push(d.faulty_reason);
        if (d.replaced_by) rmaParts.push(this._t("rma_replaced_by", { v: d.replaced_by }));
        const rmaInfo =
          (d.lifecycle === "faulty" || d.lifecycle === "replaced") && rmaParts.length
            ? `<div class="rma-line">${this._esc(rmaParts.join(" · "))}</div>`
            : "";

        const upgKey = `upg_${d.mac}`;
        const chkKey = `chk_${d.mac}`;
        const upgDisabled = !d.hasUpgrade || d.inProgress || Boolean(this._busy[upgKey]);
        const upgCls = d.hasUpgrade && !d.inProgress ? "btn sm upgrade-active" : "btn sm";
        const upgLabel = d.inProgress
          ? this._t("btn_installing")
          : d.hasUpgrade
          ? this._t("btn_upgrade")
          : this._t("btn_up_to_date");
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
            <td><span class="badge ${cfgCls}">${this._esc(cfgText)}</span>${hardIcon}</td>
            <td>
              ${this._warrantyBadgeHtml(d)}
              ${d.vendor ? `<div class="dev-meta">${this._esc(d.vendor)}</div>` : ""}
            </td>
            <td class="fw-cell">${fwHtml}</td>
            <td>
              <div class="actions-cell">
                <button class="btn sm" data-act="meta" data-mac="${this._esc(d.mac)}" title="${this._esc(this._t("btn_meta_title"))}">
                  <ha-icon icon="mdi:tune-variant" style="--mdc-icon-size:15px"></ha-icon>
                </button>
                <button class="${upgCls}" data-act="upgrade" data-mac="${this._esc(d.mac)}" data-entity="${this._esc(d.update_entity)}" data-name="${this._esc(d.name)}" ${upgDisabled ? "disabled" : ""}>
                  <ha-icon icon="mdi:package-up" style="--mdc-icon-size:15px"></ha-icon> ${this._esc(upgLabel)}
                </button>
                <button class="btn sm" data-act="check" data-mac="${this._esc(d.mac)}" data-name="${this._esc(d.name)}" ${chkBusy || d.lifecycle === "replaced" ? "disabled" : ""} title="${this._esc(this._t("btn_check_title"))}">
                  <ha-icon icon="mdi:refresh" class="${chkBusy ? "spin" : ""}" style="--mdc-icon-size:15px"></ha-icon> ${this._esc(this._t("btn_check"))}
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
            <th>${this._esc(this._t("th_device"))}</th>
            <th>${this._esc(this._t("th_backup"))}</th>
            <th>${this._esc(this._t("th_config"))}</th>
            <th>${this._esc(this._t("th_warranty"))}</th>
            <th>${this._esc(this._t("th_firmware"))}</th>
            <th style="text-align:right">${this._esc(this._t("th_actions"))}</th>
          </tr>
        </thead>
        <tbody>${rowsHtml}</tbody>
      </table>
    `;

    tableEl.querySelectorAll("[data-act='meta']").forEach((el) => {
      el.addEventListener("click", () => {
        this._openMetaModal(el.dataset.mac, false);
      });
    });

    tableEl.querySelectorAll("button[data-act='upgrade']").forEach((btn) => {
      btn.addEventListener("click", () => {
        const entity = btn.dataset.entity;
        const name = btn.dataset.name;
        const mac = btn.dataset.mac;
        if (!entity) return;
        if (!confirm(this._t("confirm_upgrade", { name }))) return;
        this._call(`upg_${mac}`, "update", "install", { entity_id: entity }, this._t("toast_upgrade_started", { name }), 3000);
      });
    });

    tableEl.querySelectorAll("button[data-act='check']").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const mac = btn.dataset.mac;
        const name = btn.dataset.name;
        await this._callAction(`chk_${mac}`, { action: "check_device", mac }, () =>
          this._t("toast_device_checked", { name })
        );
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

      const draft = this._modal.draft || {
        pdate: d.purchase_date || "",
        wmonths: d.warranty_months ?? 36,
        vendor: d.vendor || "",
        invoice: d.invoice_number || "",
        notes: d.notes || "",
        reason: "",
      };

      const addr = d.host ? (Number(d.port || 80) !== 80 ? `${d.host}:${d.port}` : d.host) : "";
      const stBadge = d.reset
        ? `<span class="badge warn">${this._esc(this._t("badge_reset"))}</span>`
        : d.lifecycle === "faulty"
        ? `<span class="badge warn">${this._esc(this._t("badge_faulty"))}</span>`
        : d.lifecycle === "replaced"
        ? `<span class="badge muted">${this._esc(this._t("badge_replaced"))}</span>`
        : d.online
        ? `<span class="badge ok">${this._esc(this._t("badge_online"))}</span>`
        : `<span class="badge miss">${this._esc(this._t("badge_offline"))}</span>`;

      const chkBusy = Boolean(this._busy[`chk_${d.mac}`]);
      const bkBusy = Boolean(this._busy[`bk_${d.mac}`]);
      const rstDryBusy = Boolean(this._busy[`rstdry_${d.mac}`]);
      const rstNowBusy = Boolean(this._busy[`rstnow_${d.mac}`]);
      const upgBusy = Boolean(this._busy[`upg_${d.mac}`]);
      const isReplaced = d.lifecycle === "replaced";

      const hardVal =
        d.hardened === true
          ? `<span style="color:var(--success-color,#4caf50)">${this._esc(this._t("hardened_short_ok"))}</span>`
          : d.hardened === false
          ? `<span style="color:var(--warning-color,#ff9800)">${this._esc(this._t("hardened_short_warn"))}</span>`
          : "—";

      const fb = this._modal.opsFeedback;
      let fbHtml = "";
      if (fb) {
        fbHtml = `<div class="ops-alert ${this._esc(fb.kind || "ok")}">
          ${this._esc(fb.text)}
          ${
            fb.allowForce
              ? `<div style="margin-top:6px"><button class="btn sm warn-btn" id="m-force-bk">${this._esc(this._t("btn_force_backup"))}</button></div>`
              : ""
          }
        </div>`;
      }

      // Restore sub-panel
      const srcMac = this._modal.restoreSourceMac || d.mac;
      const srcBackups = this._backupsCache[srcMac];
      const otherWithBk = devs.filter((x) => x.mac !== d.mac && x.has_backup);
      const srcOpts = [
        `<option value="${this._esc(d.mac)}" ${srcMac === d.mac ? "selected" : ""}>${this._esc(this._t("opt_this_device", { name: d.name }))}</option>`,
        ...otherWithBk.map(
          (o) =>
            `<option value="${this._esc(o.mac)}" ${srcMac === o.mac ? "selected" : ""}>${this._esc(o.name)} (${this._esc(o.model || "Shelly")} · ${this._esc(o.mac)})</option>`
        ),
      ].join("");

      let verOpts = "";
      if (!Array.isArray(srcBackups)) {
        verOpts = `<option value="latest.json">${this._esc(this._t("opt_loading_versions"))}</option>`;
      } else if (!srcBackups.length) {
        verOpts = `<option value="">${this._esc(this._t("opt_no_versions"))}</option>`;
      } else {
        verOpts = srcBackups
          .map((b) => {
            const dg = (b.digest || "").slice(0, 8) || "—";
            const ts = this._fmtFullDate(b.saved_at) || b.file;
            const fw = b.fw ? ` · FW ${b.fw}` : "";
            const lbl = b.is_latest
              ? this._t("opt_latest_snapshot", { ts, digest: dg })
              : this._t("opt_hist_snapshot", { ts, digest: dg, fw });
            const sel = (this._modal.restoreVersion || "latest.json") === b.file ? "selected" : "";
            return `<option value="${this._esc(b.file)}" ${sel}>${this._esc(lbl)}</option>`;
          })
          .join("");
      }

      const rOut = this._modal.restoreOutput;
      let rOutHtml = "";
      if (rOut) {
        const hdr = rOut.dry_run
          ? this._t("restore_dry_header", { n: (rOut.done || []).length })
          : this._t("restore_done_header", {
              ok: (rOut.done || []).length,
              warn: (rOut.failed || []).length ? this._t("restore_warn_suffix", { n: rOut.failed.length }) : "",
            });
        const lines = [
          ...(rOut.done || []).map((x) => `✓ ${x}`),
          ...(rOut.failed || []).map((x) => `⚠ ${x}`),
        ].join("\n");
        const cls = (rOut.failed || []).length ? "warn" : "ok";
        rOutHtml = `
          <div class="ops-alert ${cls}" style="margin-top:10px">
            <strong>${this._esc(hdr)}</strong>
            ${lines ? `<pre class="ops-log">${this._esc(lines)}</pre>` : ""}
          </div>
        `;
      }

      const restoreBoxHtml = this._modal.showRestore
        ? `
          <div class="restore-box">
            <div class="sec-title" style="margin-bottom:8px">${this._esc(this._t("restore_panel_title"))}</div>
            <div class="field-row">
              <div class="field">
                <label>${this._esc(this._t("lbl_restore_source"))}</label>
                <select id="m-r-source">${srcOpts}</select>
              </div>
              <div class="field">
                <label>${this._esc(this._t("lbl_restore_version"))}</label>
                <select id="m-r-version">${verOpts}</select>
              </div>
            </div>
            <div class="field">
              <label>${this._esc(this._t("lbl_restore_host"))}</label>
              <input type="text" id="m-r-host" value="${this._esc(this._modal.restoreHost || "")}" placeholder="${this._esc(this._t("ph_restore_host", { host: addr || "IP" }))}" />
            </div>
            <div class="ops-bar" style="justify-content:flex-end">
              <button class="btn sm" id="m-r-dry" ${rstDryBusy || rstNowBusy || (Array.isArray(srcBackups) && !srcBackups.length) ? "disabled" : ""}>
                <ha-icon icon="mdi:eye-check-outline" class="${rstDryBusy ? "spin" : ""}" style="--mdc-icon-size:15px"></ha-icon> ${this._esc(this._t("btn_dry_run"))}
              </button>
              <button class="btn sm warn-btn" id="m-r-apply" ${rstNowBusy || rstDryBusy || (Array.isArray(srcBackups) && !srcBackups.length) ? "disabled" : ""}>
                <ha-icon icon="mdi:backup-restore" class="${rstNowBusy ? "spin" : ""}" style="--mdc-icon-size:15px"></ha-icon> ${this._esc(this._t("btn_apply_restore"))}
              </button>
            </div>
            ${rOutHtml}
          </div>
        `
        : "";

      const wLine = d.warranty_until
        ? this._t("modal_warranty_valid", {
            date: this._esc(d.warranty_until),
            detail:
              d.warranty_days_left >= 0
                ? this._t("modal_days_left", { n: d.warranty_days_left })
                : this._t("modal_days_ago", { n: Math.abs(d.warranty_days_left) }),
          })
        : this._esc(this._t("modal_warranty_empty"));

      const activeTargets = devs.filter((x) => x.mac !== d.mac && x.lifecycle === "active" && x.online);
      const faultyReplaceHtml =
        d.lifecycle === "faulty" && d.has_backup && activeTargets.length
          ? `<div class="field" style="margin-top:12px">
              <label>${this._esc(this._t("lbl_replace_with_active"))}</label>
              <div style="display:flex;gap:8px;flex-wrap:wrap">
                <select id="m-repl-target" style="flex:1 1 220px">
                  <option value="">${this._esc(this._t("opt_select_replacement"))}</option>
                  ${activeTargets
                    .map((t) => {
                      const sm = d.model && t.model === d.model ? this._t("same_model") : "";
                      return `<option value="${this._esc(t.mac)}">${this._esc(t.name)} (${this._esc(t.model || "Shelly")} · ${this._esc(t.mac)})${this._esc(sm)}</option>`;
                    })
                    .join("")}
                </select>
                <button class="btn sm primary" id="m-repl-go">
                  <ha-icon icon="mdi:swap-horizontal" style="--mdc-icon-size:15px"></ha-icon> ${this._esc(this._t("btn_restore_replace"))}
                </button>
              </div>
            </div>`
          : "";

      const lifecycleHtml =
        d.lifecycle === "faulty"
          ? `<div class="modal-sub">${this._t("faulty_summary", {
              at: d.faulty_at ? this._t("on_date", { d: this._esc(d.faulty_at) }) : "",
              reason: d.faulty_reason ? ` — ${this._esc(d.faulty_reason)}` : "",
            })}</div>
            <div class="modal-actions" style="justify-content:flex-start;margin-top:8px">
              <button class="btn sm" id="m-reactivate">${this._esc(this._t("btn_reactivate"))}</button>
            </div>
            ${faultyReplaceHtml}`
          : d.lifecycle === "replaced"
          ? `<div class="modal-sub">${this._t("replaced_summary", {
              at: d.replaced_at ? this._t("on_date", { d: this._esc(d.replaced_at) }) : "",
              by: d.replaced_by ? this._t("by_mac", { m: this._esc(d.replaced_by) }) : "",
            })}</div>
            <div class="modal-actions" style="justify-content:flex-start;margin-top:8px">
              <button class="btn sm" id="m-reactivate">${this._esc(this._t("btn_mark_active"))}</button>
            </div>`
          : `<div class="field">
              <label>${this._esc(this._t("lbl_fault_reason"))}</label>
              <input type="text" id="m-reason" value="${this._esc(draft.reason || "")}" placeholder="${this._esc(this._t("ph_fault_reason"))}" />
            </div>
            <div class="modal-actions" style="justify-content:flex-start;margin-top:8px">
              <button class="btn sm danger" id="m-faulty">
                <ha-icon icon="mdi:alert-circle-outline" style="--mdc-icon-size:15px"></ha-icon> ${this._esc(this._t("btn_mark_faulty"))}
              </button>
            </div>`;

      bg.innerHTML = `
        <div class="modal">
          <div class="modal-head">
            <div>
              <h2>${this._esc(d.name)} ${stBadge}</h2>
              <div class="modal-sub">
                ${this._esc(d.model || "Shelly")} · Gen${this._esc(d.gen || 1)} · MAC <code>${this._esc(d.mac)}</code>
                ${addr ? ` · <a href="http://${this._esc(addr)}" target="_blank" rel="noopener">${this._esc(addr)} ↗</a>` : ""}
                ${d.replaces ? ` · ${this._esc(this._t("rma_replaces", { v: d.replaces }))}` : ""}
              </div>
            </div>
          </div>

          <div class="sec-title">${this._esc(this._t("sec_ops"))}</div>
          <div class="ops-grid">
            <div>
              <div class="ops-item-lbl">${this._esc(this._t("ops_last_backup"))}</div>
              <div class="ops-item-val">${d.has_backup ? this._esc(this._fmtFullDate(d.backup_at)) : this._esc(this._t("ops_none"))}</div>
            </div>
            <div>
              <div class="ops-item-lbl">${this._esc(this._t("ops_digest"))}</div>
              <div class="ops-item-val">${d.backup_digest ? `<code>#${this._esc(d.backup_digest.slice(0, 10))}</code>` : "—"}</div>
            </div>
            <div>
              <div class="ops-item-lbl">${this._esc(this._t("ops_snapshots"))}</div>
              <div class="ops-item-val">${this._esc(this._t("ops_versions_n", { n: d.backup_count || 0 }))}</div>
            </div>
            <div>
              <div class="ops-item-lbl">${this._esc(this._t("ops_hardening"))}</div>
              <div class="ops-item-val">${hardVal}</div>
            </div>
          </div>

          <div class="ops-bar">
            <button class="btn sm" id="m-act-check" ${chkBusy || isReplaced ? "disabled" : ""} title="${this._esc(this._t("btn_check_title"))}">
              <ha-icon icon="mdi:shield-refresh" class="${chkBusy ? "spin" : ""}" style="--mdc-icon-size:15px"></ha-icon> ${this._esc(this._t("btn_check"))}
            </button>
            <button class="btn sm ok-btn" id="m-act-backup" ${bkBusy || isReplaced ? "disabled" : ""} title="${this._esc(this._t("btn_backup_now_title"))}">
              <ha-icon icon="mdi:content-save-check" class="${bkBusy ? "spin" : ""}" style="--mdc-icon-size:15px"></ha-icon> ${this._esc(this._t("btn_backup_now"))}
            </button>
            <button class="btn sm ${this._modal.showRestore ? "primary" : ""}" id="m-act-restore" ${isReplaced ? "disabled" : ""} title="${this._esc(this._t("btn_restore_title"))}">
              <ha-icon icon="mdi:backup-restore" style="--mdc-icon-size:15px"></ha-icon> ${this._esc(this._t("btn_restore"))}
            </button>
            ${
              d.hasUpgrade || d.inProgress
                ? `<button class="btn sm upgrade-active" id="m-act-upgrade" ${d.inProgress || upgBusy ? "disabled" : ""}>
                    <ha-icon icon="mdi:package-up" style="--mdc-icon-size:15px"></ha-icon> ${this._esc(d.inProgress ? this._t("btn_installing") : `${this._t("btn_upgrade")} (${d.latest})`)}
                  </button>`
                : ""
            }
            ${
              addr
                ? `<a class="btn sm" href="http://${this._esc(addr)}" target="_blank" rel="noopener">
                    <ha-icon icon="mdi:open-in-new" style="--mdc-icon-size:15px"></ha-icon> ${this._esc(this._t("btn_web_ui"))}
                  </a>`
                : ""
            }
          </div>
          ${fbHtml}
          ${restoreBoxHtml}

          <div class="modal-section">
            <div class="sec-title">${this._esc(this._t("sec_warranty"))}</div>
            <div class="field-row">
              <div class="field">
                <label>
                  <span>${this._esc(this._t("lbl_purchase_date"))}</span>
                  <button type="button" class="link-btn" id="m-pdate-today">${this._esc(this._t("btn_today"))}</button>
                </label>
                <input type="date" id="m-pdate" value="${this._esc(draft.pdate || "")}" />
              </div>
              <div class="field">
                <label><span>${this._esc(this._t("lbl_warranty_months"))}</span></label>
                <input type="number" id="m-wmonths" min="0" max="120" value="${this._esc(draft.wmonths ?? 36)}" />
              </div>
            </div>
            <div class="modal-sub" style="margin-top:-4px;margin-bottom:11px">${wLine}</div>

            <div class="field-row">
              <div class="field">
                <label><span>${this._esc(this._t("lbl_vendor"))}</span></label>
                <input type="text" id="m-vendor" placeholder="${this._esc(this._t("ph_vendor"))}" value="${this._esc(draft.vendor || "")}" />
              </div>
              <div class="field">
                <label><span>${this._esc(this._t("lbl_invoice"))}</span></label>
                <input type="text" id="m-invoice" placeholder="${this._esc(this._t("ph_invoice"))}" value="${this._esc(draft.invoice || "")}" />
              </div>
            </div>

            <div class="field">
              <label><span>${this._esc(this._t("lbl_notes"))}</span></label>
              <textarea id="m-notes" rows="2" placeholder="${this._esc(this._t("ph_notes"))}">${this._esc(draft.notes || "")}</textarea>
            </div>

            <div class="modal-actions">
              <button class="btn" id="m-close">${this._esc(this._t("btn_close"))}</button>
              <button class="btn primary" id="m-save">${this._esc(this._t("btn_save"))}</button>
            </div>
          </div>

          <div class="modal-section">
            <div class="sec-title">${this._esc(this._t("sec_lifecycle"))}</div>
            ${lifecycleHtml}
          </div>
        </div>
      `;

      bg.querySelector("#m-close").addEventListener("click", () => {
        this._modal = null;
        this._renderModal();
      });

      bg.querySelector("#m-pdate-today").addEventListener("click", () => {
        const inp = bg.querySelector("#m-pdate");
        if (inp) inp.value = this._todayIso();
      });

      bg.querySelector("#m-act-check").addEventListener("click", async () => {
        const res = await this._callAction(`chk_${d.mac}`, { action: "check_device", mac: d.mac }, () =>
          this._t("toast_device_checked", { name: d.name })
        );
        if (res && this._modal?.type === "meta") {
          if (res.reset_detected) {
            this._modal.opsFeedback = {
              kind: "warn",
              text: this._t("msg_reset_protected", { ts: this._fmtFullDate(res.backup_preserved) || "latest" }),
              allowForce: false,
            };
          } else if (res.ok) {
            const dg = (res.digest || "").slice(0, 8);
            this._modal.opsFeedback = {
              kind: "ok",
              text: this._t(res.changed ? "msg_check_ok_changed" : "msg_check_ok_same", { digest: dg }),
            };
            await this._loadBackupsForMac(d.mac, true);
          } else if (res.error) {
            this._modal.opsFeedback = { kind: "err", text: this._t("toast_error", { err: res.error }) };
          }
          this._renderModal();
        }
      });

      const runBackupNow = async (force = false) => {
        const res = await this._callAction(`bk_${d.mac}`, { action: "backup_device", mac: d.mac, force }, (r) => {
          if (!r?.ok) return null;
          const dg = (r.digest || "").slice(0, 8);
          return this._t(r.changed ? "toast_backup_changed" : "toast_backup_unchanged", {
            name: d.name,
            digest: dg,
          });
        });
        if (res && this._modal?.type === "meta") {
          if (res.reset_detected) {
            this._modal.opsFeedback = {
              kind: "warn",
              text: this._t("msg_reset_protected", { ts: this._fmtFullDate(res.backup_preserved) || "latest" }),
              allowForce: true,
            };
          } else if (res.ok) {
            const dg = (res.digest || "").slice(0, 8);
            const ts = this._fmtFullDate(res.saved_at);
            this._modal.opsFeedback = {
              kind: "ok",
              text: this._t(res.changed ? "msg_backup_changed" : "msg_backup_unchanged", { digest: dg, ts }),
            };
            await this._loadBackupsForMac(d.mac, true);
          } else if (res.error) {
            this._modal.opsFeedback = { kind: "err", text: this._t("toast_error", { err: res.error }) };
          }
          this._renderModal();
        }
      };

      bg.querySelector("#m-act-backup").addEventListener("click", () => runBackupNow(false));

      const forceBtn = bg.querySelector("#m-force-bk");
      if (forceBtn) {
        forceBtn.addEventListener("click", () => {
          if (!confirm(this._t("confirm_force_backup"))) return;
          runBackupNow(true);
        });
      }

      bg.querySelector("#m-act-restore").addEventListener("click", () => {
        this._captureModalDraft();
        this._modal.showRestore = !this._modal.showRestore;
        if (this._modal.showRestore) {
          this._loadBackupsForMac(this._modal.restoreSourceMac || d.mac, true);
        }
        this._renderModal();
      });

      const upgBtn = bg.querySelector("#m-act-upgrade");
      if (upgBtn && d.update_entity) {
        upgBtn.addEventListener("click", () => {
          if (!confirm(this._t("confirm_upgrade", { name: d.name }))) return;
          this._call(`upg_${d.mac}`, "update", "install", { entity_id: d.update_entity }, this._t("toast_upgrade_started", { name: d.name }), 3000);
        });
      }

      const rSrcSel = bg.querySelector("#m-r-source");
      if (rSrcSel) {
        rSrcSel.addEventListener("change", (e) => {
          this._captureModalDraft();
          this._modal.restoreSourceMac = e.target.value;
          this._modal.restoreVersion = "latest.json";
          this._modal.restoreOutput = null;
          this._renderModal();
          this._loadBackupsForMac(this._modal.restoreSourceMac, true);
        });
      }

      const runRestore = async (dryRun) => {
        this._captureModalDraft();
        const ver = this._modal.restoreVersion || "latest.json";
        const bmac = this._modal.restoreSourceMac || d.mac;
        const hostOv = (this._modal.restoreHost || "").trim();
        if (!dryRun && !confirm(this._t("confirm_restore", { ver, name: d.name }))) return;
        const key = dryRun ? `rstdry_${d.mac}` : `rstnow_${d.mac}`;
        const res = await this._callAction(
          key,
          {
            action: "restore",
            mac: d.mac,
            backup_mac: bmac !== d.mac ? bmac : null,
            version: ver,
            host: hostOv || null,
            dry_run: dryRun,
          },
          (r) => {
            if (!r?.ok) return null;
            const okCount = (r.done || []).length;
            return this._t(dryRun ? "toast_restore_dry" : "toast_restore_done", { name: d.name, ok: okCount });
          }
        );
        if (res && this._modal?.type === "meta") {
          if (res.ok) {
            this._modal.restoreOutput = res;
          } else if (res.error) {
            this._modal.opsFeedback = { kind: "err", text: this._t("toast_error", { err: res.error }) };
          }
          this._renderModal();
        }
      };

      const dryBtn = bg.querySelector("#m-r-dry");
      if (dryBtn) dryBtn.addEventListener("click", () => runRestore(true));
      const applyBtn = bg.querySelector("#m-r-apply");
      if (applyBtn) applyBtn.addEventListener("click", () => runRestore(false));

      bg.querySelector("#m-save").addEventListener("click", async () => {
        this._captureModalDraft();
        const drf = this._modal.draft;
        const ok = await this._call(
          `meta_${d.mac}`,
          "shelly_guard",
          "set_metadata",
          {
            mac: d.mac,
            purchase_date: drf.pdate,
            warranty_months: Number(drf.wmonths || 36),
            vendor: drf.vendor,
            invoice_number: drf.invoice,
            notes: drf.notes,
          },
          this._t("toast_meta_saved", { name: d.name }),
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
            this._t("toast_marked_faulty", { name: d.name }),
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
            this._t("toast_reactivated", { name: d.name }),
            800
          );
          if (ok) {
            this._modal = null;
            this._renderModal();
          }
        });
      }

      const replGoBtn = bg.querySelector("#m-repl-go");
      if (replGoBtn) {
        replGoBtn.addEventListener("click", async () => {
          const newMac = bg.querySelector("#m-repl-target")?.value || "";
          if (!newMac) return;
          const targetDev = activeTargets.find((x) => x.mac === newMac);
          const newName = targetDev?.name || newMac;
          if (!confirm(this._t("confirm_replace", { old: d.name, new: newName }))) return;
          const res = await this._callAction(
            `repl_${d.mac}`,
            { action: "replace_device", old_mac: d.mac, new_mac: newMac },
            (r) =>
              r?.ok
                ? this._t("toast_replace_done", { old: d.name, new: newName, ok: (r.done || []).length })
                : null
          );
          if (res?.ok) {
            this._modal = null;
            this._renderModal();
          }
        });
      }
      return;
    }

    if (this._modal.type === "replace") {
      const nd = this._modal.newDev;
      const draft = this._modal.draft || { pdate: "", wmonths: 36, vendor: "", invoice: "", notes: "" };
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

      const canReplace = candidates.length > 0;
      const mode = canReplace && this._modal.mode === "replace" ? "replace" : "new";
      this._modal.mode = mode;

      const selectedOld = this._modal.oldMac || (candidates[0]?.mac ?? "");
      const opts = candidates
        .map((c) => {
          const tag = c.lifecycle === "faulty" ? this._t("tag_faulty") : this._t("tag_offline");
          const match = nd.model && c.model === nd.model ? this._t("same_model") : "";
          const bk = c.has_backup ? ` · ${this._fmtShortDate(c.backup_at)}` : this._t("no_backup_paren");
          const sel = c.mac === selectedOld ? "selected" : "";
          return `<option value="${this._esc(c.mac)}" ${sel}>${this._esc(tag)} ${this._esc(c.name)} (${this._esc(c.model || "?")})${this._esc(match)}${this._esc(bk)}</option>`;
        })
        .join("");

      const submitBusy = Boolean(this._busy[`onboard_${nd.mac}`]);

      bg.innerHTML = `
        <div class="modal">
          <h2>${this._esc(this._t("replace_title"))}</h2>
          <div class="modal-sub">
            <strong>${this._esc(nd.name)}</strong> ${nd.model ? `(${this._esc(nd.model)})` : ""} ·
            MAC <code>${this._esc(nd.mac)}</code> · ${this._esc(nd.host)}
          </div>

          <div class="mode-cards">
            <div class="mode-card ${mode === "new" ? "active" : ""}" id="r-mode-new">
              <div class="mode-card-title">
                <ha-icon icon="mdi:plus-circle-outline" style="--mdc-icon-size:17px"></ha-icon>
                ${this._esc(this._t("mode_new_title"))}
              </div>
              <div class="mode-card-desc">${this._esc(this._t("mode_new_desc"))}</div>
            </div>
            <div class="mode-card ${mode === "replace" ? "active" : ""} ${canReplace ? "" : "disabled"}" id="r-mode-replace">
              <div class="mode-card-title">
                <ha-icon icon="mdi:swap-horizontal" style="--mdc-icon-size:17px"></ha-icon>
                ${this._esc(this._t("mode_replace_title"))}
              </div>
              <div class="mode-card-desc">${this._esc(canReplace ? this._t("mode_replace_desc") : this._t("replace_none"))}</div>
            </div>
          </div>

          ${
            mode === "replace"
              ? `<div class="field">
                  <label><span>${this._esc(this._t("replace_label"))}</span></label>
                  <select id="r-old-mac">
                    ${opts || `<option value="">${this._esc(this._t("replace_none"))}</option>`}
                  </select>
                </div>`
              : ""
          }

          <div class="modal-section">
            <div class="sec-title">${this._esc(this._t("sec_new_warranty"))}</div>
            <div class="field-row">
              <div class="field">
                <label>
                  <span>${this._esc(this._t("lbl_purchase_date"))}</span>
                  <button type="button" class="link-btn" id="r-pdate-today">${this._esc(this._t("btn_today"))}</button>
                </label>
                <input type="date" id="r-pdate" value="${this._esc(draft.pdate || "")}" />
              </div>
              <div class="field">
                <label><span>${this._esc(this._t("lbl_warranty_months"))}</span></label>
                <input type="number" id="r-wmonths" min="0" max="120" value="${this._esc(draft.wmonths ?? 36)}" />
              </div>
            </div>

            <div class="field-row">
              <div class="field">
                <label><span>${this._esc(this._t("lbl_vendor"))}</span></label>
                <input type="text" id="r-vendor" placeholder="${this._esc(this._t("ph_vendor"))}" value="${this._esc(draft.vendor || "")}" />
              </div>
              <div class="field">
                <label><span>${this._esc(this._t("lbl_invoice"))}</span></label>
                <input type="text" id="r-invoice" placeholder="${this._esc(this._t("ph_invoice"))}" value="${this._esc(draft.invoice || "")}" />
              </div>
            </div>

            <div class="field">
              <label><span>${this._esc(this._t("lbl_notes"))}</span></label>
              <textarea id="r-notes" rows="2" placeholder="${this._esc(this._t("ph_notes"))}">${this._esc(draft.notes || "")}</textarea>
            </div>
          </div>

          <div class="modal-actions" style="justify-content:space-between">
            <button class="btn" id="r-later" ${submitBusy ? "disabled" : ""}>${this._esc(this._t("btn_later"))}</button>
            <button class="btn primary" id="r-submit" ${submitBusy ? "disabled" : ""}>
              <ha-icon icon="${mode === "replace" ? "mdi:swap-horizontal" : "mdi:check-circle-outline"}" class="${submitBusy ? "spin" : ""}" style="--mdc-icon-size:16px"></ha-icon>
              ${this._esc(mode === "replace" ? this._t("btn_restore_replace") : this._t("btn_is_new_save"))}
            </button>
          </div>
        </div>
      `;

      bg.querySelector("#r-mode-new").addEventListener("click", () => {
        this._captureModalDraft();
        this._modal.mode = "new";
        this._renderModal();
      });
      bg.querySelector("#r-mode-replace").addEventListener("click", () => {
        if (!canReplace) return;
        this._captureModalDraft();
        this._modal.mode = "replace";
        this._renderModal();
      });
      bg.querySelector("#r-pdate-today").addEventListener("click", () => {
        const inp = bg.querySelector("#r-pdate");
        if (inp) inp.value = this._todayIso();
      });
      bg.querySelector("#r-later").addEventListener("click", () => {
        this._modal = null;
        this._renderModal();
      });

      bg.querySelector("#r-submit").addEventListener("click", async () => {
        this._captureModalDraft();
        const drf = this._modal.draft;
        const metaFields = {
          purchase_date: drf.pdate,
          warranty_months: Number(drf.wmonths || 36),
          vendor: drf.vendor,
          invoice_number: drf.invoice,
          notes: drf.notes,
        };

        if (mode === "new") {
          const res = await this._callAction(
            `onboard_${nd.mac}`,
            { action: "confirm_new_device", mac: nd.mac, ...metaFields },
            () => this._t("toast_confirmed_new", { name: nd.name })
          );
          if (res?.ok) {
            this._modal = null;
            this._renderModal();
          }
        } else {
          const oldMac = bg.querySelector("#r-old-mac")?.value || "";
          if (!oldMac) return;
          const oldDev = candidates.find((c) => c.mac === oldMac);
          const oldName = oldDev?.name || oldMac;
          if (!confirm(this._t("confirm_replace", { old: oldName, new: nd.name }))) return;
          const res = await this._callAction(
            `onboard_${nd.mac}`,
            { action: "replace_device", old_mac: oldMac, new_mac: nd.mac, ...metaFields },
            (r) =>
              r?.ok
                ? this._t("toast_replace_done", { old: oldName, new: nd.name, ok: (r.done || []).length })
                : null
          );
          if (res?.ok) {
            this._modal = null;
            this._renderModal();
          }
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
