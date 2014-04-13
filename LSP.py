import pygame,math,time,sys,random,pygame.gfxdraw

RESOLUTION_X = 1024
RESOLUTION_Y = 600

SPAWN_TIME = 0.8
HOLD_BEFORE_DEATH=0.8
DECAY_TIME = 0.4

MOUSE_HISTORY_SIZE =100

BKG_COLOR = (45,17,44)

FONTU = None
BACKGROUND = None

scoreColors=[
    (225, 233, 43),
    (197, 255, 96),
    (167, 252, 253),
    (255, 148, 70),
    (225, 67, 23),
]

#HURRR DURR PYTHON SUX
def blit_alpha(target, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pygame.Surface((source.get_width(), source.get_height())).convert()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)        
        target.blit(temp, location)


class LSPBeat(object):

    STATE_SPAWN = 0
    STATE_WAITING = 1
    STATE_DYING = 2
    STATE_FAILED = 3

    """
    Its basically abstract
    """
    def __init__(self, spawntime):
        self.spawntime = spawntime
        self.changetime = 0
        self.state = LSPBeat.STATE_SPAWN
        self.isdead = False

    """Takes in the current gametime (time of trigger)
    and returns the object.

    Enters this object into the despawn state, where the proper
    animations are carried out
    """
    def trigger(self, gametime, mousehistory):
        self.state = LSPBeat.STATE_DYING
        self.changetime = gametime
        return abs(gametime - self.spawntime)

    def render(self, screen, gametime):
        #print gametime, self.changetime, gametime - self.changetime
        if (self.state == LSPBeat.STATE_SPAWN):
            self.render_spawn(screen, gametime-self.changetime)

        elif (self.state == LSPBeat.STATE_WAITING):
            self.render_wait(screen, gametime-self.changetime)

        elif (self.state == LSPBeat.STATE_FAILED):
            self.render_failed(screen, gametime-self.changetime)

        else:
            self.render_dying(screen, gametime-self.changetime)

    def update(self, gametime):

        if(self.changetime == 0):
            self.changetime = gametime

        if(self.state == LSPBeat.STATE_SPAWN and 
            self.changetime + SPAWN_TIME <= gametime):
            self.changetime = gametime
            self.state = LSPBeat.STATE_WAITING

        if(self.state == LSPBeat.STATE_WAITING and
            gametime > self.changetime+HOLD_BEFORE_DEATH):
            self.changetime = gametime
            self.state = LSPBeat.STATE_FAILED

        if( (self.state == LSPBeat.STATE_DYING or self.state == LSPBeat.STATE_FAILED) and 
            self.changetime + DECAY_TIME <= gametime):
            self.changetime = gametime
            self.isdead = True

    def check_hit(self,mousehistory):
        return False

    def render_spawn(self, screen, elapsed):
        pass

    def render_wait(self, screen, elapsed):
        pass

    def render_dying(self,screen, elapsed):
        pass

    def render_failed(self,screen,elapsed):
        pass

