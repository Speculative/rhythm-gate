import pygame,math,time,sys,random

RESOLUTION_X = 1024
RESOLUTION_Y = 768

SPAWN_TIME = 0.25
DECAY_TIME = 0.25

MOUSE_HISTORY_SIZE =20

BKG_COLOR = (0x22,0x22,0x22)

class LSPBeat(object):

    STATE_SPAWN = 0
    STATE_WAITING = 1
    STATE_DYING = 2

    """
    Its basically abstract
    """
    def __init__(self, spawntime):
        self.spawntime = spawntime
        self.changetime = spawntime
        self.state = LSPBeat.STATE_SPAWN
        self.isdead = False

    """Takes in the current gametime (time of trigger)
    and returns the object.

    Enters this object into the despawn state, where the proper
    animations are carried out
    """
    def trigger(self, gametime, mousehistory):
        self.state = LSPBeat.STATE_DYING
        return abs(gametime - self.spawntime)

    def render(self, screen, gametime):
        if (self.state == LSPBeat.STATE_SPAWN):
            self.render_spawn(screen, gametime-self.changetime)
        elif (self.state == LSPBeat.STATE_WAITING):
            self.render_wait(screen, gametime-self.changetime)
        else:
            self.render_dying(screen, gametime-self.changetime)

    def update(self, gametime):
        if(self.state == LSPBeat.STATE_DYING and 
                self.changetime + DECAY_TIME >= gametime):
            this.isdead = True

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

        if(LSPGate.BLOCK_IMAGE == None):
            LSPGate.BLOCK_IMAGE = pygame.transform.rotozoom(pygame.image.load("./gate.png"),0,0.4)

        self.rendered = pygame.transform.rotate(
                LSPGate.BLOCK_IMAGE,
                math.degrees(angle))

    """Determines if pm lies on line segment defined by p1 and p2"""
    def on_segment(self, pm, p1, p2):
        xmin = min(p1[0], p2[0])
        ymin = min(p1[1], p2[1])
        xmax = max(p1[0], p2[0])
        ymax = max(p1[1], p2[1])
        return (xmin <= pm[0] <= xmax) and (ymin <= pm[1] <= ymax)


    def check_hit(self, mousehistory):
        poststep = mousehistory[-1]
        prestep = mousehistory[-2]

        """
        if(self.angle == 0):
            #vertical
            return ((poststep[0]-self.x)>0 and (prestep[0] - self.x<0) or
                (poststep[0]-self.x)<0 and (prestep[0] - self.x>0))
        else:
            dxpre = prestep[0]-self.x
            dxpost = poststep[0]-self.x

            #the y values of the line @ those points
            nypre = self.y + dxpre * math.atan(self.angle)
            nypost = self.y + dxpost * math.atan(self.angle)

            return (
                ((poststep[1]-nypost)>0 and (prestep[1] - nypre<0)) or
                ((poststep[1]-nypost)<0 and (prestep[1] - nypre>0))
                )
        """
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



    def trigger(self, gametime, mousehistory):
        self.breakspot = 0 #TODO mousehistory tracking


        if (mousehistory[-1][0] - mousehistory[-2][0]) != 0:
            attack_angle = math.atan(
                    (mousehistory[-1][1] - mousehistory[-2][1]) / 
                    (mousehistory[-1][0] - mousehistory[-2][0]))
        else:
            attack_angle = 0

        print attack_angle

        mult = attack_angle / 2*math.pi
        dtime = gametime - time.time()

        LSPBeat.trigger(self, gametime, mousehistory)


    def update(self, gametime):
        LSPBeat.update(self, gametime)

    def render_spawn(self, screen, elapsed):
        screen.blit(self.rendered, (
            self.x - self.rendered.get_width()/2,
            self.y - self.rendered.get_height()/2) );

    def render_wait(self, screen, elapsed):
        pass

    def render_dying(self, screen, elapsed):
        pass

class ScoreParticle(object):
    GRAVITY = 5
    MOM_INIT_Y = -5
    MOM_INIT_X = 5
    LIFETIME = 1

    def __init__(self, x, y, score):
        self.momentumy = ScoreParticle.MOM_INIT_Y
        self.momentumx = ScoreParticle.MOM_INIT_X * random.random() - ScoreParticle.MOM_INIT_X * random.random()
        self.initial = time.time()
        self.last = self.initial
        self.isdead=False

        self.elapsed = 0

        self.renderedText = 0;

    def update(self, gametime):
        elapsed = gametime - self.last
        self.momentumy += ScoreParticle.GRAVITY*elapsed
        self.y += self.momentumy
        self.x += self.momentumx

        self.elapsed = gametime - self.initial

        if(gametime - self.initial > LIFETIME):
            self.isdead=True

    def render(self, surface):
        pass

"""gets the display screen
"""
def do_init():
    pygame.init();
    pygame.display.set_caption("LSP")
    return pygame.display.set_mode((RESOLUTION_X, RESOLUTION_Y))


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

    print "starting (lapse = %s)"%(framelapse)

    while(True):
        gametime = time.time()
        elapsedTime = gametime - lastup

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        mousehistory.append(pygame.mouse.get_pos())
        mousehistory = mousehistory[1:]

        #add objs as they come up
        while(objptr < len(gameobjs) and 
                initial + gameobjs[objptr].spawntime >= gametime - SPAWN_TIME):
            print "spawning obj"
            livingobjs.append(gameobjs[objptr])
            objptr += 1

        #updating objs & particles
        for obj in livingobjs:
            obj.update(gametime)

        #triggering objs
        for obj in livingobjs:
            if(obj.state!=LSPBeat.STATE_DYING and obj.check_hit(mousehistory)):
                score = obj.trigger(gametime, mousehistory)
                particles.append(ScoreParticle(obj.x, obj.y, score))

        #removing objs
        i = 0
        while i < len(livingobjs):
            if (livingobjs[i].isdead):
                livingobjs.remove(i)
            else:
                i += 1

        #removing objs
        i = 0
        while i < len(particles):
            if (particles[i].isdead):
                particles.remove(i)
            else:
                i += 1

        screen.fill(BKG_COLOR)

        #render objs
        for obj in livingobjs:
            obj.render(screen, gametime)

        #render particles
        for partic in livingobjs:
            partic.render(screen, gametime)

        #cap fps 
        temp = time.time();
        if(temp>lastup+framelapse):
            time.sleep( (lastup + framelapse) - temp)

        #blit screen
        pygame.display.flip()
        lastup = time.time()

if __name__ == "__main__":
    screen = do_init()

    fakelsps = [
            LSPGate(0, 0.1, 0.7, 0),
            LSPGate(0, 0.4, 0.1, math.pi*0.1),
            LSPGate(0, 0.3, 0.2, math.pi*0.1),
            LSPGate(0, 0.5, 0.5, 1)
            ]

    mainloop(screen, fakelsps, None ,10);
