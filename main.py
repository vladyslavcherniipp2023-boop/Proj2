"""
Точка входу — запускати звідси.
"""
import sys
import os

# дозволяє імпортувати models/services без відносних шляхів
sys.path.insert(0, os.path.dirname(__file__))

from ui.app import App

if __name__ == "__main__":
    App().mainloop()
