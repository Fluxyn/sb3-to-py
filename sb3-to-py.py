import sys, os
from convert import convert

if len(sys.argv) == 1:
    print('''usage: sb3-to-py --convert [options...] dir/to/file.sb3
   or: sb3-to-py --help
   see more at: https://github.com/lukarao/sb3-to-py''')
elif len(sys.argv) == 3:
    if sys.argv[1] == '--convert':
        if os.path.isfile(sys.argv[2]):
            convertedfile = convert(sys.argv[2])
            print(convertedfile)
            try:
                os.mkdir(os.path.expanduser(f'~/{convertedfile[0]}'))
            except:
                pass
            for i in convertedfile[1]:
                open(os.path.expanduser(f'~/{convertedfile[0]}/{list(i)[0]}'), 'wb').write([list(i.values())[0]][0])
            open(os.path.expanduser(f'~/{convertedfile[0]}/{convertedfile[0]}.py'), 'w').write(convertedfile[2])
            print('Conversion success! Saved in', f'~/{convertedfile[0]}')
            
        else:
            print(f'''Can't open file '{sys.argv[1]}': No such file or directory.''')

