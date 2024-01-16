import sys
import urllib.parse
import argparse

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-ip', nargs='?', default='')
    parser.add_argument ('-p','--port',  nargs='?', default='')
    #parser.add_argument ('-pass','--password', default='')
    parser.add_argument('-pass', '--password', nargs='+', default='')
    #parser.add_argument ('-c','--command', default='')
    parser.add_argument('-c', '--command', nargs='+', default='')
    parser.add_argument ('-t','--timeout', default=4)
    parser.add_argument ('-r','--num_retries', default=3)
    parser.add_argument ('-st','--stay', default='n')
    return parser

def phelp():
    print("[-h [HELP]] [-ip [IP]] [-p [PORT]] [-pass PASSWORD] [-c COMMAND] [-t TIMEOUT] [-r NUM_RETRIES] [-st [y/n] Stay in menu after send] \n commands \n [phelp]	- this help\n [pnew]		- new address")

def input_address():
  host = input('IP Addres>>')
  port = input('Port>>')
  rcon_password = input('rcon_password>>')
  return host,port,rcon_password

def send_rcon_command(host, port, rcon_password, command, raise_errors=False, num_retries=3, timeout=4):
    from valve.rcon import RCON, RCONMessageError, RCONAuthenticationError, RCONCommunicationError, RCONMessage, RCONTimeoutError
    import socket
 
    try:
        port = int(port)
    except ValueError:
        #print("Port Error")
        return "Port connection Error"
 
    attempts = 0
    while attempts < num_retries:
        attempts += 1
        try:
            with RCON((host, port), rcon_password, timeout=timeout) as rcon:
                RCONMessage.ENCODING = "utf-8"
                response = rcon(command)
                return strip_rcon_log(response)
        except KeyError:
            # There seems to be a bug in python-vavle where a wrong password
            # trigger a KeyError at line 203 of valve/source/rcon.py,
            # so this is a work around for that.
            raise RconError('Incorrect rcon password')
 
        except (socket.error, socket.timeout,
                RCONMessageError, RCONAuthenticationError) as e:
            if attempts >= num_retries:
                if raise_errors:
                    raise RconError(str(e))
                else:
                    response = "connection error"
                    return strip_rcon_log(response)
        print("repeat send")

def strip_rcon_log(response):
     print(response)
#    f = open("LogRcon_response.txt", "a+")
#    f.write(response + '\n')
#    f.close()
#print("Connection to\n" + host + ":" +port, rcon_password)

if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])
    host = namespace.ip
    port = namespace.port
    rcon_password = ' '.join(namespace.password)
    command = ' '.join(namespace.command)
    num_retries = int(namespace.num_retries)
    timeout = float(namespace.timeout)
    stay = namespace.stay

    phelp()

    while True:
        if command and host and port:
            send_rcon_command(host, port, rcon_password, command, num_retries=num_retries, timeout=timeout)
            if stay == "n":
                break
        while True:
            command = input(">> ")
            if command == "pnew":
                host, port, rcon_password = input_address()
            elif command == "phelp":
                phelp()
            else:
                resp = send_rcon_command(host, port, rcon_password, command, num_retries=num_retries, timeout=timeout)
                if resp == "Port connection Error":
                    print("connection error")
                    host, port, rcon_password = input_address()

