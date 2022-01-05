"""
```yml
    _   _             _       
   / \ | |_ ___  _ __(_)_ __  
  / _ \| __/ _ \| '__| | '_ \ 
 / ___ \ || (_) | |  | | | | |
/_/   \_\__\___/|_|  |_|_| |_|
```
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                              
Made with ❤️ by Piotr Gaździcki.

"""


def progress_bar(percent: int, text: str = "") -> str:
    j = percent / 100
    return f"[{'|' * int(10 * j):{10}s}] {int(100 * j)}%  {text}"
