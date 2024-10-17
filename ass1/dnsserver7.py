import socket
from dnslib import DNSRecord, DNSHeader, RR, A, QTYPE
import argparse

# !!!!!!!!!!!!!!!!!
# I provide command line parameter to run my file, you should run my file in this way:
# python dnsserver.py --flag 1
# or
# python dnsserver.py --flag 0


parser = argparse.ArgumentParser(description="Run a simple DNS server.")
parser.add_argument("--flag", type=int, choices=[0, 1, 2], default=1, help="Set the mode: 0 for public DNS, 1 for iterative searching, 2 for static response.")
args = parser.parse_args()

# DNS cache to store queried IP addresses
dns_cache = {}

# Function to handle incoming DNS queries
def handle_dns_query(data, client_address, sock, flag):
    # Parse the incoming query
    print(f"Received query from client: {client_address}")
    try:
        query = DNSRecord.parse(data)
    except Exception as e:
        print(f"Failed to parse DNS query: {e}")
        return
    qname = str(query.q.qname)
    qtype = QTYPE[query.q.qtype]
    print(f"Query name: {qname}, Query type: {qtype}")

    # Check if the query is in the cache
    if (qname, qtype) in dns_cache:
        print(f"Cache hit for {qname} ({qtype})")
        response = dns_cache[(qname, qtype)]
    else:
        print(f"Cache miss for {qname} ({qtype})")
        response = query.reply()

        if flag == 0:
            # Forward the query to a public DNS server
            print("Forwarding query to public DNS server")
            response = forward_query_to_public_dns(data, qname)
        elif flag == 1:
            # Perform iterative search to resolve the query
            print("Performing iterative search")
            response = iterative_query_resolution(query, qname, qtype)
        else:
            # Respond with a static IP for testing purposes (192.168.1.1)
            print("Responding with static IP address (192.168.1.1)")
            response.add_answer(RR(qname, QTYPE.A, rdata=A("192.168.1.1"), ttl=60))
        
        dns_cache[(qname, qtype)] = response  # Cache the response
        print(f"Cached response for {qname} ({qtype})")

    # Send the response to the client
    print(f"Sending response to client: {client_address}")
    sock.sendto(response.pack(), client_address)
  

# Function to forward query to a public DNS server
def forward_query_to_public_dns(data, qname):
    # Use Google Public DNS server (8.8.8.8)
    public_dns_server = ("8.8.8.8", 53)
    
    # Create a UDP socket to communicate with public DNS server
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as public_sock:
        public_sock.sendto(data, public_dns_server)
        public_sock.settimeout(3)
        try:
            print(f"Sending query to public DNS server: {public_dns_server}")
            response_data, _ = public_sock.recvfrom(512)
            response = DNSRecord.parse(response_data)
            print(f"Received response from public DNS server for {qname}")
        except socket.timeout:
            # If the query times out, return a SERVFAIL response
            print(f"Query to public DNS server for {qname} timed out.")
            response = DNSRecord(DNSHeader(qr=1, aa=1, ra=1, rcode=2), q=DNSRecord.question(qname))
        except Exception as e:
            print(f"Error communicating with public DNS server: {e}")
            response = DNSRecord(DNSHeader(qr=1, aa=1, ra=1, rcode=2), q=DNSRecord.question(qname))
    return response

# Function to perform iterative query resolution
def iterative_query_resolution(query, qname, qtype):
    current_server = ("198.41.0.4", 53)  # Root DNS server
    
    # Loop to perform iterative resolution
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as iter_sock:
            print(f"Sending query to server: {current_server}")
            iter_sock.sendto(query.pack(), current_server)
            iter_sock.settimeout(3)
            try:
                response_data, _ = iter_sock.recvfrom(2048)
                response = DNSRecord.parse(response_data)
                print(f"Received response from server: {current_server}")

                # Check if the response contains an answer
                if response.rr:
                    print(f"Received answer from {current_server[0]}")
                    return response

                # If no answer, get the next server from the authority section
                elif response.auth:
                    next_server_name = str(response.auth[0].rdata)
                    try:
                        next_server_ip = socket.gethostbyname(next_server_name)
                        current_server = (next_server_ip, 53)
                    except socket.gaierror:
                        print(f"Failed to resolve NS server {next_server_name}")
                        return DNSRecord(DNSHeader(qr=1, aa=1, ra=1, rcode=2), q=query.q)
                
                else:
                    # No more information available
                    print(f"No further information available for {qname}")
                    return DNSRecord(DNSHeader(qr=1, aa=1, ra=1, rcode=3), q=query.q)
            except socket.timeout:
                print(f"Query to server {current_server[0]} timed out.")
                return DNSRecord(DNSHeader(qr=1, aa=1, ra=1, rcode=2), q=query.q)
            


# Main function to create the local DNS server
def run_dns_server():
    # Create UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("127.0.0.1", 1234))
    print("DNS server is running on 127.0.0.1:1234")

    # Loop to listen and respond to DNS queries
    while True:
        print("Waiting for incoming DNS query...")
        try:
            data, client_address = server_socket.recvfrom(512)
            print(f"Received data from client: {client_address}")
            flag = args.flag
            handle_dns_query(data, client_address, server_socket, flag)
        except Exception as e:
            print(f"Error handling incoming DNS query: {e}")
            break

if __name__ == "__main__":
    run_dns_server()