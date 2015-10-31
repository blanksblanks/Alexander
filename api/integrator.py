import sys

# python integrator.py <url for courses> <IP for courses> <number of student partitions> 
# <list of student paritions followed by their IP>
# ex. python integrator.py courses coursesIP 2 students1 students1_IP students2 students2_IP 

courses = None
coursesIP = None
students = {}

def main(argv):
	if (len(argv) < 5):
		print "Too few command-line arguments."
		sys.exit(1)
	courses = argv[0]
	print courses
	coursesIP = argv[1]
	numberOfPartitions = int(argv[2])
	argNumber = 3
	for i in range(numberOfPartitions):
		students[argv[argNumber]] = argv[argNumber+1]
		argNumber += 2
	print students

#integrator 

if __name__ == '__main__':
	main(sys.argv[1:])
