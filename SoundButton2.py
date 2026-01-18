import pygame
import sys

class SoundButton:
    def __init__(self, top_left, size, sound, text, colour):
        self.rect = pygame.Rect(top_left[0], top_left[1], size[0], size[1])
        self.sound = sound
        self.base_color = pygame.Color(colour)
        self.text_str = text
        # Fallback to system font if yours isn't in the folder
        try:
            self.font = pygame.font.Font("LibreFranklin-Regular.ttf", 14)
        except:
            self.font = pygame.font.SysFont("Arial", 14, bold=True)
            
        self.text_surf = self.font.render(self.text_str, True, (255, 255, 255))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, screen, mouse_pos, current_sound):
        is_hovered = self.rect.collidepoint(mouse_pos)
        is_active = (self.sound == current_sound)

        # 1. Create a transparent surface for the button body
        btn_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # 2. Logic for colors
        if is_active:
            bg_color = (255, 255, 255, 180)  # Bright white/opaque
            text_color = (20, 20, 30)        # Dark text for contrast
            border_color = (255, 255, 255, 255)
        elif is_hovered:
            bg_color = (*self.base_color[:3], 200) # Brighter version
            text_color = (255, 255, 255)
            border_color = (255, 255, 255, 200)
        else:
            bg_color = (*self.base_color[:3], 80)  # Very transparent
            text_color = (200, 200, 200)
            border_color = (255, 255, 255, 80)

        # 3. Draw to the transparent surface
        pygame.draw.rect(btn_surf, bg_color, (0, 0, self.rect.width, self.rect.height), border_radius=10)
        pygame.draw.rect(btn_surf, border_color, (0, 0, self.rect.width, self.rect.height), width=2, border_radius=10)
        
        # 4. Blit button to screen, then text on top
        screen.blit(btn_surf, (self.rect.x, self.rect.y))
        
        # Re-render text color for active state
        final_text = self.font.render(self.text_str, True, text_color)
        screen.blit(final_text, self.text_rect)

    def collides(self, position):
        """
        returns whether a point is within the button
        """
        return self.rect.collidepoint(position)


def main():
    pygame.init()
    W, H = 1280, 720
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Instrument UI Test")
    clock = pygame.time.Clock()

    # Simulation Data
    current_selected_sound = (0, 0)
    mock_presets = ["Grand Piano", "Bright Piano", "E-Piano", "Harpsichord", "Clavinet", 
                    "Celesta", "Glockenspiel", "Music Box", "Vibraphone", "Marimba"]
    
    # Generate Buttons
    buttons = []
    cols, rows = 2, 5
    size = (180, 50)
    padding = (20, 15)
    start_x, start_y = W // 2 + 100, 100

    for c in range(cols):
        for r in range(rows):
            idx = c * rows + r
            pos = (start_x + (size[0] + padding[0]) * c,
                   start_y + (size[1] + padding[1]) * r)
            
            buttons.append(SoundButton(
                top_left=pos,
                size=size,
                sound=(c, r),
                text=mock_presets[idx],
                colour="steelblue3"
            ))

    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    if btn.rect.collidepoint(mouse_pos):
                        current_selected_sound = btn.sound
                        print(f"Switched to: {btn.text_str} {btn.sound}")

        # Draw Everything
        draw_gradient_background(screen, W, H)
        
        # UI Header Label
        header_font = pygame.font.SysFont("Arial", 24, bold=True)
        header_surf = header_font.render("INSTRUMENT SELECT", True, (255, 255, 255))
        screen.blit(header_surf, (start_x, start_y - 50))

        # Draw Buttons
        for btn in buttons:
            btn.draw(screen, mouse_pos, current_selected_sound)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()