class LSPGate(LSPBeat):

    BLOCK_IMAGE = None

    """
        centered on x,y
    """
    def __init__(self, spawntime, x, y, angle):
        LSPBeat.__init__(self, spawntime)

        self.x = x * RESOLUTION_X
        self.y = y * RESOLUTION_Y
        self.angle = angle
        self.breakspot = 0

        self.rendered = pygame.transform.rotate(
            LSPGate.BLOCK_IMAGE,
            math.degrees(angle))

        tem = max(self.rendered.get_width(), self.rendered.get_height())

        self.rendered = self.rendered.convert_alpha()
        self.roughrect = pygame.rect.Rect( (self.x-tem/2,self.y-tem/2,tem, tem) )

        #print self.roughrect

    def check_hit(self, mousehistory):
        poststep = mousehistory[-1]
        prestep = mousehistory[-2]

    """Determines if pm lies on line segment defined by p1 and p2"""
    def on_segment(self, pm, p1, p2):
        xmin = min(p1[0], p2[0])
        ymin = min(p1[1], p2[1])
        xmax = max(p1[0], p2[0])
        ymax = max(p1[1], p2[1])
        return (xmin <= pm[0] <= xmax) and (ymin <= pm[1] <= ymax)


    def check_hit(self, mousehistory):

        if(self.roughrect.collidepoint(mousehistory[-1])):
            poststep = mousehistory[-1]
            prestep = mousehistory[-2]

            if (poststep[0] == prestep[0]) or (poststep[1] == prestep[1]):
                return False
            #Calculate endpoints of gate
            MAGIC_NUMBER = 100
            g1 = (self.x + MAGIC_NUMBER * math.sin(self.angle),
                    self.y + MAGIC_NUMBER * math.cos(self.angle))
            g2 = (self.x - MAGIC_NUMBER * math.sin(self.angle),
                    self.y - MAGIC_NUMBER * math.cos(self.angle))

            if (g2[0] == g1[0] and poststep[0] != prestep[0]):
                m1 = float((poststep[1] - prestep[1])) / float((poststep[0] - prestep[0]))
                y = prestep[1] + m1 * (g2[0] - prestep[0])
                ret = self.on_segment((g2[0], y), prestep, poststep) and self.on_segment((g2[0], y), g1, g2)
                self.collidepoint = (g2[0],y) if ret else None
                return ret

            elif (g2[0] == g1[0] and poststep[0] == prestep[0]):
                return False

            elif (g2[0] != g1[0] and poststep[0] != prestep[0]):
                m1 = float((poststep[1] - prestep[1])) / float((poststep[0] - prestep[0]))
                m2 = float((g2[1] - g1[1])) / float((g2[0] - g1[0]))
                
                if(m1 != m2):
                    x = (g2[1] - prestep[1] + m1 * prestep[0] - m2 * g2[0]) / (m1 - m2)
                    y = m2 * (x - g2[0]) + g2[1]

                    ret = self.on_segment((x, y), prestep, poststep) and self.on_segment((x, y), g1, g2)
                    self.collidepoint = (x,y) if ret else None
                    return ret

                else:
                    return False


    def render_spawn(self, screen, elapsed):
        blit_alpha(screen, self.rendered, (
            self.x - self.rendered.get_width()/2 ,
            self.y - self.rendered.get_height()/2 
        ), int(255 * min(1.0, elapsed / SPAWN_TIME)));
        

    def render_wait(self, screen, elapsed):
        screen.blit(self.rendered, (
            self.x - self.rendered.get_width()/2,
            self.y - self.rendered.get_height()/2) );


    def render_dying(self, screen, elapsed):
        if(self.split_horizontal):
            blit_alpha(screen, self.img1, (
                self.grav1.x - self.img1.get_width(),
                self.grav1.y - self.img2.get_height()/2, 
            ), int(255 * (1.0-min(1.0, elapsed / DECAY_TIME)) ));

            blit_alpha(screen, self.img2, (
                self.grav2.x,
                self.grav2.y - self.img2.get_height()/2 
            ), int(255 * (1.0-min(1.0, elapsed / DECAY_TIME)) ));
        else:
            blit_alpha(screen, self.img1, (
                self.grav1.x-self.img1.get_width()/2,
                self.grav1.y- self.img1.get_height(), 
            ), int(255 * (1.0-min(1.0, elapsed / DECAY_TIME)) ));

            blit_alpha(screen, self.img2, (
                self.grav2.x-self.img1.get_width()/2,
                self.grav2.y 
            ), int(255 * (1.0-min(1.0, elapsed / DECAY_TIME)) ));


    def render_failed(self, screen, elapsed):
        colored = pygame.transform.rotate(self.rendered, self.grav.rot);
        cul = pygame.Color( scoreColors[-1][0], scoreColors[-1][1], scoreColors[-1][2] )
        cul.a = int(255 * elapsed / DECAY_TIME)
        colored.fill(cul, special_flags=pygame.BLEND_RGB_MULT)

        blit_alpha(screen, colored, (
            self.grav.x - colored.get_width()/2 ,
            self.grav.y - colored.get_height()/2 
        ), int(255 * (1-(elapsed / DECAY_TIME))) );

    def trigger(self, gametime, mousehistory):
        if (mousehistory[-1][0] - mousehistory[-2][0]) != 0:
            attack_angle = math.atan(
                    (mousehistory[-1][1] - mousehistory[-2][1]) / 
                    (mousehistory[-1][0] - mousehistory[-2][0]))
        else:
            attack_angle = 0

        
        breakspot = (self.collidepoint[0] - self.x, self.collidepoint[1] - self.y);

        if( abs(self.angle) < math.pi/4 or abs((self.angle - math.pi)%math.pi) < math.pi/4 ):
            #vertical 
            self.split_horizontal = False
            r1 = pygame.rect.Rect(0,0,self.rendered.get_width(), self.rendered.get_height()/2)
            r2 = pygame.rect.Rect(0,self.rendered.get_height()/2,self.rendered.get_width(), self.rendered.get_height()/2)
            self.img1 = self.rendered.subsurface(r1)
            self.img2 = self.rendered.subsurface(r2)
            self.grav1 = GravityThing(self.x,self.y,-GravityThing.MOM_INIT_X, GravityThing.MOM_INIT_Y);
            self.grav2 = GravityThing(self.x,self.y, GravityThing.MOM_INIT_X, GravityThing.MOM_INIT_Y);
        else:
            self.split_horizontal = True
            r1 = pygame.rect.Rect(0,0,self.rendered.get_width()/2, self.rendered.get_height())
            r2 = pygame.rect.Rect(self.rendered.get_width()/2,0,self.rendered.get_width()/2, self.rendered.get_height())
            self.img1 = self.rendered.subsurface(r1)
            self.img2 = self.rendered.subsurface(r2)
            self.grav1 = GravityThing(self.x,self.y,-GravityThing.MOM_INIT_X, GravityThing.MOM_INIT_Y);
            self.grav2 = GravityThing(self.x,self.y, GravityThing.MOM_INIT_X, GravityThing.MOM_INIT_Y);

        mult = attack_angle / 2*math.pi
        dtime = gametime - time.time()

        LSPBeat.trigger(self, gametime, mousehistory)

        return (1.0 - dtime/0.5)*(0.8 + 0.2*mult)

    def update(self, gametime):
        LSPBeat.update(self, gametime)
        
        if(self.state == LSPGate.STATE_FAILED):
            if not 'grav' in self.__dict__:
                self.grav = GravityThing(self.x,self.y,
                    GravityThing.MOM_INIT_X*random.random(), 0.0)
            self.grav.update(gametime);

        if(self.state == LSPGate.STATE_DYING):
            self.grav1.update(gametime)
            self.grav2.update(gametime)


