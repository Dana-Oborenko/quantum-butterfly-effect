import pygame, random, sys
pygame.init()
WIDTH, HEIGHT = 1280, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Quantum Butterfly Effect FINAL V4')
clock = pygame.time.Clock()

BG=(8,12,24); PANEL=(22,28,46); CARD=(30,36,60)
WHITE=(240,245,255); GRAY=(170,185,210)
CYAN=(0,220,255); BLUE=(80,130,255); GREEN=(70,220,140)
YELLOW=(255,205,80); RED=(255,95,95); PURPLE=(170,110,255)

f1=pygame.font.SysFont('arial',40,True)
f2=pygame.font.SysFont('arial',28,True)
f3=pygame.font.SysFont('arial',22)
f4=pygame.font.SysFont('arial',18)

MENU='menu'; COUNTRY='country'; PLAY='play'; EVENT='event'; TECH='tech'; END='end'
state=MENU

country=''
year=1; MAX_YEAR=10; POINTS=10
stats={k:50 for k in ['Environment','Education','Health','Economy','Stability']}
alloc={k:0 for k in stats}
approval=60
collapsed=False
rewind_used=False
history=None
future_cards=[]
news=['World initialized.']
message='Allocate all 10 points.'
last_event=''
end_title=''; end_text=''
ach=[]

start_btn=pygame.Rect(500,620,280,60)
restart_btn=pygame.Rect(500,680,280,55)
observe_btn=pygame.Rect(980,710,220,55)
next_btn=pygame.Rect(980,710,220,55)
rewind_btn=pygame.Rect(730,710,220,55)
country_btns=[pygame.Rect(170+i*280,300,220,80) for i in range(4)]
choice_rects=[pygame.Rect(390,500,500,50),pygame.Rect(390,570,500,50),pygame.Rect(390,640,500,50)]
tech_rects=[pygame.Rect(260,300,320,70),pygame.Rect(700,300,320,70)]
plus_minus=[]
event_title=''; event_desc=''; event_choices=[]


def txt(t,f,c,x,y): screen.blit(f.render(t,True,c),(x,y))
def clamp(v): return max(0,min(100,v))
def remain(): return POINTS-sum(alloc.values())
def button(r,t,m,col=BLUE):
 c=CYAN if r.collidepoint(m) else col
 pygame.draw.rect(screen,c,r,border_radius=10)
 pygame.draw.rect(screen,WHITE,r,2,border_radius=10)
 ts=f3.render(t,True,WHITE)
 screen.blit(ts,ts.get_rect(center=r.center))
def bar(x,y,v):
 pygame.draw.rect(screen,(40,45,65),(x,y,250,18),border_radius=8)
 c=GREEN if v>=70 else YELLOW if v>=40 else RED
 pygame.draw.rect(screen,c,(x,y,int(v*2.5),18),border_radius=8)
def wrap(s,n):
 w=s.split(); r=[]; cur=''
 for a in w:
  if len(cur+a)<n: cur+=a+' '
  else: r.append(cur); cur=a+' '
 r.append(cur); return r

def set_country(i):
 global country,stats,approval,state,news
 opts=['Developed Nation','Island State','Tech Superpower','Developing Nation']
 country=opts[i]
 if i==0: stats['Economy']=65; stats['Education']=65; stats['Environment']=40
 if i==1: stats['Environment']=70; stats['Economy']=35
 if i==2: stats['Economy']=70; stats['Education']=75; stats['Stability']=40
 if i==3: stats['Stability']=65; stats['Health']=40
 news=[country+' selected.']
 state=PLAY

def futures():
 e=alloc['Environment']; d=alloc['Education']; h=alloc['Health']; ec=alloc['Economy']; s=alloc['Stability']
 arr=[
 {'title':'Green Recovery','weight':20+e*4+d*2,'color':GREEN,'effects':{'Environment':10,'Education':4,'Health':3,'Economy':1,'Stability':3}},
 {'title':'Economic Boom','weight':20+ec*4+s*2,'color':YELLOW,'effects':{'Environment':-5,'Economy':10,'Stability':2,'Education':1}},
 {'title':'Social Strain','weight':20+(10-h)*3+(10-s)*3,'color':RED,'effects':{'Health':-8,'Economy':-4,'Stability':-10}}]
 tot=sum(i['weight'] for i in arr)
 for i in arr: i['prob']=round(i['weight']/tot*100)
 return arr

