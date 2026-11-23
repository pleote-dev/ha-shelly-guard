# Shelly Guard — Home Assistant Backup, Hardening, Auto-Restore & Dashboard

**Shelly Guard** protege todos os teus dispositivos **Shelly (Gen1, Gen2, Gen3 e Gen4)** integrados no Home Assistant contra perdas de configuração e *factory resets* acidentais, com **backup automático versionado**, **restauro automático**, **suporte nativo a Range Extender** e um **dashboard Lovelace dedicado**.

---

## Funcionalidades

* **Backup automático versionado** de todos os Shellys conhecidos pelo Home Assistant (configuração completa, nomes, perfis, relés/estores, ações, scripts, schedules, webhooks e KVS).
* **Hardening automático**: desativa *factory reset from switch/input* (evita resets acidentais ao carregar 5× no interruptor) e garante que cada dispositivo tem nome configurado.
* **Deteção e Auto-Restore**: deteta dispositivos que voltaram em modo de fábrica e restaura automaticamente toda a configuração a partir do último backup (incluindo IP estático e autenticação).
* **Deteção de AP de reset via vizinhos**: se um Shelly ficar offline, pede aos Shellys Gen2+ vizinhos para fazerem `WiFi.Scan` e avisa qual o SSID de recuperação (`Shelly...`) e perto de que dispositivo está.
* **Suporte completo a Range Extender (Gen2+/Pro)**:
  * Respeita `host:port` (porta NAT `mport`) em todas as operações;
  * Consulta `WiFi.ListAPClients` nos Shellys com Range Extender ativo antes de disparar falsos alertas de reset;
  * Atualiza automaticamente o `host` e `port` da integração Shelly no Home Assistant se um dispositivo passar a estar atrás de um Range Extender.
* **Dashboard Lovelace personalizado (`shelly-guard-card`)**:
  * Atalhos no header para **Reload Pyscript**, **Backup All** e **Check Completo**;
  * KPIs e filtros rápidos (`Todos`, `Offline`, `Com Upgrade`, `Range Extender`, `Sem Backup`) + pesquisa em tempo real;
  * Tabela com estado online/offline, link direto `http://host:port`, estado e data de backup, tipo de configuração (`Gen · Wi-Fi/Ethernet/Range Extender · Estático/DHCP`), proteção *hardened* e firmware atual;
  * **Botão Upgrade** por dispositivo (fica ativo apenas quando existe firmware novo disponível e instala via `update.install`);
  * **Botão Check** por dispositivo (`pyscript.shelly_guard_check_device`).
* **Extras opcionais**: sincronização de nomes/áreas com **NetAlertX**, auditoria de scripts/webhooks duplicados e gestão de reservas DHCP em routers **ASUS** (via integração `AsusRouter`).

---

## Pré-requisitos

1. **Home Assistant** com a integração oficial **Shelly** configurada.
2. **Pyscript Python scripting** instalado via **HACS** (HACS → Integrações → *Pyscript Python scripting*).

---

## Instalação no Home Assistant

### 1. Copiar os ficheiros para `/config/`

Copia os 3 ficheiros deste repositório para a pasta de configuração do teu Home Assistant:

| Ficheiro no repositório | Destino no Home Assistant |
| --- | --- |
| `pyscript/apps/shelly_guard/__init__.py` | `/config/pyscript/apps/shelly_guard/__init__.py` |
| `www/shelly-guard-card.js` | `/config/www/shelly-guard-card.js` |
| `lovelace/shelly_guard.yaml` | `/config/lovelace/shelly_guard.yaml` |

### 2. Configurar o `configuration.yaml`

Adiciona o bloco de exemplo disponível em `examples/configuration.example.yaml` ao teu `/config/configuration.yaml`:

```yaml
pyscript:
  allow_all_imports: true
  hass_is_global: true
  apps:
    shelly_guard:
      backup_dir: /share/shelly_guard
      state_file: /config/www/shelly_guard_state.json
      keep_versions: 15
      auto_restore: true
      harden: true
      notify_service: notify.mobile_app_your_phone   # opcional

lovelace:
  mode: storage
  dashboards:
    shelly-guard:
      mode: yaml
      title: Shelly Guard
      icon: mdi:shield-sync
      show_in_sidebar: true
      filename: lovelace/shelly_guard.yaml
```

> Se já tiveres um bloco `pyscript:` ou `lovelace:` no `configuration.yaml`, basta juntar as chaves respetivas dentro dos blocos existentes.

### 3. Registar o card Lovelace

No Home Assistant, vai a **Definições → Painéis → ⋮ (canto superior direito) → Recursos → Adicionar recurso**:

* **URL:** `/local/shelly-guard-card.js?v=1`
* **Tipo:** `Módulo JavaScript`

### 4. Reiniciar o Home Assistant

Após reiniciar:
1. O painel **Shelly Guard** aparece automaticamente na barra lateral.
2. Clica em **Check Completo** no header para fazer o primeiro backup, *hardening* e preencher a tabela de dispositivos.

---

## Serviços disponíveis

| Serviço | Descrição |
| --- | --- |
| `pyscript.shelly_guard_check` | Verifica todos os Shellys, aplica *hardening*, deteta Range Extender / resets e atualiza backups. |
| `pyscript.shelly_guard_check_device` | Executa o check e backup de um único dispositivo (`mac: "AABBCCDDEEFF"`). |
| `pyscript.shelly_guard_backup_all` | Faz backup imediato de todos os dispositivos Shelly. |
| `pyscript.shelly_guard_restore` | Restaura um dispositivo a partir do backup (`mac`, `host` opcional, `dry_run: true\|false`, `backup_mac` para clonar num equipamento de substituição). |
| `pyscript.shelly_guard_scan` | Pede aos Shellys Gen2+ online um `WiFi.Scan` à procura de APs de reset. |
| `pyscript.shelly_guard_audit` | Lista (e com `fix: true` remove) scripts e webhooks duplicados em Gen2+. |
| `pyscript.shelly_guard_router_dhcp` | Compara/adiciona reservas DHCP num router ASUS (ignora clientes em Range Extender). |
| `pyscript.shelly_guard_sync_netalertx` | Envia nomes e áreas do HA para o NetAlertX (se configurado). |

---

## Notas sobre Range Extender

* Nos Shelly Gen2/Pro, o **Range Extender** usa NAT (`192.168.33.0/24`) e expõe cada cliente numa porta dedicada do Shelly host (`http://<IP_HOST>:<mport>`).
* Para manter a porta `mport` estável após reinícios, recomenda-se definir um **IP estático** na sub-rede `192.168.33.x` no Shelly cliente e desativar o seu AP próprio.
* Se um Shelly mudar de ligação direta para Range Extender (ou mudar de `mport`), o `shelly_guard` deteta-o automaticamente via `WiFi.ListAPClients` e atualiza a entrada do Home Assistant.

---

## Licença

MIT — ver [LICENSE](LICENSE).
