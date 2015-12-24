import select
import socket
import json
import time
import random
import sdl2
import sdl2.ext

class Inform:
	def __init__(self, txt):
		self.count = 30
		self.info = txt
		
class Player:
	def __init__(self, trn):
		self.ID = -1
		self.x = 0
		self.y = 350
		self.r = 0
		self.u = 0
		self.h = 2
		self.w = 0
		self.cam = 0
		self.inc = 0
		self.ground = True
		self.wall = False
		self.score = trn
		self.hurry = 120.0
		self.moving = [0,0]
		self.picfrm = 0
		self.info = []
		self.run = False
		self.speed = 1.0
		self.name = ""
		self.LRT = time.time()

def inrange(a, mina, maxa):
	out = a
	
	if a <= mina:
		out = mina
	if a >= maxa:
		out = maxa
	
	return out

def run():
	sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
	sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
	if sdl2.SDL_NumJoysticks() <= 0:
		print("No Joysticks found")
	else:
		print("Found Joystick")
		joy = sdl2.SDL_JoystickOpen(0)
	
	myname = input("Your Name: ")
	
	win = sdl2.ext.Window("Jump N Run", size=(800,500), flags=sdl2.SDL_WINDOW_SHOWN)
	win.refresh()
	
	ren = sdl2.ext.Renderer(win)
	factory = sdl2.ext.SpriteFactory(renderer=ren)
	sprite_back = factory.from_image("back.png")
	sprite_front = factory.from_image("front.png")
	sprite_player_r = [factory.from_image("player_r1.png"), factory.from_image("player_r2.png"), factory.from_image("player_r1.png"), factory.from_image("player_r3.png")]
	sprite_player_l = [factory.from_image("player_l1.png"), factory.from_image("player_l2.png"), factory.from_image("player_l1.png"), factory.from_image("player_l3.png")]
	sprite_coin = factory.from_image("coin32.png")
	cx = 0
	sprite_trap = factory.from_image("trap.png")
	font = sdl2.ext.FontManager(font_path="OpenSans-Italic.ttf", size=20, color=(0,0,0))
	fontbg = sdl2.ext.FontManager(font_path="OpenSans-Italic.ttf", size=80, color=(0,0,0))
	
	en = []
	serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
	transcore = 0
	record = 0
	ingame = False
	level = 1
	isrunnin = True
	while isrunnin:
		p = Player(transcore)
		lk = False
		rk = False
		
		coins_gold = []
		coins_silver = []			
		coins_low = []
		traps = []

		checkpoint = 3000 + (500 * level)
		checks = []
		x = checkpoint
		checks.append(x)
		for i in range(6):
			x *= 1.5
			checks.append(int(x))
		
		numchecks = 0
		
		sendit = 0
		negtime = 0
		locktime = 4
		endtime = time.time()
		drawit = True
		endit = False
		while isrunnin:
			endtime += 0.03
			
			if ingame:
				outrc = {"act": "pos", "x": p.x, "y": p.y, "r": p.r, "u": p.u, "s": p.speed, "dir": p.moving[0], "mov": p.moving[1], "lvl": level, "score": p.score, "name": myname + " (" + str(p.score) + ")"}
			else:
				outrc = {"act": "wait", "x": p.x, "y": p.y, "r": p.r, "u": p.u, "s": p.speed, "dir": p.moving[0], "mov": p.moving[1], "lvl": level, "score": p.score, "name": myname}
			try:
				if sendit <= 0:
					sendit = 3
					serv.sendto(json.dumps(outrc).encode(), ('78.47.41.154', 6444))
				else:
					sendit -= 1
			except:
				pass
			
			if drawit:
				xx = int(p.cam/2)%800
				ren.copy(sprite_back, srcrect=(xx, 0, 800, 500))
				
				ren.fill((0,30,800,31), color=(0,0,0))
				
				for s in en:
					x2 = int(s.x/87.5)
					y2 = int(s.y/16.66) + 30
					ren.draw_line((x2,y2,x2,y2+6), color=(50,250,0))

					if s.x - p.cam >= 0 and s.x - p.cam <= 800:
						if s.moving[0] == 0:
							ren.copy(sprite_player_r[s.moving[1]], dstrect=(int(s.x - p.cam), int(s.y), 40, 100))
						else:
							ren.copy(sprite_player_l[s.moving[1]], dstrect=(int(s.x - p.cam), int(s.y), 40, 100))
						
						tnt = factory.from_text("<" + s.name + ">", fontmanager=font)
						nx = int(s.x - p.cam) - int(tnt.size[0] / 2) + 20
						ny = int(s.y - tnt.size[1])
						ren.copy(tnt, dstrect=(nx, ny, tnt.size[0], tnt.size[1]))
				
				x2 = int(p.x/87.5)
				y2 = int(p.y/16.66) + 30
				ren.draw_line((x2,y2,x2,y2+6), color=(50,250,0))

				if p.moving[0] == 0:
					ren.copy(sprite_player_r[p.moving[1]], dstrect=(int(p.x - p.cam), int(p.y), 40, 100))
				else:
					ren.copy(sprite_player_l[p.moving[1]], dstrect=(int(p.x - p.cam), int(p.y), 40, 100))
				
				if p.ground and p.r != 0:
					if p.r > 0:
						p.moving[0] = 0
					else:
						p.moving[0] = 1
					p.picfrm += 1
					if p.picfrm >= 3:
						p.picfrm = 0
						p.moving[1] += 1
						if p.moving[1] >= 4:
							p.moving[1] = 0
				else:
					p.picfrm = 0
					p.moving[1] = 0
				
				for i in coins_gold:
					x = i - p.cam
					x2 = int(i/87.5)
					ren.draw_point((x2,39), color=(255,255,0))
					if x >= 0 and x <= 800:
						ren.copy(sprite_coin, srcrect=(int(cx), 0, 32, 32), dstrect=(int(x), 150, 30, 30))
						if (p.x - p.cam) <= (x + 30) and (p.x - p.cam) >= (x - 40) and p.y <= 180 and p.y >= 50:
							p.score += 100
							coins_gold.remove(i)
							p.info.append(Inform("score +100"))
						for s in en:
							if (s.x - p.cam) <= (x + 30) and (s.x - p.cam) >= (x - 40) and s.y <= 180 and s.y >= 50:
								coins_gold.remove(i)
						
				for i in coins_silver:
					x = i - p.cam
					x2 = int(i/87.5)
					ren.draw_point((x2,43), color=(255,255,0))
					if x >= 0 and x <= 800:
						ren.copy(sprite_coin, srcrect=(int(cx), 0, 32, 32), dstrect=(int(x), 210, 30, 30))
						if (p.x - p.cam) <= (x + 30) and (p.x - p.cam) >= (x - 40) and p.y <= 240 and p.y >= 110:
							p.score += 25
							coins_silver.remove(i)
							p.info.append(Inform("score +25"))
						for s in en:
							if (s.x - p.cam) <= (x + 30) and (s.x - p.cam) >= (x - 40) and s.y <= 240 and s.y >= 110:
								coins_silver.remove(i)

				for i in coins_low:
					x = i - p.cam
					x2 = int(i/87.5)
					ren.draw_point((x2,47), color=(255,255,0))
					if x >= 0 and x <= 800:
						ren.copy(sprite_coin, srcrect=(int(cx), 0, 32, 32), dstrect=(int(x), 280, 30, 30))
						if (p.x - p.cam) <= (x + 30) and (p.x - p.cam) >= (x - 40) and p.y <= 310 and p.y >= 180:
							p.score += 1
							coins_low.remove(i)
						for s in en:
							if (s.x - p.cam) <= (x + 30) and (s.x - p.cam) >= (x - 40) and s.y <= 310 and s.y >= 180:
								coins_low.remove(i)

				for i in traps:
					x = i - p.cam
					x2 = int(i/87.5)
					ren.draw_point((x2,60), color=(180,180,180))
					if x >= 0 and x <= 800:
						ren.copy(sprite_trap, dstrect=(int(x), 440, 40, 10))
						if (p.x - p.cam) <= (x + 40) and (p.x - p.cam) >= (x - 40) and p.y <= 350 and p.y >= 340:
							p.hurry -= 15.0
							traps.remove(i)
							p.info.append(Inform("time -15"))
						for s in en:
							if (s.x - p.cam) <= (x + 40) and (s.x - p.cam) >= (x - 40) and s.y <= 350 and s.y >= 340:
								traps.remove(i)
				
				x = checkpoint - p.cam
				if x >= 0 and x <= 800:
					ren.draw_line((int(x),0,int(x),500), color=(0,0,0))

				leader = myname + " (" + str(p.score) + ")"
				maxscr = p.score
				for s in en:
					if s.score > maxscr:
						maxscr = s.score
						leader = s.name
				
				txt = factory.from_text(myname + ":: Score: " + str(p.score) + " ... Time: " + str(round(p.hurry - negtime)) + " ... Checkpoints: " + str(numchecks) + " ... Level: " + str(level) + " ....... Leader: " + leader, fontmanager=font)
				ren.copy(txt, dstrect=(0,0,txt.size[0],txt.size[1]))
				
				for i in checks:
					ren.draw_line((int(i/87.5),30,int(i/87.5),60), color=(200,200,200))
				
				cx += 32
				if cx >= 1950:
					cx = 0
				
				for nfo in p.info:
					if nfo.count > 0:
						nfo.count -= 1
					tyxt = factory.from_text(nfo.info, fontmanager=fontbg)
					ren.copy(tyxt, dstrect=(300+((30-nfo.count)*3),200+((30-nfo.count)*2),200-((30-nfo.count)*4),100-((30-nfo.count)*6)))
					if nfo.count <= 0:
						p.info.remove(nfo)
				
				xx = int(p.cam*2)%1600
				ren.copy(sprite_front, srcrect=(xx, 0, 800, 500))

				ren.present()
				win.refresh()

			drawit = True

			for e in sdl2.ext.get_events():
				if e.type == sdl2.SDL_JOYAXISMOTION:
					if e.jaxis.axis == 0:
						if e.jaxis.value <= -16000:
							lk = True
							ingame = True
						elif e.jaxis.value >= 16000:
							rk = True
							ingame = True
						elif e.jaxis.value >= -16000 and e.jaxis.value <= 16000:
							lk = False
							rk = False
				
				elif e.type == sdl2.SDL_JOYBUTTONDOWN or e.type == sdl2.SDL_JOYBUTTONUP:
					if e.jbutton.button == 0:
						isrunnin = False
						break
					
					elif e.jbutton.button == 1 and e.jbutton.state == 1:
						if p.ground:
							p.ground = False
							p.u = -5.0 * p.h
						if p.wall:
							p.u = -5.0 * p.h
							p.r = 0 - p.r

					elif e.jbutton.button == 4:
						if e.jbutton.state == 1:
							p.run = True
						else:
							p.run = False

				elif e.type == sdl2.SDL_KEYDOWN:
					if e.key.keysym.sym == sdl2.SDLK_a:
						lk = True
						ingame = True
					elif e.key.keysym.sym == sdl2.SDLK_d:
						rk = True
						ingame = True
					elif e.key.keysym.sym == sdl2.SDLK_w:
						if p.ground:
							p.ground = False
							p.u = -5.0 * p.h
						if p.wall:
							p.u = -5.0 * p.h
							p.r = 0 - p.r
					elif e.key.keysym.sym == sdl2.SDLK_m:
						p.run = True
				
				elif e.type == sdl2.SDL_KEYUP:
					if e.key.keysym.sym == sdl2.SDLK_a:
						lk = False
					elif e.key.keysym.sym == sdl2.SDLK_d:
						rk = False
					elif e.key.keysym.sym == sdl2.SDLK_m:
						p.run = False
				
				elif e.type == sdl2.SDL_QUIT:
					isrunnin = False
					break
			
			p.w = 0
			if lk:
				p.w -= 5
			if rk:
				p.w += 5
			
			if p.ground:
				p.r = p.w
				if p.run:
					p.speed += 0.05
					if p.speed >= 2.0:
						p.speed = 2.0
				else:
					p.speed -= 0.1
					if p.speed <= 1.0:
						p.speed = 1.0
			else:
				if p.r == 5 and p.w == -5:
					p.r = 3
				elif p.r == -5 and p.w == 5:
					p.r = -3

			p.u += 0.5
			if ingame:
				p.x = inrange(p.x + (p.r*p.speed), p.cam, 70000)
				p.y = inrange(p.y + p.u, 0, 350)
			if p.y == 350:
				p.ground = True
				p.u = 0
			
			for s in en:
				s.u += 0.5
				s.x = s.x + (s.r*s.speed)
				s.y = inrange(s.y + s.u, 0, 350)
				if s.r != 0:
					s.picfrm += 1
					if s.picfrm >= 3:
						s.picfrm = 0
						s.moving[1] += 1
						if s.moving[1] >= 4:
							s.moving[1] = 0
			
			p.wall = False
			if (p.x - p.cam) <= 0 and p.r == -5:
				p.wall = True
			
			p.inc = (p.x - p.cam) / 65.0
			
			p.cam += p.inc
			if p.inc > 0:
				p.inc -= 1.5
			
			if p.x >= checkpoint:
				checkpoint *= 1.5
				p.hurry += 20.0
				numchecks += 1
				if numchecks >= 7:
					transcore = p.score + (100 * level)
					level += 1
					ingame = False
					break
				p.info.append(Inform("time +20"))

			if (p.hurry - negtime) <= 0.0:
				return

			while True:
				r, w, x = select.select([serv], [], [], 0)
				
				if not r:
					break
				
				else:
					try:
						data, addr = serv.recvfrom(2000)
						inrc = json.loads(data.decode("utf-8"))
						if inrc['act'] == "pos":
							newone = True
							for s in en:
								if s.ID == inrc['ID']:
									s.LRT = time.time()
									s.x = inrc['x']
									s.y = inrc['y']
									s.r = inrc['r']
									s.u = inrc['u']
									s.speed = inrc['s']
									s.moving[0] = inrc['dir']
									s.moving[1] = inrc['mov']
									s.name = inrc['name']
									s.score = inrc['score']
									if inrc['lvl'] > level:
										level = inrc['lvl']
										transcore = p.score
										endit = True
									newone = False
									break
							if newone:
								nen = Player(0)
								nen.ID = inrc['ID']
								en.append(nen)
						
						elif inrc['act'] == "cont":
							coins_gold.append(inrc['cogo'])
							coins_silver.append(inrc['cosi'])
							coins_low.append(inrc['colo'])
							traps.append(inrc['trap'])
						
						elif inrc['act'] == "time":
							if locktime > 0:
								locktime -= 1
							else:
								negtime = inrc['time']
					
					except:
						pass
			
			if endit:
				break

			for s in en:
				if time.time() - s.LRT >= 5.0:
					en.remove(s)
					del(s)

			difftime = endtime - time.time()
			if difftime > 0.01:
				time.sleep(difftime)
			else:
				drawit = False

if __name__ == '__main__':
	sdl2.ext.init()
	run()
	sdl2.ext.quit()
