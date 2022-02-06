import os.path
import sys

if __name__ == "__main__":
    try:
        from secret_santa import main
    except ImportError as e:
        sys.path.insert(0, os.path.dirname(__file__))
        from secret_santa.secret_santa import main

    sys.exit(main())
