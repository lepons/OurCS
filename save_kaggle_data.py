import os
import csv
import re

# save kaggle data

def save_kaggle_data(kaggledata_path,output_path,max_num):
    """ parses kaggle data which is in csv format
    Attributes:
        kaggledata_path (folder where the csv files are stored)
        max_num int of number of articles to save
    """
    files = os.listdir(kaggledata_path)
    csv.field_size_limit(100000000)

    count = 0
    for file in files:
        if (file[-4:] == '.csv'):
            with open(kaggledata_path+file) as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',')
                for row in readCSV:
                    try:
                        title = re.sub(r'([^\s\w]|_)+', '', row[2])
                        f = open(output_path+title+'.txt',"w+")
                        f.write(row[9])
                        f.close()
                        count += 1
                    except:
                        print("error parsing 1 file")
                    if (count == max_num):
                        return;


if __name__ == '__main__':

    kaggledata_path = "./kaggle/"
    output_path = "./kagglenews/"
    max_num = 1000
    save_kaggle_data(kaggledata_path,output_path,max_num)
