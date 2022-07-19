import os
import glob
import time
import bluetooth
import csv

#sudo hciconfig hci0 piscan
#you have to run from terminal

base_dir = '/sys/bus/w1/devices/'
device_file = "/home/pi/Senior_Design/data_file" # path to where files are stored

def list_to_string(list):
    return_str = '\n'.join(list)
    return return_str

def read_file(fileName):
    lines_read = []
    with open(fileName, 'rt', encoding='utf-8-sig') as csvfile: # encoding necessary to prevent corruption of first line
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|', skipinitialspace=True)
        for row in spamreader:
            line_to_send = ', '.join(row)
            lines_read.append(line_to_send)

    return lines_read

def write_file(fileName):
    with open(fileName, 'w', newline='', encoding='utf-8-sig') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar="|", quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Latest update already received']) # ?


def request_cases(request_type):
	# stats data
	# stats = "1,raquelB,brittany,10/22/2021,20,15,raquelB,4\n1,jp,brittany,11/3/2021,34,18,jp,2"
	# leaderboard data
	ldb = "raquelB,brittany,qori,emerie,ian,brent,jp"

			# check if data was already received
	if request_type == "get stats updates":
		stats_list = read_file("stats.csv") # file where the stats are stored
		if (stats_list[0] == ['Latest update already received']):
			stats_request = "UPDATE ALREADY RECEIVED"
			print("Statistics update already received")
			return stats_request

		else:
			stats_request = list_to_string(stats_list)
			print("Statistics data requested")
			return stats_request

		
		

	elif request_type == "get LDB updates":
		print("Leaderboard data requested")
		return ldb

	elif request_type == "no action needed":
		print("No update sent")
		return "N/A" # dont send a message to app 

	elif request_type == "stats inserted": # it's safe to overwrite file
		write_file("stats.csv") # change file name to stats
		print("Statistics inserted into database; no update sent")
		return "N/A" 

	elif request_type == "stats NOT inserted": # DONT overwrite file
		print("Statistics NOT inserted into database; no update sent")
		return "N/A" 

	elif request_type == "LDB inserted":
		print(request_type)
		print("Leaderboard updated in the database; no update sent")
		#write_file("dummy1.csv") # change file name to LDB
		return "N/A"

	elif request_type == "LDB NOT inserted":
		#write_file("dummy1.csv") # change file name to LDB
		print("Leaderboard NOT updated in the database; no update sent")
		return "N/A"

	else:
		return "Unknown request type"



host = ""
port = 1


server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
print('Bluetooth Socket Created')
server_sock.bind(("",bluetooth.PORT_ANY))
print("Bluetooth Binding Completed")
server_sock.listen(1)

port = server_sock.getsockname()[1]

#uuid = "ae14f5e2-9eb6-4015-8457-824d76384ba0"
uuid = '256bfb09-7e59-4453-99cf-f281e0fd0f5c'

deviceName = "raspberrypi"
bluetooth.advertise_service(server_sock, deviceName,service_id = uuid, service_classes = [ uuid, bluetooth.SERIAL_PORT_CLASS ], profiles = [ bluetooth.SERIAL_PORT_PROFILE ] )
while True:
	print("Waiting for connection on RFCOMM channel %d" % port)

	client_sock, client_info = server_sock.accept()
	print("Accepted connection from", client_info)

	try:
		data_request = client_sock.recv(1024).decode('UTF-8') # why do you need to decode?
		print("\nReceived request:") # request could either be for stats data or leaderboard updates
		#print(data_request)

		# ONLY RETURN DATA IF REQUESTED, not after insertion status "N/A"
		return_data = request_cases(data_request)
		if(return_data != "N/A"):
			return_data = return_data + "#"
			client_sock.send(return_data)
			print("\nSending data:")
			print(return_data)
		else:
			print("\nNo data sent")
			client_sock.send("stop#")
		

	except IOError:
		pass

	except KeyboardInterrupt:
		
		print("Disconnected")
		
		client_sock.close()
		server_sock.close()
		print("All done")

		break
