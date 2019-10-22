from pycparser import parse_file

if "__main__" == __name__:
    ast = parse_file("main.c.pure", use_cpp=False)
    print(ast)
