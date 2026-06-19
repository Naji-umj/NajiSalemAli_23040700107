import hashlib
import os
from datetime import datetime
from scapy.all import *

NIM = "23040700107"
NAMA = "NajiSalemAli"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence")

def create_pcap_files():
    print("=" * 60)
    print("LANGKAH 1: AKUISISI DATA JARINGAN")
    print("=" * 60)
    packet_counts = [30, 50, 70, 90, 100]
    for i, count in enumerate(packet_counts, 1):
        filename = f"PCAP{i:02d}_{NIM}.pcap"
        filepath = os.path.join(EVIDENCE_DIR, filename)
        packets = []
        for j in range(count):
            pkt = IP(src=f"192.168.1.{j%254+1}", dst="10.0.0.1") / \
                  TCP(sport=1024+j, dport=80) / \
                  Raw(load=f"packet-{j}-evidence-{NIM}".encode())
            packets.append(pkt)
        wrpcap(filepath, packets)
        print(f"[+] Created: {filename} ({count} packets)")
    print()

def calculate_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        sha256.update(f.read())
    return sha256.hexdigest()

def get_packet_count(filepath):
    packets = rdpcap(filepath)
    return len(packets)

def hash_evidence_files():
    print("=" * 60)
    print("LANGKAH 2: PERHITUNGAN HASH SHA-256")
    print("=" * 60)
    evidence_data = []
    for i in range(1, 6):
        filename = f"PCAP{i:02d}_{NIM}.pcap"
        filepath = os.path.join(EVIDENCE_DIR, filename)
        file_size = os.path.getsize(filepath)
        packet_count = get_packet_count(filepath)
        sha256_hash = calculate_sha256(filepath)
        evidence_data.append({
            "filename": filename,
            "filepath": filepath,
            "packet_count": packet_count,
            "file_size": file_size,
            "sha256": sha256_hash
        })
        print(f"File      : {filename}")
        print(f"Packets   : {packet_count}")
        print(f"Size      : {file_size} bytes")
        print(f"SHA-256   : {sha256_hash}")
        print("-" * 60)
    print()
    return evidence_data

def calculate_block_hash(index, timestamp, evidence_file, packet_count, evidence_hash, previous_hash):
    data = f"{index}{timestamp}{evidence_file}{packet_count}{evidence_hash}{previous_hash}"
    return hashlib.sha256(data.encode()).hexdigest()

def create_blockchain(evidence_data):
    print("=" * 60)
    print("LANGKAH 3: SIMULASI BLOCKCHAIN")
    print("=" * 60)
    blockchain = []
    genesis = {
        "index": 0,
        "timestamp": str(datetime.now()),
        "evidence_file": "GENESIS",
        "packet_count": 0,
        "evidence_hash": "0" * 64,
        "previous_hash": "0" * 64,
        "block_hash": ""
    }
    genesis["block_hash"] = calculate_block_hash(
        genesis["index"], genesis["timestamp"],
        genesis["evidence_file"], genesis["packet_count"],
        genesis["evidence_hash"], genesis["previous_hash"]
    )
    blockchain.append(genesis)
    for i, evidence in enumerate(evidence_data, 1):
        block = {
            "index": i,
            "timestamp": str(datetime.now()),
            "evidence_file": evidence["filename"],
            "packet_count": evidence["packet_count"],
            "evidence_hash": evidence["sha256"],
            "previous_hash": blockchain[-1]["block_hash"],
            "block_hash": ""
        }
        block["block_hash"] = calculate_block_hash(
            block["index"], block["timestamp"],
            block["evidence_file"], block["packet_count"],
            block["evidence_hash"], block["previous_hash"]
        )
        blockchain.append(block)
    for block in blockchain:
        print(f"Index         : {block['index']}")
        print(f"Timestamp     : {block['timestamp']}")
        print(f"Evidence File : {block['evidence_file']}")
        print(f"Packet Count  : {block['packet_count']}")
        print(f"Evidence Hash : {block['evidence_hash'][:32]}...")
        print(f"Previous Hash : {block['previous_hash'][:32]}...")
        print(f"Block Hash    : {block['block_hash'][:32]}...")
        print("-" * 60)
    print()
    return blockchain

def validate_blockchain(blockchain):
    print("=" * 60)
    print("LANGKAH 4: VALIDASI BLOCKCHAIN")
    print("=" * 60)
    is_valid = True
    for i in range(1, len(blockchain)):
        current = blockchain[i]
        previous = blockchain[i-1]
        if current["previous_hash"] != previous["block_hash"]:
            print(f"[ERROR] Block {i}: Previous Hash TIDAK SESUAI!")
            is_valid = False
        recalculated = calculate_block_hash(
            current["index"], current["timestamp"],
            current["evidence_file"], current["packet_count"],
            current["evidence_hash"], current["previous_hash"]
        )
        if current["block_hash"] != recalculated:
            print(f"[ERROR] Block {i}: Block Hash TIDAK SESUAI!")
            is_valid = False
    if is_valid:
        print("Blockchain Validation : VALID")
    else:
        print("Blockchain Validation : INVALID")
    print()
    return is_valid

def bonus_tamper_test(original_blockchain):
    print("=" * 60)
    print("BONUS: SIMULASI TAMPERING (ONE BYTE MODIFICATION)")
    print("=" * 60)
    filepath = os.path.join(EVIDENCE_DIR, f"PCAP01_{NIM}.pcap")
    with open(filepath, 'rb') as f:
        data = bytearray(f.read())
    data[100] = (data[100] + 1) % 256
    with open(filepath, 'wb') as f:
        f.write(data)
    new_hash = calculate_sha256(filepath)
    print(f"[!] PCAP01_{NIM}.pcap telah dimodifikasi (1 byte changed)")
    print(f"[!] SHA-256 lama : {original_blockchain[1]['evidence_hash']}")
    print(f"[!] SHA-256 baru : {new_hash}")
    print()
    tampered_blockchain = [block.copy() for block in original_blockchain]
    tampered_blockchain[1]["evidence_hash"] = new_hash
    validate_blockchain(tampered_blockchain)

if __name__ == "__main__":
    create_pcap_files()
    evidence_data = hash_evidence_files()
    blockchain = create_blockchain(evidence_data)
    validate_blockchain(blockchain)
    bonus_tamper_test(blockchain)