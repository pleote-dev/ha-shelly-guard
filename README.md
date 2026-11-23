<p align="center">
  <img src="images/icon.png" alt="Shelly Guard" width="128" />
</p>

# Shelly Guard — Integração Nativa Home Assistant (HACS)

**Shelly Guard** é uma integração nativa para o **Home Assistant** (instalável via **HACS**, **sem Pyscript** nem edição de `configuration.yaml`) que protege todos os teus dispositivos **Shelly (Gen1, Gen2, Gen3 e Gen4)** contra perdas de configuração e *factory resets* acidentais, com **backup automático versionado**, **restauro automático**, **suporte nativo a Range Extender** e **dashboard automático na barra lateral**.

---

![Shelly Guard Dashboard](https://github.com/user-attachments/assets/ed0b7c7c-1d2a-4013-9b24-c20e671d26d8)

---

## Funcionalidades

* **Instalação HACS sem dependências:** integração nativa (`custom_components/shelly_guard`) com configuração 100% pela interface gráfica (Config Flow & Options Flow) — não precisa de Pyscript.
* **Backup automático versionado** de todos os Shellys integrados no Home Assistant (configuração completa, nomes, perfis, relés/estores, ações, scripts, schedules, webhooks e KVS).
* **Hardening automático:** desativa *factory reset from switch/input* (evita resets acidentais ao carregar 5× no interruptor) e garante que cada dispositivo tem nome configurado.
* **Deteção e Auto-Restore:** deteta dispositivos que voltaram em modo de fábrica e restaura automaticamente a configuração a partir do último backup (incluindo IP estático e autenticação).
* **Deteção de AP de reset via vizinhos:** se um Shelly ficar offline, pede aos Shellys Gen2+ vizinhos um `WiFi.Scan` e notifica qual o SSID de recuperação (`Shelly...`) e perto de que dispositivo está.
* **Suporte completo a Range Extender (Gen2+/Pro):**
  * Respeita `host:port` (porta NAT `mport`) em todas as operações;
  * Consulta `WiFi.ListAPClients` nos Shellys com Range Extender ativo antes de disparar falsos alertas de reset;
  * Atualiza automaticamente o `host` e `port` da integração Shelly no Home Assistant quando um dispositivo está ligado atrás de um Range Extender.
* **Dashboard automático na barra lateral (`Shelly Guard`):**
  * Servido diretamente pela integração via API autenticada (`/api/shelly_guard/state`) — sem copiar ficheiros para `www/` nem adicionar recursos Lovelace;
  * Atalhos no header para **Reload**, **Backup All** e **Check Completo**;
  * KPIs e filtros rápidos (`Todos`, `Offline`, `Com Upgrade`, `Range Extender`, `Sem Backup`) + pesquisa em tempo real;
  * Tabela com estado online/offline, link direto `http://host:port`, estado e data de backup, tipo de configuração (`Gen · Wi-Fi/Ethernet/Range Extender · Estático/DHCP`), proteção *hardened* e firmware atual;
  * **Botão Upgrade** por dispositivo (fica ativo apenas quando existe firmware novo disponível e instala via `update.install`);
  * **Botão Check** por dispositivo (`shelly_guard.check_device`).
* **Lista de Avariados & Assistente de Substituição (v1.1.0):**
  * Marca manualmente qualquer dispositivo como **Avariado** (preservando o último backup e os dados de fatura/garantia mesmo que seja removido do HA);
  * Quando entra um **Shelly novo** na rede (detetado em tempo real), o dashboard abre uma janela para escolher se é um **dispositivo novo** ou se vem **substituir um dispositivo avariado/offline**, restaurando automaticamente todo o backup no equipamento novo e arquivando o antigo como *Substituído*.
* **Registo de Compra & Garantia (v1.1.0):**
  * Guarda por dispositivo: **data de compra**, **duração da garantia** (36 meses por defeito), **vendedor/loja**, **nº de fatura** e notas (em `/share/shelly_guard/metadata.json`);
  * Mostra na tabela a validade da garantia (*Em garantia*, *Expira em breve*, *Expirada*) e destaca loja + nº de fatura nos dispositivos avariados para pedir RMA rapidamente.
* **Extras opcionais:** sincronização de nomes/áreas com **NetAlertX**, auditoria de scripts/webhooks duplicados e gestão de reservas DHCP em routers **ASUS** (via integração `AsusRouter`).

---

## Instalação via HACS (Recomendado)

Clica no botão abaixo para abrir o repositório diretamente no HACS da tua instância Home Assistant:

[![Abrir repositório no HACS do teu Home Assistant](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=pleote-dev&repository=ha-shelly-guard&category=integration)

Ou manualmente:

1. No Home Assistant, abre o **HACS** → menu **⋮** (canto superior direito) → **Repositórios personalizados**.
2. Adiciona o URL:
   ```text
   https://github.com/pleote-dev/ha-shelly-guard
   ```
   com categoria **Integração** → **Adicionar**.
3. Procura **Shelly Guard** no HACS → **Transferir** → **Reiniciar o Home Assistant**.
4. Vai a **Definições → Dispositivos e Serviços → Adicionar integração** → procura **Shelly Guard**.
5. Escolhe as opções (pasta de backups, `auto_restore`, `harden`, serviço de notificação opcional) e clica em **Submeter**.

Pronto! O painel **Shelly Guard** aparece automaticamente na barra lateral e a entidade `sensor.shelly_guard` fica ativa.

### Instalação manual (sem HACS)
Copia a pasta `custom_components/shelly_guard` para `/config/custom_components/shelly_guard`, reinicia o Home Assistant e adiciona a integração em **Definições → Dispositivos e Serviços**.

---

## Serviços disponíveis

| Serviço | Descrição |
| --- | --- |
| `shelly_guard.check` | Verifica todos os Shellys, aplica *hardening*, resolve Range Extender / resets e atualiza backups. |
| `shelly_guard.check_device` | Executa o check e backup de um único dispositivo (`mac: "AABBCCDDEEFF"`). |
| `shelly_guard.backup_all` | Faz backup imediato de todos os dispositivos Shelly. |
| `shelly_guard.restore` | Restaura um dispositivo a partir do backup (`mac`, `host` opcional, `dry_run: true\|false`, `backup_mac` para clonar em equipamento de substituição). |
| `shelly_guard.scan` | Pede aos Shellys Gen2+ online um `WiFi.Scan` à procura de APs de reset. |
| `shelly_guard.audit` | Lista (e com `fix: true` remove) scripts e webhooks duplicados em Gen2+. |
| `shelly_guard.router_dhcp` | Compara/adiciona reservas DHCP num router ASUS (ignora clientes em Range Extender). |
| `shelly_guard.sync_netalertx` | Envia nomes e áreas do HA para o NetAlertX (se configurado nas opções). |
| `shelly_guard.reload` | Recarrega a integração Shelly Guard. |
| `shelly_guard.set_metadata` | Guarda data de compra, garantia, vendedor, nº de fatura e notas de um dispositivo. |
| `shelly_guard.set_lifecycle` | Marca um dispositivo como `active`, `faulty` (avariado) ou `replaced` (substituído). |
| `shelly_guard.confirm_new_device` | Confirma um Shelly recém-detetado como dispositivo novo. |
| `shelly_guard.replace_device` | Restaura o backup de `old_mac` para `new_mac` e arquiva o dispositivo antigo como substituído. |

---

## Notas sobre Range Extender

* Nos Shelly Gen2/Pro, o **Range Extender** usa NAT (`192.168.33.0/24`) e expõe cada cliente numa porta dedicada do Shelly host (`http://<IP_HOST>:<mport>`).
* Para manter a porta `mport` estável após reinícios, recomenda-se definir um **IP estático** na sub-rede `192.168.33.x` no Shelly cliente e desativar o seu AP próprio.
* Se um Shelly mudar de ligação direta para Range Extender (ou mudar de `mport`), o `shelly_guard` deteta-o automaticamente via `WiFi.ListAPClients` e atualiza a entrada do Home Assistant.

---

## Licença

MIT — ver [LICENSE](LICENSE).
