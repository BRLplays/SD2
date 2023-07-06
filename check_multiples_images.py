import os
import time
import subprocess


folder_path = 'C:/Users/luigi/Desktop/LPR_Pipeline'

# Function to rename multiple files
def main():
	log = open("GarageTestLog.txt", "a")
	path="C:/Users/luigi/Desktop/G2/"

	for filename in os.listdir(path):
		print("TESTING: " + filename)
		log.write("TESTING: " + filename + "             ")
		file_path = path + filename
		
		string_to_edit = 'python automatic_script.py image_path'
		command = string_to_edit.replace('image_path', file_path)
		results = subprocess.run(command, cwd=folder_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output = results.stdout.decode("utf-8") # For debugging purposes
		print(output)
		log.write(output)
	
	log.close()

		
# Driver Code
if __name__ == '__main__':
	# Calling main() function
	main()