from nose.tools import *
import player, pygame
'''
	Tests the initialization of the player object
'''
def test_init():
	# Player requires an image, so loading the current player image
	# TODO: make this load any image so that it doesn't fail
	#       whenever we change the name of the image.
	p = player.Player((1,2),(3,4),pygame.image.load('img/princess.png'))

	assert_equal(p.x, 1)
	assert_equal(p.y, 2)
	assert_equal(p.width, 3)
	assert_equal(p.height, 4)
	assert_equal(p.onGround, False)
'''
	Tests that get_rect() returns a proper pygame.rect obect
'''
def test_get_rect():
	p = player.Player((1,2),(10,10),pygame.image.load('img/princess.png'))

	rect = p.get_rect()

	assert_equal(rect.w,10)
	assert_equal(rect.h,10)
	assert_equal(rect.left,1)
	assert_equal(rect.top,2)
	assert_equal(rect.centerx,6)
	assert_equal(rect.centery,7)
