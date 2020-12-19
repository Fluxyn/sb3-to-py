import json, os, sys
from conversion_opcodes import conversion_opcodes
from zipfile import ZipFile

def convert(filepath):
    print('Reading file...', end='')
    try:
        file = ZipFile(filepath, 'r')
    
        projectname = os.path.basename(filepath)
    
        projectdict = json.loads(file.read('project.json'))
    
        spritelist = projectdict['targets']
    
        broadcastlist = [list(i['broadcasts'].values())[0] for i in spritelist if i['broadcasts']]
        brodcastdict = {i: False for i in broadcastlist}
    
        codedict = {}
        [codedict.update(i['blocks']) for i in spritelist]

        print('')

    except:
        print('error')
        sys.exit()

    print('Converting code...', end='')
    try:
        codelist = []
        for i in codedict:
            if codedict[i]['parent'] == None:
                tmp = []
                tmp.append({i: codedict[i]})
                block = codedict[i]['next']
                while block:
                    tmp.append({block: codedict[block]})
                    block = codedict[block]['next']
                codelist.append(tmp)
        
        def pyconvert(blockid):
            def indent(text):
                return text.replace('\n', '\n    ')
            sprite = [sprite['name'] for sprite in spritelist if blockid in sprite['blocks']][0]
        
            field_opcodes = ['event_whenkeypressed'] #opcodes of blocks that take input from 'fields'
            if any(opc in codedict[blockid]['opcode'] for opc in field_opcodes):
                items = list(codedict[blockid]['inputs'].items()) + list(codedict[blockid]['fields'].items()) 
            else:
                items = codedict[blockid]['inputs'].items()
        
            for key, val in items:
                if isinstance(val, list) and len(val) == 2:
                    if isinstance(val[1], list): #type: [1, [4, '10']]
                        exec(f'{key} = """{val[1][1]}"""')
                    elif val[1] == None: #type: ['space', None]
                        exec(f'{key} = """{val[0]}"""')
                    else: #type: [2, '?wh2~G4eqc/%]}=x@9{+']
                        exec(f'{key} = """{pyconvert(val[1])}"""')
                elif isinstance(val, list) and len(val) == 3: #type: [3, 'OdXqTJFNBX)bGY:TGVA?', [10, '']]
                    exec(f'{key} = """{pyconvert(val[1])}"""')
        
            #below are opcodes of events that are not indented
            no_indent_opcodes = ['control_start_as_clone', 'control_forever', 'event_whentouchingobject', 'event_whenflagclicked', 'event_whenthisspriteclicked', 'event_whenstageclicked', 'event_whenbroadcastreceived', 'event_whenbackdropswitchesto', 'event_whengreaterthan', 'event_whenkeypressed']
            
            if any(opc in codedict[blockid]['opcode'] for opc in no_indent_opcodes):
                symbol = ''
            else:
                symbol = '¶'
            
            try:
                return symbol + eval("f'''"+conversion_opcodes[codedict[blockid]['opcode']]+"'''")
            except NameError as e:
                locals()[str(e).split("'")[1]] = symbol + 'pass'
                return symbol + eval("f'''"+conversion_opcodes[codedict[blockid]['opcode']]+"'''")
            except KeyError:
                return '[scratch code not yet added to conversion_opcodes]'    
        
        finalcode = []
        for code in codelist:
            for block in code:
                for blockid in block:
                    finalcode.append(pyconvert(blockid))
        
        for n in range(len(finalcode)):
            if finalcode[n].startswith('¶'):
                finalcode[n] = '\n'.join(['    ' + i for i in finalcode[n].split('\n')]).replace('¶', '')
        
        finalcode = '\n\n'.join(finalcode).replace('\n', '\n    ')

        print('')

    except:
        print('error')
        sys.exit()

    print('Rendering sprites...', end='')
    try:
        spritelist = [{i['name']: [{cos['name']: cos['md5ext']} for cos in i['costumes']]} for i in spritelist]
        
        classtemplate = '''
        class {name}_object(pygame.sprite.Sprite):
            def __init__(self, position):
                pygame.sprite.Sprite.__init__(self)
                self.costumes = {costumes}
                self.costume_num = 0
                self.image = loadsvg(self.costumes[self.costume_num])
                self.rect = self.image.get_rect(center=position)
                self.pos_y = position[0]
                self.pos_x = position[1]
        
            def update(self):
                self.rect.y = self.pos_y
                self.rect.x = self.pos_x
                if self.costume_num > len(self.costumes):
                    self.costumes = 0
                self.image = loadsvg(self.costumes[self.costume_num])
        
        {name} = {name}_object((0, 0))
        sprite_list.add({name})
        sprite_list.update()
        '''

        costumelist = []
        classes = []
        for sprite in spritelist:
            if list(sprite)[0] != 'Stage':
                name = list(sprite)[0]
                costumes = [list(i.values())[0] for i in sprite[name]]
                [costumelist.append({i: file.read(i)}) for i in costumes]
                classes.append(eval("f'''"+classtemplate+"'''"))
        
        classes = '\n'.join(classes)

        print('')

    except:
        print('error')
        sys.exit()

    print('Packaging python...', end='')
    try:
        projectname = os.path.splitext(os.path.basename(filepath))[0]
        
        finalpygame = f'''import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
from svg import Parser, Rasterizer
import pygame, time, random, sys
        
pygame.init()
        
window_width = 480
window_height = 360
background = (255, 255, 255)
        
screen = pygame.display.set_mode((window_width, window_height))
screen.fill((255, 255, 255))
pygame.display.set_caption('{projectname}')
        
font = pygame.font.Font(None, 15)
sprite_list = pygame.sprite.Group()
clock = pygame.time.Clock()
start = True
broadcastdict = {brodcastdict}
        
def loadsvg(filename):
    svg = Parser.parse_file(filename)
    buffer = Rasterizer().rasterize(svg, svg.width, svg.height, 1, 0, 0)
    return pygame.image.frombuffer(buffer, (svg.width, svg.height), 'RGBA')
        
{classes}
pygame.display.update()
        
        
def loop():
    global start, broadcastdict
    {finalcode}
        
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        
    screen.fill((255, 255, 255))
    loop()
    for sprite in sprite_list:
        screen.blit(sprite.image, sprite.rect)
        sprite.update()
    pygame.display.flip()
    clock.tick(30)
        
pygame.quit()
sys.exit()'''
        
        return projectname, costumelist, finalpygame

    except:
        print('error')
        sys.exit()
