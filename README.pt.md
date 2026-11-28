<p align="center">
  <img src="images/icon.png" alt="Shelly Guard" width="128" />
</p>

<p align="center">
  <a href="README.md">🇬🇧 English</a> · <strong>🇵🇹 Português</strong>
</p>

# Shelly Guard — Integração Personalizada para Home Assistant (HACS)

**Shelly Guard** é uma integração personalizada para o **Home Assistant** (instalável via **HACS** e configurada 100% pela interface gráfica) que protege todos os teus dispositivos **Shelly (Gen1, Gen2, Gen3 e Gen4)** contra perdas de configuração e avarias, com **backup automático versionado**, **restauro automático**, **suporte a Range Extender**, **registo de garantia** e **dashboard dedicado na barra lateral**.

---

![Shelly Guard Dashboard](https://github.com/user-attachments/assets/ed0b7c7c-1d2a-4013-9b24-c20e671d26d8)

---

> **Aviso de independência:** O Shelly Guard é um projeto comunitário totalmente independente. **Não** tem qualquer afiliação, patrocínio ou ligação oficial à marca **Shelly** / **Shelly Group** (Allterco Robotics) nem ao **Home Assistant**.

---

## Funcionalidades

* **Configuração 100% pela UI (HACS):** instalação via HACS e configuração direta em *Definições → Dispositivos e Serviços* (Config Flow e Opções traduzidos em Português e Inglês).
* **Backup automático versionado:** guarda a configuração completa de todos os Shellys integrados no Home Assistant (nomes, perfis, relés/estores, ações, scripts, schedules, webhooks e KVS), criando uma nova versão apenas quando existe alteração.
* **Hardening automático:** desativa o *factory reset* por interruptor/input (evita resets acidentais ao carregar 5× no interruptor) e garante que cada dispositivo tem nome definido.
* **Deteção de Reset & Auto-Restore:** deteta dispositivos que voltaram em modo de fábrica e restaura automaticamente a configuração a partir do último backup (incluindo IP estático e autenticação).
* **Deteção de AP de reset via vizinhos:** se um Shelly ficar offline, pede aos Shellys Gen2+ vizinhos um `WiFi.Scan` e notifica qual o SSID de recuperação (`Shelly...`) e perto de que dispositivo está.
* **Suporte completo a Range Extender (Gen2+/Pro):**
  * Respeita `host:port` (porta NAT `mport`) em todas as operações;
  * Consulta `WiFi.ListAPClients` nos Shellys com Range Extender ativo antes de disparar falsos alertas de reset;
  * Atualiza automaticamente o `host` e `port` da integração Shelly no Home Assistant quando um dispositivo está ligado atrás de um Range Extender.
* **Lista de Avariados & Assistente de Novos Shellys:**
  * Marca manualmente qualquer dispositivo como **Avariado** (preservando o último backup e os dados de fatura/garantia mesmo que seja removido do HA);
  * Sempre que entra **qualquer Shelly novo** no Home Assistant, abre um assistente que permite preencher logo **data de compra, garantia, loja, fatura e notas** e escolher se é um **dispositivo novo** (aplicando proteção e fazendo o primeiro backup) ou se vem **substituir um dispositivo da lista de Avariados/Offline** (restaurando automaticamente o backup no equipamento novo e arquivando o antigo como *Substituído*).
* **Menu Individual por Dispositivo (Backup Now, Restore por Versão, Check & Garantia):**
  * Mostra para cada Shelly a data/hora exata do último backup, o hash SHA-256 (`digest`), o número de versões históricas guardadas e o estado da proteção contra reset por interruptor;
  * Botões individuais para **Check**, **Backup Now** (com confirmação imediata se houve alterações de parâmetros gravadas num novo snapshot), **Restore** (escolha entre o último backup ou versões datadas anteriores, **Simular / Dry Run** e **Restaurar Agora** com IP opcional), **Upgrade de Firmware** e **Web UI**;
  * Guarda **data de compra**, **duração da garantia** (36 meses por defeito), **vendedor/loja**, **nº de fatura** e notas (em `/share/shelly_guard/metadata.json`), destacando loja + fatura nos dispositivos avariados para pedidos de RMA.
* **Dashboard dedicado na barra lateral (`Shelly Guard`):**
  * Servido diretamente pela integração via API autenticada (`/api/shelly_guard/state`), com tradução automática **Português / Inglês** consoante o idioma do utilizador no Home Assistant;
  * Atalhos no header para **Reload**, **Backup All** e **Check Completo**;
  * KPIs clicáveis, filtros rápidos, pesquisa em tempo real, links diretos `http://host:port`, firmware atual com botão **Upgrade** (ativo apenas quando há atualização disponível) e botão **Check** individual.
* **Integrações opcionais:** sincronização de nomes/áreas com **NetAlertX** (configurável nas Opções), auditoria de scripts/webhooks duplicados e gestão de reservas DHCP em routers **ASUS** (quando a integração `AsusRouter` está instalada).

---

## Instalação via HACS (Recomendado)

Clica no botão abaixo para abrir o repositório diretamente no HACS da tua instância Home Assistant:

[![Abrir repositório no HACS do teu Home Assistant](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=pleote-dev&repository=ha-shelly-guard&category=integration)

Ou manualmente:

1. No Home Assistant, abre o **HACS** → menu **⋮** (canto superior direito) → **Repositórios personalizados**.
2. Adiciona `https://github.com/pleote-dev/ha-shelly-guard` com categoria **Integração** → **Adicionar**.
3. Procura **Shelly Guard** no HACS → **Transferir** → **Reiniciar o Home Assistant**.
4. Vai a **Definições → Dispositivos e Serviços → Adicionar integração** → procura **Shelly Guard**.
5. Escolhe as opções (pasta de backups, intervalo de verificação, `auto_restore`, `harden`, serviço de notificação opcional) e clica em **Submeter**.

O painel **Shelly Guard** aparece automaticamente na barra lateral e a entidade `sensor.shelly_guard` fica ativa.

### Instalação manual (sem HACS)
Copia a pasta `custom_components/shelly_guard` para `/config/custom_components/shelly_guard`, reinicia o Home Assistant e adiciona a integração em **Definições → Dispositivos e Serviços**.

---

## Serviços disponíveis

| Serviço | Descrição |
| --- | --- |
| `shelly_guard.check` | Verifica todos os Shellys, aplica *hardening*, resolve Range Extender / resets e atualiza backups. |
| `shelly_guard.check_device` | Executa check, *hardening* e backup de um único dispositivo (`mac: "AABBCCDDEEFF"`), protegendo o backup se detetar modo de fábrica. |
| `shelly_guard.backup_all` | Faz backup imediato de todos os dispositivos Shelly. |
| `shelly_guard.backup_device` | Faz backup imediato de um único Shelly (`mac`, `force` opcional), criando nova versão datada sempre que mudam parâmetros. |
| `shelly_guard.restore` | Restaura um dispositivo a partir do backup (`mac`, `version` opcional, `host` opcional, `dry_run: true\|false`, `backup_mac` para clonar em substituição). |
| `shelly_guard.scan` | Pede aos Shellys Gen2+ online um `WiFi.Scan` à procura de APs de reset. |
| `shelly_guard.audit` | Lista (e com `fix: true` remove) scripts e webhooks duplicados em Gen2+. |
| `shelly_guard.router_dhcp` | Compara/adiciona reservas DHCP num router ASUS (ignora clientes em Range Extender). |
| `shelly_guard.sync_netalertx` | Envia nomes e áreas do HA para o NetAlertX (se configurado nas Opções). |
| `shelly_guard.set_metadata` | Guarda data de compra, garantia, vendedor, nº de fatura e notas de um dispositivo. |
| `shelly_guard.set_lifecycle` | Marca um dispositivo como `active`, `faulty` (avariado) ou `replaced` (substituído). |
| `shelly_guard.confirm_new_device` | Confirma um Shelly recém-detetado como dispositivo novo. |
| `shelly_guard.replace_device` | Restaura o backup de `old_mac` para `new_mac` e arquiva o dispositivo antigo como substituído. |
| `shelly_guard.reload` | Recarrega a integração Shelly Guard. |

---

## Notas sobre Range Extender

* Nos Shelly Gen2/Pro, o **Range Extender** usa NAT (`192.168.33.0/24`) e expõe cada cliente numa porta dedicada do Shelly host (`http://<IP_HOST>:<mport>`).
* Para manter a porta `mport` estável após reinícios, recomenda-se definir um **IP estático** na sub-rede `192.168.33.x` no Shelly cliente e desativar o seu AP próprio.
* Se um Shelly mudar de ligação direta para Range Extender (ou mudar de `mport`), o Shelly Guard deteta-o automaticamente via `WiFi.ListAPClients` e atualiza a entrada do Home Assistant.

---

## Licença

MIT — ver [LICENSE](LICENSE).
