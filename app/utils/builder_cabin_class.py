import csv
if __name__ == '__main__':
    # write data to cabin.csv
    filepath = "flight/management/data/cabin.csv"
    CABIN_CLASS = [
        ("E", "Economy", 200),
        ("P", "Premium Economy", 1000),
        ("B", "Business", 1500),
        ("F", "First", 2000),
    ]
    with open(filepath, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["abb", "des", "score"])
        writer.writeheader()
        for cabin in CABIN_CLASS:
            writer.writerow({"id": cabin[0], "name": cabin[1]})