class GravityThing(object):
    
    GRAVITY = 0.1
    MOM_INIT_Y = -3
    MOM_INIT_X = 1
    LIFETIME = 1

    def __init__(self, x, y, xmov, ymov):
        self.x=x
        self.y=y
        self.ymov = ymov
        self.xmov = xmov
        self.initial = time.time()
        self.lud = self.initial

        self.isdead=False
        self.elapsed = 0
        self.rot = 0

        self.rmov = 0.2+random.random()*0.5
        if random.random() > 0.5:
            self.rmov = -self.rmov
        
    def update(self, nexttime):
        self.elapsed = nexttime - self.lud
        self.lud = nexttime

        self.ymov += GravityThing.GRAVITY * self.elapsed * 100
        self.x += self.xmov * self.elapsed * 100
        self.y += self.ymov * self.elapsed * 100

        self.rot += self.rmov * self.elapsed *100

        if( (self.lud -self.initial) > GravityThing.LIFETIME):
            self.isdead = True

    def getFracCompl(self):
        return (self.lud - self.initial)/GravityThing.LIFETIME

        

class ScoreParticle(object):

    def __init__(self, x, y, score):
        self.grav = GravityThing(x,y,
            GravityThing.MOM_INIT_X * random.random() - GravityThing.MOM_INIT_X * random.random(),
            GravityThing.MOM_INIT_Y * random.random());

        if(score>0.8):
            self.renderedtext = ScoreParticle.FONTU_BEST
        elif(score>0.6):
            self.renderedtext = ScoreParticle.FONTU_EH
        elif(score>0.4):
            self.renderedtext = ScoreParticle.FONTU_GOOD
        elif(score>0.2):
            self.renderedtext = ScoreParticle.FONTU_OH;
        else:
            self.renderedtext = ScoreParticle.FONTU_WORST
            
    def update(self, gametime):
        self.grav.update(gametime)

    def render(self, surface):
        self.renderedtext.set_alpha(255 - 255.0*self.grav.getFracCompl());

        n = pygame.transform.rotate(self.renderedtext, self.grav.rot);

        surface.blit(n,(self.grav.x-n.get_width()/2, self.grav.y-n.get_width()/2))

