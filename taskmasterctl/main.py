from TaskMasterCtl import TaskMasterCtl
import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <port>")
        sys.exit(1)

    taskmaster = TaskMasterCtl(int(sys.argv[1]))
    taskmaster.run()


if __name__ == '__main__':
    main()
