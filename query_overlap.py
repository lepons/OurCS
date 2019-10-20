
negoutput = open('same_neg_query.txt','w')
posoutput = open('same_pos_query.txt','w')

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
# print(query)
# same words
with open('new_neg_query.txt') as negfile:
    neg = negfile.read().split('\n')
    for line in neg:
        info =  line.split(' ')
        if (len(info) > 1):
            negquery.add(info[0])
# print(negquery)
same_neg = query.intersection(negquery)
# print(same_neg)

# same words
with open('new_pos_query.txt') as posfile:
    pos = posfile.read().split('\n')
    for line in pos:
        info =  line.split(' ')
        if (len(info) > 1):
            posquery.add(info[0])
# print(posquery)
same_pos = query.intersection(posquery)
# print(same_pos)

#output
negoutput.write('\n'.join(same_neg))
negoutput.close()
posoutput.write('\n'.join(same_pos))
posoutput.close()
