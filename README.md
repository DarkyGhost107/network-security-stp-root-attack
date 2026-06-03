# STP Root Claim Attack - Laboratorio de Seguridad de Redes

**Ambiente:** GNS3 (Controlado) | **Herramienta:** Python 3 + Scapy | **Capa OSI:** Capa 2

## Aviso Legal

Uso **exclusivamente educativo** en laboratorio controlado (GNS3). El uso no autorizado es **ilegal**.

## 1. Objetivo del Laboratorio

Demostrar el ataque STP Root Claim: el atacante envia BPDUs (Bridge Protocol Data Units) con una prioridad de bridge inferior (numericamente) a la del Root Bridge legitimo. Esto provoca que los switches de la red elijan al atacante como nuevo Root Bridge, forzando una reconvergencia STP y potencialmente redirigiendo el trafico por el atacante (MitM).

## 2. Objetivo del Script

`stp_root_attack.py` envia continuamente BPDUs de configuracion STP con:
- **Prioridad = 0** (la mas baja posible, siempre gana la eleccion)
- **Root MAC = MAC del atacante**
- **Path Cost = 0** (camino aparentemente mas corto)

## 3. Parametros del Script

| Parametro | Flag | Tipo | Default | Descripcion |
|-----------|------|------|---------|-------------|
| Interfaz | `-i` | str | eth0 | Interfaz de red |
| Intervalo | `--interval` | float | 2.0 | Segundos entre BPDUs (= hello time STP) |
| Prioridad | `--priority` | int | 0 | Prioridad STP (0 = minima, gana) |
| VLAN | `--vlan` | int | 1 | VLAN objetivo |

### Ejemplo de uso

```bash
sudo python3 stp_root_attack.py
sudo python3 stp_root_attack.py -i eth1
sudo python3 stp_root_attack.py --priority 0 --interval 1.0
```

## 4. Requisitos

```bash
Python 3.8+
pip install scapy
root (sudo)
python3 -c "from scapy.all import STP; print('STP OK')"
```

## 5. Funcionamiento del Script

```
ANTES del ataque:
  SW-A (prioridad 4096)  = Root Bridge legitimo
  SW-B (prioridad 32768)
  SW-C (prioridad 32768)

DESPUES del ataque:
  ATACANTE (prioridad 0) = Root Bridge FALSO  <- gana
  SW-A (prioridad 4096)  = ya no es root
  Reconvergencia STP -> posible caida momentanea
```

Estructura del BPDU malicioso:
- dst: 01:80:c2:00:00:00 (STP Multicast)
- bpdutype: 0x00 (Configuration BPDU)
- bpduflags: 0x01 (Topology Change)
- rootid: 0 (PRIORIDAD MINIMA)
- pathcost: 0
- hellotime: 2, maxage: 20, fwddelay: 15

## 6. Topologia de Red (GNS3)

```
                    +─────────────────+
                    |   SW-A (ROOT)   | <- Root Bridge legitimo ANTES
                    | Prioridad 4096   |
                    +────────+────────+
                             |
              +──────────────+──────────────+
              |                             |
     +────────+────────+           +────────+────────+
     |      SW-B       |           |      SW-C       |
     | Prioridad 32768 |           | Prioridad 32768 |
     +────────+────────+           +-────────────────+
              |
     +────────+────────+
     |   ATACANTE       | <- Envia BPDUs con prioridad 0
     | Kali Linux        |    Se convierte en nuevo Root
     | Prioridad 0       |    Todo el trafico pasa aqui
     +-─────────────────+
```

### Direccionamiento

| Dispositivo | IP Mgmt | Prioridad STP | Rol |
|-------------|---------|---------------|-----|
| SW-A | 192.168.1.1/24 | 4096 | Root Bridge legitimo |
| SW-B | 192.168.1.2/24 | 32768 | Switch distribucion |
| SW-C | 192.168.1.3/24 | 32768 | Switch acceso |
| Atacante | 192.168.1.50/24 | **0** | Root Bridge falso |

## 7. Capturas de Pantalla

Coloca tus capturas en `screenshots/`:
- `screenshots/stp_before.png` - Topologia STP antes del ataque
- `screenshots/stp_attack_running.png` - Script enviando BPDUs
- `screenshots/stp_root_changed.png` - Nuevo Root Bridge (atacante)
- `screenshots/stp_convergence.png` - Reconvergencia en switches
- `screenshots/wireshark_bpdu.png` - Wireshark capturando BPDUs

```cisco
show spanning-tree
show spanning-tree summary
show spanning-tree detail | include topology
```

## 8. Contramedidas

| Contramedida | Comando Cisco IOS | Descripcion |
|---|---|---|
| BPDU Guard | `spanning-tree bpduguard enable` | Apaga el puerto si recibe un BPDU |
| Root Guard | `spanning-tree guard root` | Ignora BPDUs con menor prioridad |
| Root Bridge manual | `spanning-tree vlan 1 priority 0` | Fijar el root legitimo |
| PortFast | `spanning-tree portfast` | Solo en puertos de acceso |

```cisco
! Fijar Root Bridge legitimo
spanning-tree vlan 1 priority 0

! BPDU Guard en puertos de acceso
interface range GigabitEthernet0/1 - 24
 spanning-tree bpduguard enable
 spanning-tree portfast

! Root Guard en puertos de distribucion
interface GigabitEthernet0/25
 spanning-tree guard root

show spanning-tree inconsistentports
```

## 9. Referencias

- [MITRE ATT&CK T1557 - Adversary-in-the-Middle](https://attack.mitre.org/techniques/T1557/)
- [IEEE 802.1D - Spanning Tree Protocol](https://standards.ieee.org/ieee/802.1D/6847/)
- [Cisco STP Security Best Practices](https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/24062-146.html)

---
*Laboratorio de Seguridad de Redes | GNS3 | Uso educativo exclusivo*