def trigger_event():
 global state,event_title,event_desc,event_choices,last_event
 state=EVENT
 ev=[('Pandemic','Hospitals overloaded.', [('Lockdown',{'Health':8,'Economy':-6}),('Balanced',{'Health':4,'Economy':-2}),('Open',{'Health':-6,'Economy':5})]),('Floods','Cities under water.', [('Green Aid',{'Environment':6}),('Relief',{'Stability':3}),('Ignore',{'Approval':-6})]),('Scandal','Trust collapsing.', [('Reform',{'Stability':7}),('Control',{'Approval':2}),('Nothing',{'Approval':-8})])]
 av=[x for x in ev if x[0]!=last_event]
 ch=random.choice(av); last_event=ch[0]; event_title,event_desc,event_choices=ch

def apply_choice(i):
 global state,approval
 for k,v in event_choices[i][1].items():
  if k=='Approval': approval+=v
  else: stats[k]+=v
 approval=clamp(approval)
 for k in stats: stats[k]=clamp(stats[k])
 news.append(event_title+' handled.')
 state=PLAY

def apply_future(f):
 global collapsed,history,message,state
 history={'year':year,'stats':stats.copy(),'approval':approval,'alloc':alloc.copy(),'news':news.copy()}
 for k,v in f['effects'].items(): stats[k]=clamp(stats[k]+v)
 if random.random()<0.55: trigger_event()
 collapsed=True; message='Reality collapsed into '+f['title']
 if year in [3,6,8] and stats['Education']>=65: state=TECH

def next_year():
 global year,collapsed,future_cards,message,state,end_title,end_text
 year+=1
 if year in [4,8] and approval<40:
  end_title='LOST ELECTION'; end_text='Citizens voted you out.'; state=END; return
 for k in alloc: alloc[k]=0
 collapsed=False; future_cards=futures(); message='Allocate all 10 points.'
 if year>MAX_YEAR:
  finish()

def finish():
 global state,end_title,end_text,ach
 avg=sum(stats.values())/5
 if avg>75: end_title='SUSTAINABLE GOLDEN AGE'; ach.append('Green Savior')
 elif stats['Economy']>85: end_title='CORPORATE DYSTOPIA'; ach.append('Economic Titan')
 else: end_title='UNCERTAIN FUTURE'
 end_text='Final world assessment complete.'
 if not rewind_used: ach.append('Timeline Master')
 state=END

def draw_menu(m):
 screen.fill(BG)
 txt('QUANTUM BUTTERFLY EFFECT',f1,CYAN,280,180)
 txt('FINAL V4 EDITION',f2,WHITE,470,260)
 button(start_btn,'START',m)

def draw_country(m):
 screen.fill(BG)
 txt('SELECT STARTING NATION',f1,CYAN,320,170)
 names=['Developed','Island','Tech Power','Developing']
 cols=[BLUE,GREEN,PURPLE,YELLOW]
 for i,r in enumerate(country_btns): button(r,names[i],m,cols[i])

def draw_play(m):
 screen.fill(BG)
 txt(country,f3,PURPLE,20,10)
 txt('Year '+str(year)+'/10',f2,WHITE,20,40)
 txt('Approval '+str(approval),f2,WHITE,980,30)
 txt('Points '+str(remain()),f2,WHITE,1020,70)
 pygame.draw.rect(screen,PANEL,(20,120,430,650),border_radius=14)
 y=160; plus_minus.clear()
 for s in stats:
  txt(s,f2,WHITE,40,y); txt(str(stats[s]),f3,GRAY,320,y); bar(40,y+35,stats[s])
  m1=pygame.Rect(320,y+28,35,30); p1=pygame.Rect(365,y+28,35,30)
  plus_minus.append((s,'-',m1)); plus_minus.append((s,'+',p1))
  button(m1,'-',m); button(p1,'+',m)
  y+=110
 pygame.draw.rect(screen,PANEL,(480,120,480,260),border_radius=14)
 txt('Choose carefully: each future has risks.',f4,GRAY,500,165)
 txt('Quantum Futures',f2,CYAN,500,140)
 for i,f in enumerate(future_cards):
  x=500+i*155
  pygame.draw.rect(screen,CARD,(x,190,145,150),border_radius=10)
  pygame.draw.rect(screen,f['color'],(x,190,145,150),2,border_radius=10)
  txt(f['title'][:12],f4,f['color'],x+8,220); txt(str(f['prob'])+'%',f2,WHITE,x+8,260)
 pygame.draw.rect(screen,PANEL,(980,120,260,250),border_radius=12)
 txt('HOW TO PLAY',f2,CYAN,1035,140)
 txt('1. Spend all 10 points',f4,WHITE,995,185)
 txt('2. Observe one future',f4,WHITE,995,215)
 txt('3. Handle world events',f4,WHITE,995,245)
 txt('4. Win elections',f4,WHITE,995,275)
 txt('5. Survive to Year 10',f4,WHITE,995,305)
 txt('ADVISORS',f2,CYAN,1060,345)
 tips=['Scientist: env matters','Economist: growth needed','Public: approval matters']
 yy=390
 for t in tips: txt(t,f4,WHITE,995,yy); yy+=34
 pygame.draw.rect(screen,PANEL,(480,410,770,360),border_radius=14)
 txt('News Feed',f2,CYAN,500,430)
 txt('Hint: Balance all systems for best ending.',f4,PURPLE,760,430)
 yy=470
 for n in news[-8:]: txt('- '+n,f4,WHITE,500,yy); yy+=28
 if approval < 45:
  txt('Low approval!',f4,RED,980,640)
 if year in [3,7]:
  txt('Election next year',f4,YELLOW,980,665)
 if stats['Stability'] < 35:
  txt('Stability critical',f4,RED,980,690)
 if not collapsed: button(observe_btn,'OBSERVE',m)
 else: button(next_btn,'NEXT YEAR',m)
 if history and not rewind_used: button(rewind_btn,'REWIND',m,PURPLE)

