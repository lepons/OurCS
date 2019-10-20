file = open('query.txt','r')
filepos = open('new_pos_query.txt','r')
fileneg = open('new_neg_query.txt','r')
sameoutput = open('same_query.txt','w')
diffoutput = open('diff_query.txt','w')

diff = set()
same = set()
query = set()
negquery = set()
posquery = set()
with open('query.txt') as file:
    og = file.read().split('\n')
    for line in og:
        info =  line.split(' ')
        if (len(info) > 1):
            query.add(info[0])
# different words
with open('new_neg_query.txt') as file:
    neg = file.read().split('\n')
    for line in neg:
        info =  line.split(' ')
        if (len(info) > 1):
            negquery.add(info[0])
    diff = query.difference(negquery)

# same words
with open('new_pos_query.txt') as file:
    pos = file.read().split('\n')
    for line in neg:
        info =  line.split(' ')
        if (len(info) > 1):
            posquery.add(info[0])

same = query.intersection(posquery)

#output
sameoutput.write('\n'.join(same))
sameoutput.close()
diffoutput.write('\n'.join(diff))
diffoutput.close()
file.close()
filepos.close()
fileneg.close()
