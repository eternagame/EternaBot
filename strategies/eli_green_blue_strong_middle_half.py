#by Chengfu chengfuc@andrew.cmu.edu date:6.19
from eterna_utils import *
import re
import strategy_template

class Strategy(strategy_template.Strategy):
	def __init__(self):
		strategy_template.Strategy.__init__(self)
		
		self.title_ = "Green and blue nucleotides a strand + Strong middle half"
		self.author_ = "Eli Fisker"
		self.url_ = "http://getsatisfaction.com/eternagame/topics/_strategy_market_green_and_blue_nucleotides_a_strand_strong_middle_half"
		self.default_params_ = [-1]
		self.code_length_ = 190
		self.publishable_ = True

		
       	def isExist(self,array, elem):
                for ii in range(0,len(array)):
                        if(elem==array[ii]):
                                return ii
                return -1
        def isLoop(self,array, elem):
                for ii in range(0,len(array)):
                        for jj in range(0,len(array[ii])):
                                for kk in range(0, len(array[ii][jj])):
                                        if(elem==array[ii][jj][kk]):
                                                return True
                                        
                return False

        def isHalf(self, array, index):
                for ii in range(0,len(array)):
                        for jj in range(0,len(array[ii])):
                                if(array[ii][jj]==index):
                                        if(len(array[ii])>=11 and jj>=6):
                                                return True;
                return False;
        def getLength(self, array, index):
                for ii in range(0,len(array)):
                        for jj in range(0,len(array[ii])):
                                if(array[ii][jj]==index):
                                        return len(array[ii]);
                return -1;
        #return the index of neck pair and the neck pair
        def get_neck_index(self,loop_groups,sequence,pairmap):
	
		necks = []
		pair_indices = []
		
		
		for ii in range(0,len(loop_groups)):
			start_i = loop_groups[ii][0]
			end_i = loop_groups[ii][len(loop_groups[ii]) - 1]
			
			if(start_i - 1 >= 0):
				if(pairmap[start_i-1] <0):
					print "ERROR something's wrong with RNAELEMENT 1"
					sys.exit(0)

				if(pair_indices.count(start_i-1) == 0):
                                        if(self.isExist(necks,start_i-1)==-1):
                                                necks.append(start_i-1)
                                        if(self.isExist(necks,pairmap[start_i-1])==-1):
                                                necks.append(pairmap[start_i-1])
			if(end_i + 1 < len(sequence)):
				if(pairmap[end_i+1] <0):
					print "ERROR something's wrong with RNAELEMENT 2"
					sys.exit(0)
				
				if(pair_indices.count(end_i+1) == 0):
                                        if(self.isExist(necks,end_i+1)==-1):
                                                necks.append(end_i+1)
                                        if(self.isExist(necks,end_i+1)==-1):
                                                necks.append(pairmap[end_i+1])
		return necks	

        
        def score(self, design, params):			
		
		elements = design['secstruct_elements']
		sequence = design['sequence']
		pairmap = design['pairmap']
		neckArea = []
		loops=[]
		score = 100
		#================================================================================================Get necks========================
		for ii in range(0,len(elements)):                                                                                               #=
			elem = elements[ii]
			if(elem.type_ == RNAELEMENT_LOOP):
                                loop_groups = elem.get_loop_groups()
                                loops.append(loop_groups)
                                tmp=[]
                                tmp = self.get_neck_index(loop_groups,sequence,pairmap)
                                for jj in range(0, len(tmp)):
                                        neckArea.append(tmp[jj])

                #print(neckArea)#=
                #=================================================================================================================================

                indice=[]
                lengthArray=[]
                length=[]
                for ii in range(0,len(sequence)):
                        if(self.isLoop(loops,ii)==False):
                                length.append(ii);   
                                if(sequence[ii]=='U' or sequence[ii]=='C'):
                                        indice.append(ii);
                        else:
                                if(len(length)!=0):
                                        lengthArray.append(length);
                                        length=[];

                if(len(length)!=0):
                        lengthArray.append(length);
                        length=[];
                '''
                for ii in range(0,len(lengthArray)):
                        print(len(lengthArray[ii]));
                        print('========')
                        for jj in range(0, len(lengthArray[ii])):
                                print(':'+str(lengthArray[ii][jj]))
                '''     
                group=[]
                seq=[]
                for ii in range(1,len(indice)):
                        if(indice[ii]-indice[ii-1]==1):
                                seq.append(indice[ii-1])
                        else:
                                if(len(seq)!=0):
                                        seq.append(indice[ii-1])
                                        group.append(seq)
                                        seq=[]
                if(len(seq)>0):
                        seq.append(indice[len(indice)-1])
                        group.append(seq)

                '''
                print(group)
                for ii in range(0,len(group)):
                        for jj in range(0,len(group[ii])):
                                print(self.getLength(lengthArray,group[ii][jj]));
                                print(sequence[group[ii][jj]]);
                
                print('====================')
                '''
                multiplier=0
                for ii in range(0,len(group)):
                        length =self.getLength(lengthArray,group[ii][0]);
                        isNeck=False;
                        for jj in range(0,len(group[ii])):
                                isNeck=self.isExist(neckArea, group[ii][jj]);
                                if(isNeck):
                                        break;
                                
                        #print(length);
                        if(length<2):
                                continue;
                        elif (length>2 and length<6):
                                if(len(group[ii])>3 and isNeck==False):
                                        multiplier=len(group[ii])-3;
                        elif (length>5 and  length<10):
                                if(len(group[ii])>4 and isNeck==False):
                                        multiplier=len(group[ii])-4;
                                elif(len(group[ii])>6 and isNeck==True):
                                        multiplier=len(group[ii])-6;
                        else:
                                if(isNeck):
                                        for jj in range(0,len(group[ii])):
                                                
                                                isHalf=self.isHalf(group, jj);
                                                if(isHalf==False and len(group[ii])>6):
                                                        #print('----');
                                                        multiplier=len(group[ii])-6;
                                                        break;
                                                
                                else:
                                        for jj in range(0,len(group[ii])):
                                                isHalf=self.isHalf(group, jj);
                                                if(isHalf==False and len(group[ii])>4):
                                                        multiplier=len(group[ii])-4;
                                                        break;

                score += multiplier*params[0]
                return score




