

def main():

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', type=str, help='', metavar='file')
    args = parser.parse_args()

    from ast import literal_eval

    with open(args.filename) as f:

        texts = f.read()
        checklist = literal_eval(texts)

    apartments = []

    for line in checklist:

        apartment = line["apartment"]
        apartments.append(apartment)

    print(len(apartments))

    apartments = set(apartments)

    print(len(set(apartments)))

    return

if __name__ == '__main__':
    main()
