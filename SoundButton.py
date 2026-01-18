import pygame

class SoundButton:
    """
    button that has an associated sound file
    """


    def __init__(self, top_left, size, bank, preset, text, colour):
        """
        make new button
        
        :param self: self
        :param top_left: (x, y) of top left corner
        :param bank: associated soundfont sound's bank number
        :param preset: associated soundfont sound's preset number
        :param text: text to display on the button
        :param colour: colour of the button
        """
        self.rect = pygame.Rect(top_left[0], top_left[1], size[0], size[1])
        self.bank = bank
        self.preset = preset
        self.colour = colour
        self.text, self.hovertext = self.make_text(text)


    def make_text(self, text):
        """
        makes a text object that will fit in the button

        :param size: (width, height) of button
        :param text: text to display
        """
        for smaller_size in range(20, 8 - 1, -1):
            font = pygame.font.Font("LibreFranklin-Regular.ttf", smaller_size)
            text_surface = font.render(text, True, self.colour)
            if (text_surface.get_width() <= self.rect.width 
                and text_surface.get_height() <= self.rect.height):
                return text_surface, (font.render(text, True, "white"))
            
        return text_surface, (font.render(text, True, "white"))
    

    def collides(self, position):
        """
        returns whether a point is within the button
        """
        return self.rect.collidepoint(position)