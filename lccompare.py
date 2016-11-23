import csv

LC_PROD_CSV = 'lc_prod_prices.csv'
CT_PROD_CSV = 'ct_prod_prices.csv'

# Afuresertib info for testing
AFUR_NAME = "A-6877 Afuresertib, Hydrochloride Salt, >99%"

class ProdTable:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        # self.reader = self.make_reader()

    # def make_reader(self):
        # with open(self.csv_file, 'r') as f:
        #     reader = csv.DictReader(f, ["product", "size", "price"])
        # return reader
    #     # Problem is that the file closes. You can just do this one line
    #     # anywhere you want but I'd like it to be a function.
    #     # TODO: Stop this from closing (don't use 'with')

    def print_prods(self):
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f, ["product", "size", "price"])
            for row in reader:
                print(row["product"])

    def get_price(self, prod_name, prod_size):
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f, ["product", "size", "price"])
            for row in reader:
                if row["product"] == prod_name and row["size"] == prod_size:
                    return row["price"]
            return "Product or size not found"

    def get_prod_price_list(self, prod_name):
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f, ["product", "size", "price"])
            prod_price_list = []
            # prod_found = False
            for row in reader:
                if row["product"] == prod_name:
                    prod_price_list.append([prod_name, row["size"], row["price"]])
                    # prod_found = True
            return prod_price_list

    # TODO: Add CAS #s to lc/ct_prod_csv tables, and compare them that way
    def zip_prod_table(self, prod_csv):
        pass

if __name__ == '__main__':
    lc_table = ProdTable(LC_PROD_CSV)
    # lc_table.print_prods()
    # print(lc_table.get_price(AFUR_NAME, "100 mg"))
    print(lc_table.get_prod_price_list(AFUR_NAME))
