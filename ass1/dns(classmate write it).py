import socket
import dnslib

PORT = 1234
IP = '127.0.0.1'
ROOT_IP = ['198.41.0.4',
        '192.228.79.201',
        '192.33.4.12',
        '128.8.10.90',
        '192.203.230.10',
        '192.5.5.241',
        '192.112.36.4',
        '128.63.2.53',
        '192.36.148.17',
        '192.58.128.30',
        '193.0.14.129',
        '198.32.64.12',
        '202.12.27.33',]

def iterative_searching(qname,final_response_record):
    domain_list = qname.split(".")
    domain_list.pop()
    print(domain_list)
    domain_list.reverse()
    domain = ""
    dest_list = ROOT_IP
    print("Passing by: ")
    current_server_level = 0
    for a in domain_list:
        domain = a + "." + domain
        query_record = dnslib.DNSRecord.question(domain)
        timeout = True
        dest_index = 0
        dest = dest_list[dest_index]
        while (timeout):
            try:
                response_data = query_record.send(dest,timeout = 2)
                print(dest)
                timeout = False
            # if timeout occurred when sending query to a server, switch to another available server at the same level
            except:
                print(dest + ": timeout error. Switching server...")
                if dest_index < len(dest_list):
                    dest_index = dest_index + 1
                    dest = dest_list[dest_index]
                else:
                    print("All servers at this level encountered timeout. Please shut down the server and retry.")
        response_record = dnslib.DNSRecord.parse(response_data)
        # print(response_record)
        dest_list = []
        if(response_record.rr == [] and response_record.auth != []):
            # if there is additional section, get the ip address of the next server 
            if response_record.ar != []:
                for AR in response_record.ar:
                    dest_list.append(AR.rdata.__str__())
            else:
                for AU in response_record.auth:
                    dest = AU.rdata.__str__()
                    print(dest)
                    query_record = dnslib.DNSRecord.question(dest)
                    response_data = query_record.send('223.5.5.5')
                    response_record = dnslib.DNSRecord.parse(response_data)
                    dest_list.append(response_record.rr[0].rdata.__str__())
        elif(response_record.rr != []):
            rdata = response_record.rr[0].rdata.__str__()
            # if the answer is a CNAME, the client will use the CNAME to do iterative searching agin
            if (response_record.rr[0].rtype == 5):
                print("Search using CNAME")
                final_response_record.add_answer(response_record.rr[0])
                # print(final_response_record)
                iterative_searching(rdata, final_response_record)
            else:
                for RR in response_record.rr:
                    final_response_record.add_answer(RR)
                # print(final_response_record)
        # print(dest)

def ask_local_dns_server(flag):

    local_cache = {}
    while 1:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        sock.bind((IP, PORT))
        # Parse DNS packet data to get a DNSRecord instance
        print("Waiting for next query...\n(or use keyboard interrupt to shut down the server)")
        query_data, client_address = sock.recvfrom(512)
        query_record = dnslib.DNSRecord.parse(query_data)
        print("Client is asking for IP address of", query_record.q.qname)
        query_record.header.set_rd(0)
        final_response_record = query_record.reply()
        
        if query_record.q.qname in local_cache:
            for RR in local_cache[query_record.q.qname]:
                final_response_record.add_answer(RR)
            print("Sending response from the local cache")
            
        else:
            if flag == 0:
                # Ask the public server
                response_data = query_record.send('223.5.5.5')
                final_response_record = dnslib.DNSRecord.parse(response_data)
                print("Sending response from public server")
            else:
                # Do iterative searching
                qname = str(query_record.q.qname)
                iterative_searching(qname, final_response_record)
            local_cache[query_record.q.qname] =final_response_record.rr
        # prepare final_reponse_record packet
        final_response_record.header.id = query_record.header.id 
        final_response_record.q.qtype = 1 # qtype = "A"
        sock.sendto(final_response_record.pack(), client_address)
        print("---------------------------------------------------")



if __name__ == '__main__':
    try:
        flag = int(input("Choose flag to be 0 or 1?"))
        ask_local_dns_server(flag)
    except KeyboardInterrupt:
        pass