def draw_event(m):
 screen.fill(BG)
 pygame.draw.rect(screen,PANEL,(250,140,780,560),border_radius=18)
 txt('GLOBAL EVENT',f2,RED,520,180)
 txt(event_title,f1,CYAN,450,240)
 txt(event_desc,f3,WHITE,430,330)
 cols=[GREEN,YELLOW,RED]
 for i,r in enumerate(choice_rects): button(r,event_choices[i][0],m,cols[i])

def draw_tech(m):
 screen.fill(BG)
 txt('TECHNOLOGY UNLOCKED',f1,CYAN,340,180)
 button(tech_rects[0],'Green Fusion',m,GREEN)
 button(tech_rects[1],'AI Governance',m,PURPLE)
 txt('Choose one national technology.',f3,WHITE,430,450)

def draw_end(m):
 screen.fill(BG)
 txt('FINAL OUTCOME',f1,CYAN,420,120)
 txt(end_title,f2,WHITE,420,240)
 txt(end_text,f3,GRAY,430,320)
 yy=420
 for a in ach: txt('Achievement: '+a,f4,YELLOW,430,yy); yy+=30
 button(restart_btn,'RESTART',m)

future_cards=futures()
run=True
while run:
 m=pygame.mouse.get_pos()
 for e in pygame.event.get():
  if e.type==pygame.QUIT: run=False
  if e.type==pygame.MOUSEBUTTONDOWN:
   if state==MENU and start_btn.collidepoint(e.pos): state=COUNTRY
   elif state==COUNTRY:
    for i,r in enumerate(country_btns):
      if r.collidepoint(e.pos): set_country(i); future_cards=futures()
   elif state==PLAY:
    for s,a,r in plus_minus:
      if r.collidepoint(e.pos):
       if a=='+' and remain()>0: alloc[s]+=1
       if a=='-' and alloc[s]>0: alloc[s]-=1
       future_cards=futures()
    if history and not rewind_used and rewind_btn.collidepoint(e.pos):
      year=history['year']; stats=history['stats'].copy(); approval=history['approval']; alloc=history['alloc'].copy(); news=history['news'].copy(); collapsed=False; rewind_used=True; future_cards=futures()
    elif not collapsed and observe_btn.collidepoint(e.pos) and remain()==0:
      pick=random.choices(future_cards,weights=[x['weight'] for x in future_cards],k=1)[0]; apply_future(pick)
    elif collapsed and next_btn.collidepoint(e.pos): next_year()
   elif state==EVENT:
    for i,r in enumerate(choice_rects):
      if r.collidepoint(e.pos): apply_choice(i)
   elif state==TECH:
    if tech_rects[0].collidepoint(e.pos): stats['Environment']=clamp(stats['Environment']+10); stats['Economy']=clamp(stats['Economy']+5); news.append('Green Fusion deployed.'); state=PLAY
    if tech_rects[1].collidepoint(e.pos): stats['Economy']=clamp(stats['Economy']+12); stats['Stability']=clamp(stats['Stability']-6); news.append('AI Governance activated.'); state=PLAY
   elif state==END and restart_btn.collidepoint(e.pos):
    country=''; year=1; approval=60; collapsed=False; rewind_used=False; history=None; stats={k:50 for k in stats}; alloc={k:0 for k in stats}; news=['World initialized.']; ach=[]; future_cards=futures(); state=MENU
 if state==MENU: draw_menu(m)
 elif state==COUNTRY: draw_country(m)
 elif state==PLAY: draw_play(m)
 elif state==EVENT: draw_event(m)
 elif state==TECH: draw_tech(m)
 elif state==END: draw_end(m)
 pygame.display.flip(); clock.tick(60)
pygame.quit(); sys.exit()
