import pygame,math,time,sys,random,pygame.gfxdraw

RESOLUTION_X = 1024
RESOLUTION_Y = 400

SPAWN_TIME = 0.2
DECAY_TIME = 0.2

MOUSE_HISTORY_SIZE =100

BKG_COLOR = (45,17,44)

FONTU = None

scoreColors=[
    (239,67,57),
    (202,41,62),
    (202,41,62),
    (130,2,51),
    (83,0,49),
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

        else:
            self.render_dying(screen, gametime-self.changetime)

    def update(self, gametime):

        if(self.changetime == 0):
            self.changetime = gametime

        if(self.state == LSPBeat.STATE_SPAWN and 
            self.changetime + SPAWN_TIME <= gametime):
            self.changetime = gametime
            self.state = LSPBeat.STATE_WAITING

        if(self.state == LSPBeat.STATE_DYING and 
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
        self.roughrect = pygame.rect.Rect( (self.x-tem/2,self.y-tem/2,tem, tem) );

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
                m1 = (poststep[1] - prestep[1]) / (poststep[0] - prestep[0])
                y = prestep[1] + m1 * (g2[0] - prestep[0])
                return self.on_segment((g2[0], y), prestep, poststep) and self.on_segment((g2[0], y), g1, g2)

            elif (g2[0] == g1[0] and poststep[0] == prestep[0]):
                return False

            elif (g2[0] != g1[0] and poststep[0] != prestep[0]):
                m1 = (poststep[1] - prestep[1]) / (poststep[0] - prestep[0])
                m2 = (g2[1] - g1[1]) / (g2[0] - g1[0])
                
                if(m1 != m2):
                    x = (g2[1] - prestep[1] + m1 * prestep[0] - m2 * g2[0]) / (m1 - m2)
                    y = m2 * (x - g2[0]) + g2[1]

                    return self.on_segment((x, y), prestep, poststep) and self.on_segment((x, y), g1, g2)

                else:
                    return False


    def render_spawn(self, screen, elapsed):
        blit_alpha(screen, self.rendered, (
            self.x - self.rendered.get_width()/2 ,
            self.y - self.rendered.get_height()/2 
        ), int(255 * min(1.0, elapsed / DECAY_TIME)));
        

    def render_wait(self, screen, elapsed):
        screen.blit(self.rendered, (
            self.x - self.rendered.get_width()/2,
            self.y - self.rendered.get_height()/2) );


    def render_dying(self, screen, elapsed):
        blit_alpha(screen, self.rendered, (
            self.x - self.rendered.get_width()/2 ,
            self.y - self.rendered.get_height()/2 
        ), int(255 * (1.0-min(1.0, elapsed / DECAY_TIME)) ));

    def trigger(self, gametime, mousehistory):
        self.breakspot = 0 #TODO mousehistory tracking


        if (mousehistory[-1][0] - mousehistory[-2][0]) != 0:
            attack_angle = math.atan(
                    (mousehistory[-1][1] - mousehistory[-2][1]) / 
                    (mousehistory[-1][0] - mousehistory[-2][0]))
        else:
            attack_angle = 0

        #print attack_angle

        mult = attack_angle / 2*math.pi
        dtime = gametime - time.time()

        LSPBeat.trigger(self, gametime, mousehistory)

        return (1.0 - dtime/0.5)*(0.8 + 0.2*mult)

    def update(self, gametime):
        LSPBeat.update(self, gametime)


class ScoreParticle(object):
    GRAVITY = 0.1
    MOM_INIT_Y = -1
    MOM_INIT_X = 1
    LIFETIME = 1


    def __init__(self, x, y, score):
        self.momentumy = ScoreParticle.MOM_INIT_Y * random.random()
        self.momentumx = ScoreParticle.MOM_INIT_X * random.random() - ScoreParticle.MOM_INIT_X * random.random()
        self.initial = time.time()
        self.last = self.initial
        self.isdead=False
        self.x=x
        self.y=y

        self.elapsed = 0

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
        elapsed = gametime - self.last
        self.momentumy += ScoreParticle.GRAVITY*elapsed
        self.y += self.momentumy
        self.x += self.momentumx

        self.elapsed = gametime - self.initial

        if(gametime - self.initial > ScoreParticle.LIFETIME):
            self.isdead=True

    def render(self, surface):
        self.renderedtext.set_alpha(255 - 255.0*self.elapsed / ScoreParticle.LIFETIME);
        surface.blit(self.renderedtext,(self.x, self.y))

class SparksParticle(ScoreParticle):
    def __init__(self, x, y, score):
        self.momentumy = ScoreParticle.MOM_INIT_Y * random.random()
        self.momentumx = ScoreParticle.MOM_INIT_X * random.random() - ScoreParticle.MOM_INIT_X * random.random()
        self.initial = time.time()
        self.last = self.initial
        self.isdead=False
        self.x=x
        self.y=y

        self.elapsed = 0


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
        elapsed = gametime - self.last
        self.momentumy += ScoreParticle.GRAVITY*elapsed
        self.y += self.momentumy
        self.x += self.momentumx

        self.elapsed = gametime - self.initial

        if(gametime - self.initial > ScoreParticle.LIFETIME):
            self.isdead=True

    def render(self, surface):
        pygame.gfxdraw.filled_circle(surface, int(self.x), int(self.y),
                int(1.0 * self.elapsed / ScoreParticle.LIFETIME * 5), (255,255,255))

"""gets the display screen
"""
def do_init():
    global FONTU
    pygame.init();
    pygame.display.set_caption("LSP")
    screen = pygame.display.set_mode((RESOLUTION_X, RESOLUTION_Y))

    pygame.mouse.set_visible(False)
    FONTU = pygame.font.Font("./wire1.ttf", 28);

    ScoreParticle.FONTU_BEST = FONTU.render("PERFECT!", False, scoreColors[0]);
    ScoreParticle.FONTU_EH = FONTU.render("GOOD!", False, scoreColors[1]);
    ScoreParticle.FONTU_GOOD = FONTU.render("OKAY", False, scoreColors[2]);
    ScoreParticle.FONTU_OH = FONTU.render("NOT GREAT", False, scoreColors[3]);
    ScoreParticle.FONTU_WORST = FONTU.render("KILL YOURSELF", False, scoreColors[4]);


    if(LSPGate.BLOCK_IMAGE == None):
        LSPGate.BLOCK_IMAGE = pygame.transform.rotozoom(pygame.image.load("./gate.png"),0,0.4)
        LSPGate.BLOCK_IMAGE = LSPGate.BLOCK_IMAGE.convert_alpha(screen)

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
                initial + gameobjs[objptr].spawntime <= gametime - SPAWN_TIME):
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
            if(pygame.mouse.get_pressed()[0] and obj.state == LSPBeat.STATE_WAITING and obj.check_hit(mousehistory)):
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
            if (particles[i].isdead):
                particles.remove(particles[i])
            else:
                i += 1

        #============== RENDER ==============

        screen.fill(BKG_COLOR)

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
        if(temp>lastup+framelapse):
            time.sleep( (lastup + framelapse) - temp)
            pass

        #blit screen
        pygame.display.flip()
        lastup = time.time()

if __name__ == "__main__":
    screen = do_init()


    fakelsps = [
            LSPGate(i*1, random.random(), random.random(), random.random()*math.pi*2) for i in range(40)
            ]

    mainloop(screen, fakelsps, None ,10);
