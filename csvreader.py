import csv


class CsvReader(object):

    def __init__(self, csv_file):
        self.csv = csv_file

    def parse(self):
        csvFile = open(self.csv, "r")
        print(self.csv)
        result = []
        with open(self.csv, "r") as file:
            reader = csv.reader(csvFile)
            for item in reader:
                result.append([item[0], item[1]])
        return result
