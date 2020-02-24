#to store the list of constituents in each line
lines={}

#the registers
registers={}

#the memory
memory={}

#the data variables in the '.data' section
variables={}

#exactly what the name suggests
jumplabels={}

regname=['$r0','$at','$v0','$v1','$a0','$a1','$a2','$a3','$t0','$t1','$t2','$t3','$t4','$t5','$t6','$t7','$s0','$s1','$s2','$s3','$s4','$s5','$s6','$s7','$t8','$t9','$k0','$k1','$gp','$sp','$fp','$ra']
for i in regname:
    registers[i]=0
for i in range(4096):
    memory[i]='00000000'

#to convert a number into its 32-bit 2's complement binary form
def binary(n):
    if(n<0):
        st = bin(2 ** 32 + n)
        st = st.replace('0b', '')
    else:
        st = bin(n)
        st = st.replace('0b', '')
        m=32-len(st)
        att=''
        for i in range(m):
            att = att + '0'
        st = att + st
    return st

#to convert a 32-bit 2's complement binary number into its decimal form
def decimal(s):
    if(s[0]=='0'):
        return int(s,2)
    else:
        return int(s,2)-2**32

#to store a number in its 32-bit 2's complement binary form to memory
def store(m,n):
    b=binary(n)
    memory[m]=b[0:8]
    memory[m+1]=b[8:16]
    memory[m+2]=b[16:24]
    memory[m+3]=b[24:32]

#to read the 4-byte data that begins from the mth byte
def read(m):
    a=''
    for i in range(4):
        a+=memory[m+i]
    return a

#class for 'add'
class adder:
    def doit(self,linecontent):
        global linecounter
        linecounter+=1
        registers[linecontent[1]] = registers[linecontent[2]] +  registers[linecontent[3]]

#class for 'sub'
class subter:
    def doit(self,linecontent):
        global linecounter
        linecounter+=1
        registers[linecontent[1]] = registers[linecontent[2]] - registers[linecontent[3]]

#class for 'sll'
class lshifter:
    def doit(self,linecontent):
        global linecounter
        linecounter+=1
        a=binary(registers[linecontent[2]])
        shiftby=int(linecontent[3],10)
        a=a[shiftby:32]
        for i in range(shiftby):
            a+='0'
        registers[linecontent[1]]=decimal(a[0:32])

#class for 'slr'
class rshifter:
    def doit(self,linecontent):
        global linecounter
        linecounter+=1
        a=binary(registers[linecontent[2]])
        shiftby=int(linecontent[3],10)
        b=''
        for i in range(shiftby):
            b+=a[0]
        a=b+a[0:32-shiftby]
        registers[linecontent[1]] = decimal(a[0:32])

#class for 'lw'
class loader:
    def doit(self,linecontent):
        global linecounter
        linecounter+=1
        l=linecontent[2].replace(')','').split('(')
        offset=int(l[0],10)
        if(registers[l[1]] + offset >4091  and   registers[l[1]] + offset >=0):
            print("Memory out of bound at line " + str(linecounter))
            linecounter=-1
        if(linecounter!=-1):
            registers[linecontent[1]]=int(read(registers[l[1]]+offset),2)

#class for 'sw'
class storer:
    def doit(self,linecontent):
        global linecounter
        linecounter+=1
        l = linecontent[2].replace(')', '').split('(')
        offset=int(l[0],10)
        if (registers[l[1]] + offset > 4091  and   registers[l[1]] + offset >=0):
            print("Memory out of bound at line " + str(linecounter))
            linecounter = -1
        if(linecounter!=-1):
            store(registers[l[1]]+offset,registers[linecontent[1]])

#class for 'j'
class jumper:
    def doit(self,linecontent):
        global linecounter
        linecounter=jumplabels[linecontent[1].replace(':','')]

#class for 'bne' and 'beq'
class brancher:
    def doit(self,linecontent):
        global linecounter
        if(linecontent[0]=='beq' and registers[linecontent[1]]==registers[linecontent[2]]):
            linecounter=jumplabels[linecontent[3]]
        elif(linecontent[0]=='beq'):
            linecounter+=1
        elif(linecontent[0]=='bne' and registers[linecontent[1]]!=registers[linecontent[2]]):
            linecounter = jumplabels[linecontent[3]]
        else:
            linecounter+=1

#class for 'addi'
class immadder:
    def doit(self,linecontent):
        global linecounter
        linecounter+=1
        registers[linecontent[1]] = registers[linecontent[2]] +  int(linecontent[3],10)

#class for 'li'
class immloader:
    def doit(self,linecontent):
        global linecounter
        linecounter+=1
        registers[linecontent[1]]=int(linecontent[2],10)

#class for 'slt'
class lesser:
    def doit(self,linecontent):
        global linecounter
        linecounter+=1
        if(registers[linecontent[2]]<registers[linecontent[3]]):
            registers[linecontent[1]]=1
        else:
            registers[linecontent[1]]=0

