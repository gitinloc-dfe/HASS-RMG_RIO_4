#!/usr/bin/env python3
"""
Script de test avancé pour RMG Rio 4
Test toutes les fonctionnalités : relais, DIO, requêtes d'état, etc.
"""

import asyncio
import sys

async def test_rmg_full(host, port, username, password):
    """Test complet du boîtier RMG Rio 4"""
    
    try:
        print(f"🔌 Connexion à {host}:{port}...")
        
        # Connexion TCP
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, int(port)),
            timeout=10.0
        )
        print("✅ Connexion TCP établie")
        
        # Authentification
        login_request = await asyncio.wait_for(reader.read(100), timeout=5.0)
        message = login_request.decode('utf-8').strip()
        print(f"📥 Reçu: {message}")
        
        if "LOGINREQUEST?" not in message:
            print(f"❌ Réponse inattendue: {message}")
            return False
        
        login_string = f"{username};{password}\r"
        writer.write(login_string.encode('utf-8'))
        await writer.drain()
        print(f"📤 Identifiants envoyés: {username};***")
        
        response = await asyncio.wait_for(reader.read(100), timeout=5.0)
        auth_message = response.decode('utf-8').strip()
        print(f"📥 Authentification: {auth_message}")
        
        if "AUTHENTICATION=Successful" not in auth_message:
            print(f"❌ Authentification échouée: {auth_message}")
            return False
        
        print("✅ Authentification réussie")
        
        # Fonction helper pour lire les réponses
        async def read_responses(duration=2):
            buffer = ""
            start_time = asyncio.get_event_loop().time()
            responses = []
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                try:
                    data = await asyncio.wait_for(reader.read(1024), timeout=0.5)
                    if data:
                        buffer += data.decode('utf-8')
                        while '\r' in buffer or '\n' in buffer:
                            if '\r' in buffer:
                                line, buffer = buffer.split('\r', 1)
                            else:
                                line, buffer = buffer.split('\n', 1)
                            
                            line = line.strip()
                            if line:
                                responses.append(line)
                                print(f"📨 Reçu: {line}")
                except asyncio.TimeoutError:
                    continue
            return responses
        
        # Écouter les états initiaux
        print("\n📡 États initiaux envoyés par le serveur...")
        await read_responses(3)
        
        # Test 1: Requêtes d'état
        print("\n🧪 Test des requêtes d'état...")
        
        for i in range(1, 5):
            print(f"\n📤 RELAY{i}?")
            writer.write(f"RELAY{i}?\r".encode())
            await writer.drain()
            await read_responses(1)
        
        for i in range(1, 5):
            print(f"\n📤 DIO{i}?")
            writer.write(f"DIO{i}?\r".encode())
            await writer.drain()
            await read_responses(1)
        
        # Test 2: Contrôle des relais
        print("\n🧪 Test du contrôle des relais...")
        
        # Test ON/OFF sur RELAY1
        print(f"\n📤 RELAY1 ON")
        writer.write(b"RELAY1 ON\r")
        await writer.drain()
        await read_responses(1)
        
        await asyncio.sleep(1)
        
        print(f"\n📤 RELAY1 OFF")
        writer.write(b"RELAY1 OFF\r")
        await writer.drain()
        await read_responses(1)
        
        # Test PULSE
        print(f"\n📤 RELAY2 PULSE 1.5")
        writer.write(b"RELAY2 PULSE 1.5\r")
        await writer.drain()
        print("⏱️ Écoute du PULSE (activation + désactivation)...")
        await read_responses(3)
        
        # Test 3: Informations système
        print("\n🧪 Test des informations système...")
        
        commands = [
            b"SERIALNUMBER?\r",
            b"FIRMWAREVERSION?\r", 
            b"HOSTNAME?\r"
        ]
        
        for cmd in commands:
            print(f"\n📤 {cmd.decode().strip()}")
            writer.write(cmd)
            await writer.drain()
            await read_responses(1)
        
        # Test 4: Test des DIO (attention: certains peuvent être en lecture seule)
        print("\n🧪 Test des DIO (certains peuvent être en lecture seule)...")
        
        for i in range(1, 5):
            print(f"\n📤 DIO{i} ON")
            writer.write(f"DIO{i} ON\r".encode())
            await writer.drain()
            responses = await read_responses(1)
            
            # Vérifier si on a une erreur de type DI
            for resp in responses:
                if "TYPE DI ERROR" in resp:
                    print(f"ℹ️ DIO{i} est une entrée digitale (lecture seule)")
                elif f"DIO{i}=ON" in resp:
                    print(f"✅ DIO{i} est une sortie digitale (contrôlable)")
                    # Remettre à OFF
                    await asyncio.sleep(0.5)
                    writer.write(f"DIO{i} OFF\r".encode())
                    await writer.drain()
                    await read_responses(1)
        
        # Test 5: Commande de fermeture propre
        print("\n🧪 Test de fermeture propre...")
        print(f"\n📤 GOODBYE!")
        writer.write(b"GOODBYE!\r")
        await writer.drain()
        await read_responses(1)
        
        print("\n✅ Test complet terminé avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    if len(sys.argv) != 5:
        print("Usage: python3 test_full.py <IP> <PORT> <USERNAME> <PASSWORD>")
        print("Exemple: python3 test_full.py 192.168.1.100 22023 admin Inloc+1300")
        sys.exit(1)
    
    host = sys.argv[1]
    port = sys.argv[2]
    username = sys.argv[3]
    password = sys.argv[4]
    
    print("🔧 Test complet RMG Rio 4")
    print("=" * 50)
    
    asyncio.run(test_rmg_full(host, port, username, password))

if __name__ == "__main__":
    main()