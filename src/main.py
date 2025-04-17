import sys

from app import EpicEvents


def main():
    app = EpicEvents()
    try:
        app.start()
    except KeyboardInterrupt:
        app.exit()
    except Exception as e:
        print(f"Une erreur inattendue s'est produite: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()