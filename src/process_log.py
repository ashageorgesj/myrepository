# your Python code to implement the features could be placed here
# note that you may use any language, there is no preference towards Python
import sys
import datetime
class BlockList:
	def __init__(self,ipName,noFailedAttempts,startTime,endTime):
		self.ipName = ipName;
		self.noFailedAttempts = noFailedAttempts;
		self.startTime = startTime;
		self.endTime = endTime
		self.BlockTimeRemaining = 0;
		
	def getipName(self):
		return self.ipName;
		
	def getnoAttempts(self):
		return self.noFailedAttempts;
		
	def getBlockTime(self):
		return self.BlockTimeRemaining;
		
	def setBlockTime(self):
	    self.BlockTimeRemaining = 5;
		
	def computeDiffTime(self):
		splitStart = self.startTime.split(':');
		splitEnd = self.endTime.split(':');
		return abs(int(splitStart[3]) - int(splitEnd[3]));
		
	def incrementAttempts(self):
		self.noFailedAttempts = self.noFailedAttempts + 1;
	
	def setStartTime(self,time):
		self.startTime = time;
		
	def setEndTime(self,time):
		self.endTime = time;
		
	def decrementBlockTime(self):
		self.blockTimeRemaining = self.blockTimeRemaining - 1;

def findActive(logName,ipFileName,hoursFileName,resourceFileName,blockFileName):
	file = open(logName,'r');
	blockFile = open(blockFileName,'w');
	activeIps = {};
	resourceList = {};
	timeList = {};
	problemList = [];
	#keys = None;
	currentTime = None;
	for line in file:
		params = line.split();
		ipList = params[0];
		# Ip checking
		currentKey = activeIps.get(ipList);
		if currentKey is None:
			activeIps[ipList] = 1;
		else:
			activeIps[ipList] = currentKey + 1;
		# Checking for most active hours.
		#timeStamp = params[3]+ ' ' + params[4];
		timeStamp = params[3];
		timeStamp = timeStamp.strip("[");
		
		#print timeList;
		if len(timeList.keys()) == 0:
			timeList[timeStamp] = 1;
		else:
			# Check if the time falls within an hour of the current keys.
			timeList = checknoVisits(timeList,timeStamp);
		
		#print timeStamp;
		# Checking for bandwidth.
		paramLength = len(params);
		bytes = params[paramLength - 1];
		
		# Make sure the bytes are made numeric.
		if (bytes == '-'):
			bytes = 0;
		else:
			bytes = int(bytes);	
		
		request = " ";
		interest = params[5:paramLength - 2];
		request = request.join(interest);
		currResource = params[6];
		# The name of the resource. It shouldn't be just a slash
		if len(currResource) > 1:
			bandWidth = resourceList.get(currResource);
			if bandWidth is None:
				resourceList[currResource] = bytes;
			else:
				resourceList[currResource] = bandWidth + bytes;
		# Checking for failed logins and preparing blocked list.
		status = params[paramLength - 2];
		
		if (status == '401'):
			if (len(problemList) == 0):
				problemList.append(BlockList(ipList,1,timeStamp,timeStamp));
			else: 
				for x in problemList:
					if (x.getipName() == ipList):
						x.incrementAttempts();
						x.setEndTime(timeStamp);
						if (x.getnoAttempts() == 3) & (x.computeDiffTime() <= 20):
							blockFile.write(line);
							x.setBlockTime();
		elif (status == '200'):
			#print any(x.getipName() == ipList for x in problemList);
			for x in problemList:
				if (x.getipName() == ipList):
					if (x.getBlockTime() > 0):
						x.decrementBlockTime();
					else:	
						problemList.remove(x);
		#print request;
		#keys = activeIps.keys();
	#print activeIps;
	file.close();
	blockFile.close();
	sortandwrite(activeIps,ipFileName,True);
	sortandwrite(resourceList,resourceFileName,False);
	sortandwrite(timeList,hoursFileName,True);
	#print timeList;
	
	

	
		
def checknoVisits(timeList,currentTime):
	#print currentTime;
	keyNames = timeList.keys();
	sortedkeyNames = sorted(keyNames);
	sortedkeyNames.append(currentTime);
	
	size = len(sortedkeyNames);
	entered = False;
	currIndex = sortedkeyNames.index(currentTime);
	sortedkeyNames.remove(currentTime);
	#print sortedkeyNames;
	for i in range(0,currIndex):
		if (entered):
			break;
		timeInterest = sortedkeyNames[i];
		interestValues = timeInterest.split(':');
		currentValues = currentTime.split(':');
		# If dates are the same.
		if (interestValues[0] == currentValues[0]):
			diffSec = (int(interestValues[1])- int(currentValues[1]))* 3600 + \
					(int(interestValues[2])- int(currentValues[2]))*60 + \
					(int(interestValues[3])- int(currentValues[3]));
			#print diffSec;
			# The difference should be within an hour
			if (abs(diffSec) < 3600):
			
				timeList[timeInterest] = timeList[timeInterest] + 1;
				# We need all the time till the last one.
				for j in range(1,(abs(diffSec) + 1)):
					# Add all seconds values between the existing and new timestamp.
					newSec = int(interestValues[3]) + j;
					# Add additional 0 for numbers less than 10.
					if (newSec >= 10):
						newTimeStamp = ':'.join([currentValues[0], currentValues[1],\
				                 currentValues[2], str(newSec)]);
					else:
						newTimeStamp = ':'.join([currentValues[0], currentValues[1],\
				                 currentValues[2], '0' + str(newSec)]);
					#print newTimeStamp;
					if (newTimeStamp in keyNames):
						timeList[newTimeStamp] = timeList[newTimeStamp] + 1;
					else:
						timeList[newTimeStamp] = 1;
				# Do it just once.
				entered = True;
		else:
		# To do for hour ranging two days. The calculation can be complicated.
			pass;
			#currentStamp = datetime.datetime(currentTime);
			#print currentStamp;
			#interestStamp = datetime.datetime(timeInterest);
			#print interestStamp;
	return timeList;	
	#keyNames = keyNames.add(currentTime);
		
def sortandwrite(dictItem,fileName,writeValues):
	fileHandle = open(fileName,'w');
	itemTuples = dictItem.items();
	
	# Make sure that string comparison don't take place. 
	# Convert to integer the item you want to be sorted on.
	sortedTuples = sorted(itemTuples,key = lambda item : int(item[1]), reverse = True);
	if writeValues:
		fileHandle.write('\n'.join(s[0] + "," + str(s[1]) for s in sortedTuples[0:10]));
	else:
		fileHandle.write('\n'.join(s[0] for s in sortedTuples[0:10]));
	fileHandle.close();
	

			
		

def main():
	#print len(sys.argv[1:]);
	#for i in range(0,len(sys.argv[1:]) + 1):
		# The input log
		#if (i == 1):
	findActive(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5]);

if __name__ == "__main__":
    main()