class SparksParticle(ScoreParticle):
    def __init__(self, x, y, score):
        self.grav = GravityThing(x,y,
            GravityThing.MOM_INIT_X * random.random() - GravityThing.MOM_INIT_X * random.random(),
            GravityThing.MOM_INIT_Y * 2*(0.5+0.5*random.random()) );

        if(score>0.8):
            self.color = scoreColors[0]
        elif(score>0.6):
            self.color = scoreColors[1]
        elif(score>0.4):
            self.color = scoreColors[2]
        elif(score>0.2):
            self.color = scoreColors[3]
        else:
            self.color = scoreColors[4]

    def update(self, gametime):
        self.grav.update(gametime)

    def render(self, surface):
        pygame.gfxdraw.filled_circle(surface, int(self.grav.x), int(self.grav.y),
                int(1.0 * self.grav.getFracCompl()* 5), self.color)

"""gets the display screen
"""
def do_init():
    global FONTU, BACKGROUND

    pygame.init();
    pygame.display.set_caption("LSP")
    screen = pygame.display.set_mode((RESOLUTION_X, RESOLUTION_Y))

    pygame.mouse.set_visible(False)
    FONTU = pygame.font.Font("./GOTHIC.TTF", 28);

    ScoreParticle.FONTU_BEST = FONTU.render("PERFECT!", False, scoreColors[0]);
    ScoreParticle.FONTU_EH = FONTU.render("GOOD!", False, scoreColors[1]);
    ScoreParticle.FONTU_GOOD = FONTU.render("OKAY.", False, scoreColors[2]);
    ScoreParticle.FONTU_OH = FONTU.render("NOT GREAT..", False, scoreColors[3]);
    ScoreParticle.FONTU_WORST = FONTU.render("KILL YOURSELF.", False, scoreColors[4]);


    #if(LSPGate.BLOCK_IMAGE == None):
    LSPGate.BLOCK_IMAGE = pygame.transform.rotozoom(pygame.image.load("./gatenew.png"),0,0.4)
    LSPGate.BLOCK_IMAGE = LSPGate.BLOCK_IMAGE.convert_alpha(screen)

    BACKGROUND = pygame.image.load("./background.png")

    return screen


