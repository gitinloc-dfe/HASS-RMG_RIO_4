#!/usr/bin/env python3
"""
Script de test pour valider la connexion au boîtier RMG Rio 4
Usage: python3 test_connection.py <IP> <PORT> <USERNAME> <PASSWORD>
"""

import asyncio
import sys

async def test_rmg_connection(host, port, username, password):
    """Teste la connexion au boîtier RMG Rio 4"""
    
    try:
        print(f"Connexion à {host}:{port}...")
        
        # Connexion TCP
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, int(port)),
            timeout=10.0
        )
        print("✅ Connexion TCP établie")
        
        # Attendre le LOGINREQUEST du serveur
        login_request = await asyncio.wait_for(reader.read(100), timeout=5.0)
        message = login_request.decode('utf-8').strip()
        print(f"📥 Reçu du serveur: {message}")
        
        if "LOGINREQUEST?" not in message:
            print(f"❌ Réponse inattendue, attendu LOGINREQUEST?: {message}")
            return False
        
        # Envoi des identifiants
        login_string = f"{username};{password}\r"
        writer.write(login_string.encode('utf-8'))
        await writer.drain()
        print(f"📤 Identifiants envoyés: {username};***")
        
        # Attendre la réponse d'authentification
        response = await asyncio.wait_for(reader.read(100), timeout=5.0)
        auth_message = response.decode('utf-8').strip()
        print(f"📥 Authentification: {auth_message}")
        
        if "AUTHENTICATION=Successful" not in auth_message:
            print(f"❌ Authentification échouée: {auth_message}")
            return False
        
        print("✅ Authentification réussie")
        
        # Écouter les états initiaux (le serveur les envoie automatiquement)
        print("\n📡 Écoute des états initiaux...")
        start_time = asyncio.get_event_loop().time()
        buffer = ""
        
        while (asyncio.get_event_loop().time() - start_time) < 3:
            try:
                data = await asyncio.wait_for(reader.read(1024), timeout=1.0)
                if data:
                    buffer += data.decode('utf-8')
                    while '\r' in buffer or '\n' in buffer:
                        if '\r' in buffer:
                            line, buffer = buffer.split('\r', 1)
                        else:
                            line, buffer = buffer.split('\n', 1)
                        
                        line = line.strip()
                        if line:
                            print(f"📨 État initial: {line}")
                            
            except asyncio.TimeoutError:
                continue
        
        # Test requête d'état
        print("\n🧪 Test requête état RELAY1?...")
        writer.write(b"RELAY1?\r")
        await writer.drain()
        
        # Écouter la réponse
        try:
            data = await asyncio.wait_for(reader.read(1024), timeout=2.0)
            if data:
                response = data.decode('utf-8').strip()
                print(f"📨 Réponse: {response}")
        except asyncio.TimeoutError:
            print("⏱️ Pas de réponse")
        
        # Test d'une commande
        print("\n🧪 Test d'une commande RELAY1 ON...")
        writer.write(b"RELAY1 ON\r")
        await writer.drain()
        
        # Écoute des réponses pendant 5 secondes
        print("👂 Écoute des réponses...")
        start_time = asyncio.get_event_loop().time()
        buffer = ""
        
        while (asyncio.get_event_loop().time() - start_time) < 5:
            try:
                data = await asyncio.wait_for(reader.read(1024), timeout=1.0)
                if data:
                    buffer += data.decode('utf-8')
                    # Traiter les lignes complètes
                    while '\r' in buffer or '\n' in buffer:
                        if '\r' in buffer:
                            line, buffer = buffer.split('\r', 1)
                        else:
                            line, buffer = buffer.split('\n', 1)
                        
                        line = line.strip()
                        if line:
                            print(f"📨 Reçu: {line}")
                            
            except asyncio.TimeoutError:
                continue
        
        # Test commande OFF
        print("\n🧪 Test d'une commande RELAY1 OFF...")
        writer.write(b"RELAY1 OFF\r")
        await writer.drain()
        
        # Écoute encore 2 secondes
        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) < 2:
            try:
                data = await asyncio.wait_for(reader.read(1024), timeout=1.0)
                if data:
                    buffer += data.decode('utf-8')
                    while '\r' in buffer or '\n' in buffer:
                        if '\r' in buffer:
                            line, buffer = buffer.split('\r', 1)
                        else:
                            line, buffer = buffer.split('\n', 1)
                        
                        line = line.strip()
                        if line:
                            print(f"📨 Reçu: {line}")
                            
            except asyncio.TimeoutError:
                continue
        
        # Test commande PULSE
        print("\n🧪 Test d'une commande RELAY1 PULSE 1.0...")
        writer.write(b"RELAY1 PULSE 1.0\r")
        await writer.drain()
        
        # Écoute pendant 3 secondes pour voir le PULSE
        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) < 3:
            try:
                data = await asyncio.wait_for(reader.read(1024), timeout=1.0)
                if data:
                    buffer += data.decode('utf-8')
                    while '\r' in buffer or '\n' in buffer:
                        if '\r' in buffer:
                            line, buffer = buffer.split('\r', 1)
                        else:
                            line, buffer = buffer.split('\n', 1)
                        
                        line = line.strip()
                        if line:
                            print(f"📨 Reçu: {line}")
                            
            except asyncio.TimeoutError:
                continue
        
        # Fermeture
        writer.close()
        await writer.wait_closed()
        print("\n✅ Test terminé avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

def main():
    if len(sys.argv) != 5:
        print("Usage: python3 test_connection.py <IP> <PORT> <USERNAME> <PASSWORD>")
        print("Exemple: python3 test_connection.py 192.168.1.100 22023 admin Inloc+1300")
        sys.exit(1)
    
    host = sys.argv[1]
    port = sys.argv[2]
    username = sys.argv[3]
    password = sys.argv[4]
    
    print("🔧 Test de connexion RMG Rio 4")
    print("=" * 40)
    
    asyncio.run(test_rmg_connection(host, port, username, password))

if __name__ == "__main__":
    main()