#class for 'la'
class addrloader:
    def doit(self,linecontent):
        global linecounter
        linecounter+=1
        registers[linecontent[1]]=variables[linecontent[2]]


#method to check for syntax errors in a passed line
def errorchecker(linecontent,line1) :
    if(len(linecontent)==0):
        return 1
    line=line1.replace(' ','')
    if(linecontent[0]=='add' or linecontent[0]=='sub' or linecontent[0]=='slt'):
        if (len(linecontent)!=4):
            print("Invalid syntax at line "  +  str(linecounter))
        elif (line[6]!=',' or line[10]!=',' ):
            print("Missing ',' at line " + str(linecounter))
        elif( linecontent[1] not in regname):
            print("Undefined symbol " + linecontent[1] + " at line " + str(linecounter))
        elif( linecontent[2] not in regname):
            print("Undefined symbol " + linecontent[2] + " at line " + str(linecounter))
        elif( linecontent[3] not in regname):
            print("Undefined symbol " + linecontent[3] + " at line " + str(linecounter))
        elif(linecontent[1] == '$r0'):
            print("Trying to alter immutable value at line " + str(linecounter))
        else:
            return 1

    elif (linecontent[0]=='sll' or linecontent[0]=='slr' or linecontent[0]=='addi'):
        num=linecontent[3].replace('-','')
        if (len(linecontent)!=4):
            print("Invalid syntax at line "  +  str(linecounter))
        elif ((line[6]!=',' or line[10]!=',') and linecontent[0]!='addi'):
            print("Missing ',' at line " + str(linecounter))
        elif((line[7]!=',' or line[11]!=',') and linecontent[0]=='addi'):
            print(line)
            print("Missing ',' at line " + str(linecounter))
        elif( linecontent[1] not in regname):
            print("Undefined symbol " + linecontent[1] + "at line " + str(linecounter))
        elif( linecontent[2] not in regname):
            print("Undefined symbol " + linecontent[2] + "at line " + str(linecounter))
        elif (linecontent[1] == '$r0'):
            print("Trying to alter immutable value at line " + str(linecounter))
        elif (not linecontent[3].isdigit() and linecontent[0]!='addi'):
            print("Non-constant shift amount found at line " + str(linecounter))
        elif(not num.isdigit() and linecontent[0]=='addi'):
            print("Non-constant add amount found at line " + str(linecounter))
        else:
            return 1

    elif(linecontent[0]=='lw' or linecontent[0]=='sw'):
        splitline=linecontent[2].split('(')
        numlen=len(splitline[0])
        if (len(linecontent)!=3 or line[6+numlen]!='(' or line[numlen+10]!=')'):
            print("Invalid syntax at line "  +  str(linecounter))
        elif (line[5]!=','):
            print("Missing ',' at line " + str(linecounter))
        elif(not splitline[0].isdigit()):
            print("Non-constant offset found at line " + str(linecounter))
        elif( linecontent[1] not in regname):
            print("Undefined symbol " + linecontent[1] + "at line " + str(linecounter))
        elif( splitline[1].replace(')','') not in regname):
            print("Undefined symbol " + splitline[1].replace(')','') + "at line " + str(linecounter))
        elif (linecontent[1] == '$r0' and linecontent[0]=='lw' ):
            print("Trying to alter immutable value at line " + str(linecounter))
        else:
            return 1

    elif (linecontent[0]=='li'):
        number=linecontent[2].replace('-','')
        if (len(linecontent)!=3):
            print("Invalid syntax at line "  +  str(linecounter))
        elif (line[5]!=','):
            print("Missing ',' at line " + str(linecounter))
        elif( linecontent[1] not in regname):
            print("Undefined symbol " + linecontent[1] + "at line " + str(linecounter))
        elif (linecontent[1] == '$r0'):
            print("Trying to alter immutable value at line " + str(linecounter))
        elif (not number.isdigit() ):
            print("Non-constant load amount found at line " + str(linecounter))
        else:
            return 1

    elif (linecontent[0]=='la'):
        if (len(linecontent)!=3):
            print("Invalid syntax at line "  +  str(linecounter))
        elif (line[5]!=','):
            print("Missing ',' at line " + str(linecounter))
        elif( linecontent[1] not in regname):
            print("Undefined symbol " + linecontent[1] + "at line " + str(linecounter))
        elif (linecontent[1] == '$r0'):
            print("Trying to alter immutable value at line " + str(linecounter))
        elif (linecontent[2] not in variables.keys() ):
            print("Invalid memory label at line " + str(linecounter))
        else:
            return 1

    elif (linecontent[0] == 'bne' or linecontent[0] == 'beq'):
        if (len(linecontent) != 4):
            print("Invalid syntax at line " + str(linecounter))
        elif (line[6] != ',' or line[10] != ','):
            print("Missing ',' at line " + str(linecounter))
        elif (linecontent[1] not in regname):
            print("Undefined symbol " + linecontent[1] + "at line " + str(linecounter))
        elif (linecontent[2] not in regname):
            print("Undefined symbol " + linecontent[2] + "at line " + str(linecounter))
        elif (linecontent[3] not in jumplabels.keys()):
            print("Invalid label " + linecontent[3] + "at line " + str(linecounter))
        else:
            return 1

    elif (linecontent[0] == 'j'):
        if (len(linecontent) != 2):
            print("Invalid syntax at line " + str(linecounter))
        elif (linecontent[1] not in jumplabels.keys()):
            print("Invalid label " + linecontent[1] + " at line " + str(linecounter))
        else:
            return 1
    elif (linecontent[0] == 'jr'):
        if (linecontent[1]!='$ra'):
            print("Invalid syntax at line " + str(linecounter))
        else:
            return 1
    else:
        print("Invalid syntax at line " + str(linecounter))
    return -1