"""
    screen: screen surface to blit to (pygame.Surface)
    gameobjs: [LSPBeat] list of LSPBeats sorted in nondecending
        order of hit time

"""
def mainloop(screen, gameobjs, song, bpm):
    initial = time.time()
    lastup = initial
    framelapse = 1.0/60.0

    livingobjs = []
    particles = []
    objptr = 0

    mousehistory = [pygame.mouse.get_pos()] * MOUSE_HISTORY_SIZE

    #print "starting (lapse = %s)"%(framelapse)

    while(True):
        gametime = time.time()
        elapsedTime = gametime - lastup

        #============== EVT ==============

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        #============== MOUSE HIST ==============

        mousehistory.append(pygame.mouse.get_pos())
        mousehistory = mousehistory[1:]

        #============== RENDER OBJS ==============

        #add objs as they come up
        #print gameobjs
        while(objptr < len(gameobjs) and 
                initial + gameobjs[objptr].spawntime <= gametime + SPAWN_TIME):
            #print "spawning obj (ini+spawn = %s, spawn = %s, game-- = %s)"%(initial + gameobjs[objptr].spawntime, gameobjs[objptr].spawntime, gametime - SPAWN_TIME)
            livingobjs.append(gameobjs[objptr])
            objptr += 1

        #============== UPDATES ==============

        #updating objs & particles
        for obj in livingobjs:
            obj.update(gametime)

        for part in particles:
            part.update(gametime)

        #triggering objs
        for obj in livingobjs:
            if(pygame.mouse.get_pressed()[0] and
                (obj.state == LSPBeat.STATE_WAITING or obj.state == LSPBeat.STATE_SPAWN)
                and obj.check_hit(mousehistory)):
                score = obj.trigger(gametime, mousehistory)
                particles.append(ScoreParticle(obj.x, obj.y, score))
                for i in range(10):
                    particles.append(SparksParticle(obj.x, obj.y, score))

        #removing objs
        i = 0
        while i < len(livingobjs):
            if (livingobjs[i].isdead):
                #print "removing obj"
                livingobjs.remove(livingobjs[i])
            else:
                i += 1

        #removing objs
        i = 0
        while i < len(particles):
            if (particles[i].grav.isdead):
                particles.remove(particles[i])
            else:
                i += 1

        #============== RENDER ==============

        screen.fill(BKG_COLOR)

        #render bkg img
        screen.blit(BACKGROUND,(0,0))

        #render objs
        for obj in livingobjs:
            obj.render(screen, gametime)

        #render particles
        for partic in particles:
            partic.render(screen)

        #render mouse "trails"
        i=0
        for pt in mousehistory:
            if(pygame.mouse.get_pressed()[0]):
                                pygame.gfxdraw.filled_circle(
                    screen,
                    pt[0],pt[1],
                    int(10.0*i/MOUSE_HISTORY_SIZE),
                    (255,255,0,255*(0.8*i/MOUSE_HISTORY_SIZE) ))
            else:
                pygame.gfxdraw.filled_circle(
                    screen,
                    pt[0],pt[1],
                    int(5.0*i/MOUSE_HISTORY_SIZE),
                    (255,255,255,255*(0.8*i/MOUSE_HISTORY_SIZE) ))
            i+=1

        #============== cap fps ==============
        temp = time.time();
        if(temp<lastup+framelapse):
            time.sleep( (lastup + framelapse) - temp)
            pass

        #blit screen
        pygame.display.flip()
        lastup = time.time()

def parse_map(filename):
    #Some constants we might look for
    headers = {'bpm': 0, 'offset': 0}
    #Ordered list (chronologically) of beat objects
    beats = []

    f = open(filename, 'r')
    for line in f:
        if not line.isspace() and not (line[0] == '#'):
            line = line.strip()
            if (line.startswith('FILE')):
                headers['filename'] = line.split()[1]
            elif (line.startswith('BPM')):
                headers['bpm'] = float(line.split()[1])
            elif (line.startswith('OFFSET')):
                headers['offset'] = float(line.split()[1])
            else:
                #REQUIRES BPM TO HAVE BEEN DEFINED BY THIS POINT
                if (line.startswith('g')):
                    #TODO: Create Beat objects
                    args = line.split(" ")
                    beat_time = float(args[1]) * 60/headers['bpm'] + headers['offset']
                    beats.append(LSPGate(beat_time, float(args[2]), float(args[3]), float(args[4])))

    return (headers, beats)


if __name__ == "__main__":
    screen = do_init()

    headers, beats = parse_map("./" + sys.argv[1] + ".lsp")

    pygame.mixer.init()
    s = pygame.mixer.Sound("./" + sys.argv[1] + ".ogg")
    s.set_volume(1.0)
    s.play()

    """
    fakelsps = [
            LSPGate(i*1, random.random(), random.random(), random.random()*math.pi*2) for i in range(40)
            ]
    """

    mainloop(screen, beats, None ,10);
