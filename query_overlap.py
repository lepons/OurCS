
negoutput = open('same_neg_query.txt','w')
posoutput = open('same_pos_query.txt','w')

same_neg = []
same_pos = []
query = set()
negquery = []
posquery = []
with open('query.txt') as file:
    og = file.read().split('\n')
    for line in og:
        info =  line.split(' ')
        if (len(info) > 1):
            query.add(info[0])
# print(query)
# same words
with open('new_neg_query.txt') as negfile:
    neg = negfile.read().split('\n')
    for line in neg:
        info =  line.split(' ')
        if (len(info) > 1):
            negquery.append(info)
# print(negquery)
for w in negquery:
    if ( w[0] in query ):
        same_neg.append(w)
# print(same_neg)

# same words
with open('new_pos_query.txt') as posfile:
    pos = posfile.read().split('\n')
    for line in pos:
        info =  line.split(' ')
        if (len(info) > 1):
            posquery.append(info)
# print(posquery)
for w in posquery:
    if ( w[0] in query ):
        same_pos.append(w)
# print(same_pos)

#output
for info in same_pos:
    posoutput.write(info[0]+' '+info[1]+ '\n')
for info in same_neg:
    negoutput.write(info[0]+' '+info[1] + '\n')
# negoutput.write('\n'.join(same_neg))
negoutput.close()
# posoutput.write('\n'.join(same_pos))
posoutput.close()
