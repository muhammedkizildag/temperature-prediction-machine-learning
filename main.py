import argparse






if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="First")

    parser.add_argument("name", help="Name of person")
    parser.add_argument("-r", "--repetition", type=int, default=1, help="Number of repetitions")

    args = parser.parse_args()


    for _ in range(args.repetition):
        print(f"Hello {args.name}")

