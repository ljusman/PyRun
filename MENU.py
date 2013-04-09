'''
@author: avalanchy (at) google mail dot com
@version: 0.1; python 2.7; pygame 1.9.2pre; SDL 1.2.14; MS Windows XP SP3
@date: 2012-04-08
@license: This document is under GNU GPL v3

README on the bottom of document.

@font: from http://www.dafont.com/coders-crux.font
      more abuot license you can find in data/coders-crux/license.txt
'''

import random, copy, os, pygame, sys, tiledtmxloader
from pygame.locals import *

if not pygame.display.get_init():
    pygame.display.init()

if not pygame.font.get_init():
    pygame.font.init()

BRIGHTBLUE  = (  0, 150, 255)

class Menu:
    lista = []
    pola = []
    Font_Size = 32
    font = pygame.font.Font
    dest_surface = pygame.Surface
    ilosc_pol = 0
    Heading_Brackground = (0,255,255)
    Letter_color =  (255, 255, 153)
    Highlight_color = (0,255,255)
    Highlight_Start_Pos = 0
    pozycja_wklejenia = (0,0)
    menu_width = 0
    menu_height = 0

    class Pole:
        tekst = ''
        pole = pygame.Surface
        pole_rect = pygame.Rect
        zaznaczenie_rect = pygame.Rect

    def move_menu(self, top, left):
        self.pozycja_wklejenia = (top,left) 

    def set_colors(self, text, selection, background):
        self.Heading_Brackground = background
        self.Letter_color =  text
        self.Highlight_color = selection
        
    def set_fontsize(self,font_size):
        self.Font_Size = font_size
        
    def get_position(self):
        return self.Highlight_Start_Pos
    
    def init(self, lista, dest_surface):
        self.lista = lista
        self.dest_surface = dest_surface
        self.ilosc_pol = len(self.lista)
        self.stworz_strukture()        
        
    def draw(self,przesun=0):
        if przesun:
            self.Highlight_Start_Pos += przesun 
            if self.Highlight_Start_Pos == -1:
                self.Highlight_Start_Pos = self.ilosc_pol - 1
            self.Highlight_Start_Pos %= self.ilosc_pol
        menu = pygame.Surface((self.menu_width, self.menu_height))
        menu.fill(self.Heading_Brackground)
        zaznaczenie_rect = self.pola[self.Highlight_Start_Pos].zaznaczenie_rect
        pygame.draw.rect(menu,self.Highlight_color,zaznaczenie_rect)

        for i in xrange(self.ilosc_pol):
            menu.blit(self.pola[i].pole,self.pola[i].pole_rect)
        self.dest_surface.blit(menu,self.pozycja_wklejenia)
        return self.Highlight_Start_Pos

    def stworz_strukture(self):
        przesuniecie = 0
        self.menu_height = 0
        self.font = pygame.font.Font('freesansbold.ttf' , self.Font_Size)
        for i in xrange(self.ilosc_pol):
            self.pola.append(self.Pole())
            self.pola[i].tekst = self.lista[i]
            self.pola[i].pole = self.font.render(self.pola[i].tekst, 1, self.Letter_color)

            self.pola[i].pole_rect = self.pola[i].pole.get_rect()
            przesuniecie = int(self.Font_Size * 0.2)

            height = self.pola[i].pole_rect.height
            self.pola[i].pole_rect.left = przesuniecie
            self.pola[i].pole_rect.top = przesuniecie+(przesuniecie*2+height)*i

            width = self.pola[i].pole_rect.width+przesuniecie*2
            height = self.pola[i].pole_rect.height+przesuniecie*2            
            left = self.pola[i].pole_rect.left-przesuniecie
            top = self.pola[i].pole_rect.top-przesuniecie

            self.pola[i].zaznaczenie_rect = (left,top ,width, height)
            if width > self.menu_width:
                    self.menu_width = width
            self.menu_height += height
        x = self.dest_surface.get_rect().centerx - self.menu_width / 2
        y = self.dest_surface.get_rect().centery - self.menu_height / 2
        mx, my = self.pozycja_wklejenia
        self.pozycja_wklejenia = (x+mx, y+my)



''' For testing:
    surface = pygame.display.set_mode((800,600)) #0,6671875 and 0,(6) of HD resoultion
    yellow = pygame.image.load('Yellow.jpg').convert()
    surface.blit(yellow, (0,0)) # BackGround Color

'''

'''First you have to make an object of a *Menu class.
    *init take 2 arguments. List of fields and destination surface.
    Then you have a 4 configuration options:
    *set_colors will set colors of menu (text, selection, background)
    *set_fontsize will set size of font.
    *set_font take a path to font you choose.
    *move_menu is quite interseting. It is only option which you can use before 
    and after *init statement. When you use it before you will move menu from 
    center of your surface. When you use it after it will set constant coordinates. 
    Uncomment every one and check what is result!
    *draw will blit menu on the surface. Be carefull better set only -1 and 1 
    arguments to move selection or nothing. This function will return actual 
    position of selection.
    *get_postion will return actual position of seletion. '''

''' How to set up:
    menu = Menu()#necessary
    #menu.set_colors((255,255,255), (0,0,255), (0,0,0))#optional
    menu.set_fontsize(40)#optional
    #menu.set_font('data/couree.fon')#optional
    #menu.move_menu(0, 0)#optional, moves the list of choices BY (x,y)
    menu.init(['Level 1','Level 2','Quit'], surface)#necessary
    #menu.move_menu(0, 0)#optional, moves the choice list TO (x,y)
    menu.draw()#necessary
    
    pygame.key.set_repeat(199,69)#(delay,interval)
    pygame.display.update()
    while 1:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    menu.draw(-1) #here is the Menu class function
                if event.key == K_DOWN:
                    menu.draw(1) #here is the Menu class function
                if event.key == K_RETURN:
                    if menu.get_position() == 2:#here is the Menu class function
                        pygame.display.quit()
                        sys.exit()                        
                if event.key == K_ESCAPE:
                    pygame.display.quit()
                    sys.exit()
                pygame.display.update()
            elif event.type == QUIT:
                pygame.display.quit()
                sys.exit()
        pygame.time.wait(8)
        
'''