#to print part of memory and all the registers
def printer():
    print("__________MEMORY____________")
    for i in range(128):
        print( str(4*i)  + " |" +  str(decimal(memory[4*i] + memory[4*i +1] + memory[4*i +2] + memory[4*i +3])), end="|    "   )
        if(i%16==15):
            print()
    print()
    print("__________REGISTERS__________")
    j=0
    for i in regname:
        print( i + "  |" + str(registers[i]),end="|   ")
        j+=1
        if(j%8==0):
            print()
    print()


#the main code begins here
'''HELLO THERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'''


i=1

#to input the location of file from the user
filename=input("Enter file location")

linescopy={}
with open(filename) as file:
    data = file.readlines()
    for j in data:
        j=j.replace('\t','')
        if(j.replace(' ','')!='\n'):
            lines[i]=j
            linescopy[i]=j
            i=i+1

#linescopy contains each of the lines verbatim
#lines segregates the line into keyword, register names, and constants

for x in range(1,len(linescopy)):
    linescopy[x]=linescopy[x].replace('\n' ,'')
for j in range(1,i) :
    lines[j]=lines[j].replace(',',' ')
    lines[j]=lines[j].split()
n=len(lines)
linecounter=1
memorycounter=0

#to detect the data variables
if lines[linecounter][0]=='.data':
    linecounter+=1
    for l in range(linecounter,n):
        if(len(lines[l])==0):
            linecounter+=1
            continue
        elif(lines[l][0]=='.text'):
            linecounter+=1
            break
        else:
            x=0
            if(lines[l][0]!='.word'):
                variables[lines[l][0].replace(':', '')] = memorycounter
                x+=1
            if (lines[l][x] == '.word'):
                for var in range(x+1,len(lines[l])):
                    store(memorycounter,int(lines[l][var],10))
                    memorycounter+=4
            linecounter+=1


if(lines[linecounter][0].startswith('.') ):
    if(lines[linecounter][0]!='.globl'):
        print("Undefined symbol " + lines[linecounter][0] + "at line "  + str(linecounter))
        linecounter=-1
    else:
        linecounter+=1

codebegin=linecounter

#to detect jump-labels
for l in range(codebegin,n):
    if (linecounter<=0):
        break
    temp=lines[linecounter][0]
    if temp.endswith(':'):
        temp=temp.replace(':','')
        if(temp in jumplabels.keys()):
            print("Invalid label at line"+str(linecounter))
            linecounter=-1
        jumplabels[temp]=linecounter
        bek=lines[linecounter].pop(0)
    linecounter+=1
linecounter=codebegin
x=0

#error checking
for l in range(codebegin,n):
    x=errorchecker(lines[l],linescopy[l])
    if(x==-1):
        print(linescopy[l])
        break

#if no errors found, we proceed further to user choices
if(x!=-1):
    a=adder()
    b=subter()
    c=rshifter()
    d=lshifter()
    e=loader()
    f=storer()
    g=jumper()
    h=brancher()
    i=immadder()
    j=immloader()
    k=lesser()
    m=addrloader()

    operators={'add':a ,'sub':b , 'slr':c ,'sll':d ,'lw':e ,'sw':f ,'j':g ,'beq':h ,'bne':h ,'addi':i ,'li':j ,'slt':k ,'la':m}
    #to create objects and connect them with their respective keyword and function

    print("1.....RUN")
    print("2.....STEP BY STEP")
    rep=input()
    rep=int(rep)

    if (rep==2):
        while(rep==2 and linecounter!=-1 and linecounter<=n):
            print(linescopy[linecounter])
            if (lines[linecounter] == ['jr', '$ra']):
                linecounter = -1
            elif(lines[linecounter]==[]):
                linecounter+=1
            else:
                operators[lines[linecounter][0]].doit(lines[linecounter])
            printer()
            rep=int(input("Next step"))


    if (rep == 1):
        while (linecounter != -1 and linecounter<=n):
            if (lines[linecounter] == ['jr', '$ra']):
                linecounter = -1
            elif (lines[linecounter] == []):
                linecounter += 1
            else:
                temp=operators[lines[linecounter][0]]
                temp.doit(lines[linecounter])
        printer()
